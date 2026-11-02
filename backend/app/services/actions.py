"""Confirmación por capacidad secreta, TTL, idempotencia y auditoría del registro demo local."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ConfigDict, Field
from app.services import admin_store as store


class SolicitudTutorIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    carrera: str = Field(min_length=3, max_length=120)
    modalidad: str = Field(min_length=3, max_length=120)
    tema: str = Field(min_length=3, max_length=300)


class AccionPendiente(BaseModel):
    id: str
    token: str
    herramienta: str
    argumentos: SolicitudTutorIn
    vence: str
    alcance: str = 'Borrador académico de demostración: se guarda localmente tras confirmar; no se envía a la universidad ni asigna tutor.'


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str = Field(min_length=32, max_length=100)
    aprobar: bool = Field(strict=True)


class DecisionOut(BaseModel):
    id: str
    estado: str
    mensaje: str


def preparar(datos: SolicitudTutorIn, *, ttl_minutes=30) -> AccionPendiente:
    token = secrets.token_urlsafe(32)
    pending = AccionPendiente(id=store.new_id(), token=token, herramienta='registrar_solicitud_tutor',
                             argumentos=datos, vence=(datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat())
    record = pending.model_dump(mode='json', exclude={'token'}) | {
        'token_hash': hashlib.sha256(token.encode()).hexdigest(), 'estado': 'pendiente'}
    with store.db() as conn:
        store.put(conn, 'action', pending.id, record)
        store.audit(conn, 'agente', 'proponer_solicitud_demo', pending.id, None, record)
    return pending


def decidir(action_id: str, decision: DecisionIn) -> DecisionOut:
    # Mismo bloqueo/transacción que el resto del estado: confirmar dos veces no duplica registros.
    with store.db() as conn:
        record = store.get(conn, 'action', action_id)
        digest = hashlib.sha256(decision.token.encode()).hexdigest()
        if not record or not secrets.compare_digest(record['token_hash'], digest):
            raise LookupError('Acción no encontrada o capacidad inválida')
        if record['estado'] != 'pendiente':
            if (record['estado'] == 'registrada_localmente') != decision.aprobar:
                raise ValueError('La acción ya tiene una decisión diferente')
            return DecisionOut(id=action_id, estado=record['estado'], mensaje='Esta decisión ya fue procesada; no se duplicó el registro.')
        if datetime.fromisoformat(record['vence']) <= datetime.now(timezone.utc):
            raise TimeoutError('La propuesta expiró. Vuelve a preparar el borrador.')
        before = dict(record)
        record['estado'] = 'registrada_localmente' if decision.aprobar else 'cancelada'
        record['decidida_en'] = store.now()
        # Identifica la capacidad que decidió; no afirma identidad institucional autenticada.
        record['actor'] = 'usuario_demo:' + digest[:12]
        if decision.aprobar:
            store.put(conn, 'solicitud_demo', action_id, {'id': action_id, 'datos': record['argumentos'],
                                                        'fecha': record['decidida_en'], 'actor': record['actor']})
        store.put(conn, 'action', action_id, record)
        store.audit(conn, record['actor'], 'confirmar_solicitud_demo' if decision.aprobar else 'cancelar_solicitud_demo', action_id, before, record)
        return DecisionOut(id=action_id, estado=record['estado'], mensaje=(
            'Borrador guardado localmente. No se envió a la universidad ni se asignó tutor.' if decision.aprobar else
            'Propuesta cancelada. No se registró la solicitud.'))
