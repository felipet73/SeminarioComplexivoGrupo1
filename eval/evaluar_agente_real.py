"""Seis consultas reales sin guion ni fallback; exige seis checklists citados.

Una abstención segura queda registrada y falla el objetivo de disponibilidad del
checklist; no se confunde con una respuesta inventada ni se reemplaza por otra.
"""
import argparse
import os
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.config import get_settings
from app.parametros import PARAMETROS
from app.prompts import cargar_prompt
from app.schemas import ConsultaChat
from app.services import admin_store as store
from app.services.chat_flow import generar_respuesta
from app.services.llm import ClienteLLM, ProveedorNoDisponible


CASOS = [
    {'id':'a1','pregunta':'Genera un checklist con los requisitos de integración curricular para un estudiante de grado.', 'curso':'grado'},
    {'id':'a2','pregunta':'Necesito una lista de verificación de titulación de posgrado; usa generar_checklist para organizar los requisitos.', 'curso':'posgrado'},
    {'id':'a3','pregunta':'Genera un checklist de requisitos de titulación para grado con examen complexivo.', 'curso':'grado','modalidad_titulacion':'examen complexivo'},
    {'id':'a4','pregunta':'Organiza un checklist para titularme mediante proyecto de investigación en grado.', 'curso':'grado','modalidad_titulacion':'proyecto de investigación'},
    {'id':'a5','pregunta':'Genera un checklist de requisitos de titulación de maestría; distingue lo que falta verificar.', 'curso':'maestría'},
    {'id':'a6','pregunta':'Necesito una lista de verificación de requisitos de titulación de tercer nivel, basada en los artículos recuperados.', 'curso':'tercer nivel'},
]


def diagnostico_proveedor(error):
    """Solo categorías conocidas y estado HTTP; nunca texto del SDK o credenciales."""
    vistos = set()
    actual = error
    while actual is not None and id(actual) not in vistos:
        vistos.add(id(actual))
        if isinstance(actual, ProveedorNoDisponible):
            categorias = {'autenticacion', 'cuota_o_limite', 'modelo_no_disponible',
                          'timeout', 'proveedor', 'salida_o_conexion',
                          'sin_configuracion', 'no_disponible'}
            categoria = actual.category if actual.category in categorias else 'no_disponible'
            status = actual.status
            status = status if type(status) is int and 100 <= status <= 599 else None
            return {'categoria_proveedor': categoria, 'status_proveedor': status}
        actual = actual.__cause__ or actual.__context__
    return {}


def evaluar(modelo='gemini'):
    settings = get_settings()
    if not (settings.gemini_api_key if modelo == 'gemini' else settings.openai_api_key):
        raise ValueError(f'Falta credencial del proveedor {modelo}')
    rows = []
    llm = ClienteLLM(settings, min_interval_seconds=float(os.environ.get('EVAL_LLM_MIN_INTERVAL_SECONDS', '0')))
    for caso in CASOS:
        row = dict(caso)
        try:
            response, raw = generar_respuesta(ConsultaChat(**{k:v for k,v in caso.items() if k != 'id'}, modelo_preferido=modelo),
                                              llm, permitir_fallback=False, permitir_escrituras=False)
            payload = response.model_dump(mode='json', exclude={'accion_pendiente'})
            row.update(respuesta=payload, salida_final_modelo=raw.texto if raw else None,
                       tokens_total=raw.tokens_total if raw else None)
            trace = response.traza_agente
            requested = any(e['evento']=='herramienta_solicitada' and e['herramienta']=='generar_checklist' for e in trace)
            executed = any(e['evento']=='herramienta_completada' and e['herramienta']=='generar_checklist' for e in trace)
            turns = sum(e['evento']=='modelo' for e in trace)
            row['cumple'] = bool(requested and executed and 2 <= turns <= PARAMETROS['max_iteraciones']
                                 and response.estado=='respuesta' and response.fuentes and response.checklist
                                 and response.checklist.items and not response.fallback_activado)
            row['herramienta_elegida_y_ejecutada'] = bool(requested and executed and 2 <= turns <= PARAMETROS['max_iteraciones'] and not response.fallback_activado)
        except Exception as error:
            row.update(cumple=False, error=getattr(error, 'detail', type(error).__name__))
            row.update(diagnostico_proveedor(error))
        rows.append(row)
        print(caso['id'], 'cumple' if row['cumple'] else 'no cumple',
              row.get('categoria_proveedor', ''), row.get('status_proveedor', ''), flush=True)
    return {'fecha':store.now(), 'modo':'agente_modelo_real_sin_fallback', 'proveedor':modelo,
            'modelo':settings.ai_model if modelo=='gemini' else settings.fallback_model,
            'prompt_sha256':hashlib.sha256(cargar_prompt().encode()).hexdigest(),
            'config':store.settings(), 'casos':rows, 'aciertos':sum(r['cumple'] for r in rows),
            'total':len(rows), 'limite':'Verifica elección y ejecución real, citas y lista no vacía. No mide exhaustividad ni respaldo semántico de cada frase.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT/'data/eval-hybrid')
    parser.add_argument('--modelo', choices=['gemini','openai'], default='gemini')
    parser.add_argument('--output', type=Path, default=ROOT/'eval/results-agente-real.json')
    args = parser.parse_args()
    store.DATA_DIR = args.data_dir.resolve()
    try:
        report = evaluar(args.modelo)
    except ValueError as error:
        parser.exit(2, str(error)+'\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    sys.exit(0 if report['aciertos'] == report['total'] else 1)
