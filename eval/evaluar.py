"""Evalúa recuperación real. --chat añade generación real y acierto de citas, no exactitud semántica."""
import argparse
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


def evaluar(cases, chat=False, version=None):
    results = []
    llm = ClienteLLM(get_settings()) if chat else None
    from app.prompts import cargar_prompt
    expected = json.loads((ROOT / 'eval/respuestas_esperadas.json').read_text(encoding='utf-8'))
    proveedor_fallo = False
    for case in cases:
        found = rag.retrieve(case['pregunta'])['chunks']
        match = lambda c: c['title'] == case['documento'] and c['section'] == case['seccion']
        row = dict(case, respuesta_esperada=expected[case['id']], recuperados=[{'documento': c['title'], 'seccion': c['section']} for c in found],
                   acierto=any(match(c) for c in found) if case['documento'] else not found)
        if chat:
            try:
                if proveedor_fallo and found:
                    raise RuntimeError('No evaluado: el proveedor falló en un caso anterior')
                response, _ = generar_respuesta(ConsultaChat(pregunta=case['pregunta']), llm,
                                                evidencia=found, system_prompt=cargar_prompt(version))
                row['respuesta'] = response.model_dump()
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
              'limite': 'Acierto de artículo no acredita que todas las afirmaciones estén respaldadas. Revisión humana pendiente.'}
    if chat:
        report['acierto_cita'] = sum(r['cita_correcta'] for r in positive) / len(positive)
        report['abstencion_o_rechazo'] = sum(r['cita_correcta'] for r in negative) / len(negative)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data/eval-state')
    parser.add_argument('--chat', action='store_true', help='Consume el proveedor configurado y sus cuotas')
    parser.add_argument('--prompt', choices=['system_v1', 'system_v2', 'system_v3'])
    parser.add_argument('--output', type=Path, default=ROOT / 'eval/results.json')
    args = parser.parse_args()
    store.DATA_DIR = args.data_dir.resolve()
    cases = [json.loads(line) for line in (ROOT / 'eval/preguntas.jsonl').read_text(encoding='utf-8').splitlines() if line]
    report = evaluar(cases, args.chat, args.prompt)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('casos', 'config')}, ensure_ascii=False))
    ok = report['acierto_top_k'] >= .7 and report['silencio'] >= .9
    if args.chat:
        ok = ok and report['acierto_cita'] >= .8 and report['abstencion_o_rechazo'] == 1
    sys.exit(0 if ok else 1)
