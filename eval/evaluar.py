"""Evalúa recuperación real. --chat añade generación real y acierto de citas, no exactitud semántica."""
import argparse
import os
import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services import admin_store as store, rag
from app.services.chat_flow import generar_respuesta
from app.schemas import ConsultaChat
from app.services.llm import ClienteLLM
from app.config import get_settings
from app.parametros import PARAMETROS


def evaluar(cases, chat=False, version=None, llm=None):
    if not cases or not any(c.get('documento') for c in cases) or not any(not c.get('documento') for c in cases):
        raise ValueError('La muestra debe contener preguntas con fuente y sin fuente')
    results = []
    llm = (llm or ClienteLLM(get_settings(), min_interval_seconds=float(os.environ.get('EVAL_LLM_MIN_INTERVAL_SECONDS', '0')))) if chat else None
    from app.prompts import cargar_prompt
    expected = json.loads((ROOT / 'eval/respuestas_esperadas.json').read_text(encoding='utf-8'))
    proveedor_fallo = False
    for case in cases:
        retrieval_error = None
        try:
            found = rag.retrieve(case['pregunta'])['chunks']
        except Exception as error:
            found = []
            retrieval_error = f'Recuperación fallida: {type(error).__name__}'
        match = lambda c: c['title'] == case['documento'] and c['section'] == case['seccion']
        row = dict(case, respuesta_esperada=case.get('respuesta_esperada', expected.get(case['id'], '')),
                   recuperados=[{'documento': c['title'], 'seccion': c['section'], 'fragmento_id': c['id'], 'pagina': c['page'], 'sha256': c['sha256']} for c in found],
                   acierto=(any(match(c) for c in found) if case['documento'] else not found) and retrieval_error is None)
        if retrieval_error:
            row['error'] = retrieval_error
        if chat:
            try:
                if retrieval_error:
                    raise RuntimeError(retrieval_error)
                if proveedor_fallo and found:
                    raise RuntimeError('No evaluado: el proveedor falló en un caso anterior')
                response, _ = generar_respuesta(ConsultaChat(pregunta=case['pregunta']), llm,
                                                evidencia=found, system_prompt=cargar_prompt(version), permitir_escrituras=False)
                row['respuesta'] = response.model_dump(exclude={'accion_pendiente'})
                row['cita_correcta'] = (response.estado == 'respuesta' and any(
                    f.titulo == case['documento'] and f.seccion == case['seccion'] for f in response.fuentes)
                    if case['documento'] else response.estado in ('abstencion', 'rechazo') and not response.fuentes)
            except Exception as error:
                proveedor_fallo = True
                row.update(error=getattr(error, 'detail', str(error)), cita_correcta=False)
        results.append(row)
    positive = [r for r in results if r['documento']]
    negative = [r for r in results if not r['documento']]
    hit = sum(r['acierto'] for r in positive) / len(positive)
    silence = sum(r['acierto'] for r in negative) / len(negative)
    report = {'modo': 'chat_real' if chat else 'recuperacion_sin_llm', 'config': store.settings(), 'fecha': store.now(),
              'prompt_version': version or 'activo',
              'prompt_sha256': hashlib.sha256(cargar_prompt(version).encode()).hexdigest() if chat else None,
              'positivos': len(positive), 'negativos': len(negative), 'acierto_top_k': hit,
              'silencio': silence, 'casos': results,
              'errores': sum('error' in r for r in results), 'criterios': PARAMETROS['evaluacion'],
              'limite': 'Acierto de artículo no acredita que todas las afirmaciones estén respaldadas. Revisión humana pendiente.'}
    if chat:
        report['acierto_cita'] = sum(r['cita_correcta'] for r in positive) / len(positive)
        report['abstencion_o_rechazo'] = sum(r['cita_correcta'] for r in negative) / len(negative)
    return report


def cumple_umbrales(report):
    thresholds = PARAMETROS['evaluacion']
    ok = (not report.get('errores', 0) and report['positivos'] > 0 and report['negativos'] > 0
          and report['acierto_top_k'] >= thresholds['acierto_top_k']
          and report['silencio'] >= thresholds['silencio'])
    if report['modo'] == 'chat_real':
        ok = ok and report['acierto_cita'] >= thresholds['acierto_cita'] and report['abstencion_o_rechazo'] >= thresholds['abstencion_o_rechazo']
    return bool(ok)


def leer_casos(path):
    cases = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    thresholds = PARAMETROS['evaluacion']
    if len(cases) < thresholds['min_casos'] or sum(not c.get('documento') for c in cases) < thresholds['min_negativos']:
        raise ValueError('La evaluación exige al menos 20 casos y cuatro negativos según config/parametros.yaml')
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('Hay IDs duplicados en el conjunto de evaluación')
    for case in cases:
        if not case.get('pregunta') or bool(case.get('documento')) != bool(case.get('seccion')):
            raise ValueError('Cada caso necesita pregunta y documento/sección coherentes')
    return cases


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data/eval-state')
    parser.add_argument('--chat', action='store_true', help='Consume el proveedor configurado y sus cuotas')
    parser.add_argument('--prompt', choices=['system_v1', 'system_v2', 'system_v3'])
    parser.add_argument('--output', type=Path, default=ROOT / 'eval/results.json')
    parser.add_argument('--cases', type=Path, default=ROOT / 'eval/preguntas.jsonl')
    args = parser.parse_args()
    store.DATA_DIR = args.data_dir.resolve()
    try:
        cases = leer_casos(args.cases)
        report = evaluar(cases, args.chat, args.prompt)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'Evaluación no ejecutada: {error}\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('casos', 'config')}, ensure_ascii=False))
    ok = cumple_umbrales(report)
    sys.exit(0 if ok else 1)
