from fastapi import APIRouter, HTTPException
from app.agente import esquemas, MAX_ITER, REQUIEREN_OK
from app.tools import academicas
from app.tools.academicas import PlazoIn, PlazoOut, calcular_plazo, RequisitosIn, ChecklistIn, ConsultaOut, ChecklistOut
from app.services.actions import DecisionIn, DecisionOut
from app.flujo import resolver

router = APIRouter(prefix='/api/herramientas', tags=['Herramientas educativas'])
agente_router = APIRouter(prefix='/api/agente', tags=['Agente educativo'])


@router.get('')
def contratos():
    return {'permitidas': esquemas(), 'salidas': {'consulta': ConsultaOut.model_json_schema(), 'checklist': ChecklistOut.model_json_schema(), 'calculo': PlazoOut.model_json_schema(), 'decision': DecisionOut.model_json_schema()}, 'max_iteraciones': MAX_ITER, 'requieren_ok': sorted(REQUIEREN_OK)}


@router.post('/calcular-plazo', response_model=PlazoOut)
def simular_calendario(datos: PlazoIn):
    """Simula días hábiles declarados. No determina un plazo institucional ni incluye feriados."""
    return calcular_plazo(datos)


@router.post('/consultar-requisitos', response_model=ConsultaOut)
def consultar_requisitos(datos: RequisitosIn):
    return academicas.consultar_requisitos(datos)[0]


@router.post('/generar-checklist', response_model=ChecklistOut)
def generar_checklist(datos: ChecklistIn):
    return academicas.generar_checklist(datos)[0]


@agente_router.post('/confirmar/{action_id}', response_model=DecisionOut)
@router.post('/agente/confirmar/{action_id}', response_model=DecisionOut)
def confirmar(action_id: str, decision: DecisionIn):
    try:
        return resolver(action_id, decision)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except TimeoutError as error:
        raise HTTPException(410, str(error)) from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
