"""20 contratos sobre corpus real y modelo doble: NO mide calidad del LLM."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.flujo import orientar, resolver
from app.schemas import ConsultaChat
from app.services.actions import DecisionIn
from app.services.llm import ResultadoLLM
from app.services import admin_store as store


def modelo_guion(name):
    count = 0
    def generar(*args, **kwargs):
        nonlocal count
        count += 1
        evidence = kwargs['contexto']['evidencia']
        answer = {'estado': 'respuesta', 'respuesta': 'Orientación doble para verificar contrato y procedencia.',
                  'fragmentos': [evidence[0]['id']] if evidence else []}
        if name == 'no_llamar':
            raise AssertionError('Una consulta bloqueada no debe llamar al proveedor')
        if name == 'cita_inventada':
            answer['fragmentos'] = ['id-que-no-existe']
        if name == 'json_invalido':
            return ResultadoLLM('texto sin JSON', 'doble-flujo', False, 0)
        if name == 'abstencion':
            answer = {'estado': 'abstencion', 'respuesta': 'No hay respaldo para ese requisito.'}
        if name == 'herramienta_prohibida':
            answer = ({'herramienta': 'aprobar_tema', 'argumentos': {}} if count == 1 else
                      {'estado': 'rechazo', 'respuesta': 'La herramienta no está permitida.'})
        if name == 'bucle':
            answer = {'herramienta': 'buscar_fragmentos', 'argumentos': {'pregunta': 'matrícula'}}
        if name == 'checklist' and count == 1:
            answer = {'herramienta': 'generar_checklist', 'argumentos': {'perfil_estudiante': 'titulación'}}
        if name == 'solicitud':
            answer = {'herramienta': 'registrar_solicitud_tutor', 'argumentos': {'carrera': 'Software', 'modalidad': 'Proyecto', 'tema': 'RAG educativo'}}
        return ResultadoLLM(json.dumps(answer), 'doble-flujo', False, 0)
    return SimpleNamespace(generar_texto=generar)


def evaluar():
    cases = [json.loads(line) for line in (ROOT / 'eval/casos_flujo.jsonl').read_text(encoding='utf-8').splitlines() if line]
    results = []
    for case in cases:
        result = orientar(ConsultaChat(**case['consulta']), modelo_guion(case['guion']))
        ok = result.estado == case['estado']
        if result.estado == 'respuesta':
            ok = ok and bool(result.fuentes)
        row = {'id': case['id'], 'esperado': case['estado'], 'obtenido': result.estado, 'ok': bool(ok)}
        if 'decision_humana' in case and result.accion_pendiente:
            pending = result.accion_pendiente
            decision = resolver(pending.id, DecisionIn(token=pending.token, aprobar=case['decision_humana']))
            row['decision'] = decision.estado
            row['ok'] = row['ok'] and decision.estado == case['resultado_decision']
        results.append(row)
    return {'modo': 'contratos_con_modelo_doble_y_corpus_real', 'casos': results,
            'correctos': sum(r['ok'] for r in results), 'total': len(results),
            'limite': 'Los guiones simulan decisiones del modelo. No representan exactitud generativa ni resultados reales de estudiantes.'}


if __name__ == '__main__':
    store.DATA_DIR = ROOT / 'data/eval-state'
    report = evaluar()
    (ROOT / 'eval/results-flujo.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Contratos del flujo: {report['correctos']}/{report['total']} (modelo doble, corpus real)")
    sys.exit(0 if report['correctos'] == report['total'] else 1)
