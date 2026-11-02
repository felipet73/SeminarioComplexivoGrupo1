from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ConsultaChat
from app.services import actions, admin_store as store, rag
from app.services.chat_flow import generar_respuesta
from tests.test_agente import guion

DATOS = {'carrera': 'Software', 'modalidad': 'Proyecto', 'tema': 'RAG educativo'}


def test_propuesta_no_escribe_solicitud_y_confirmar_es_idempotente(fuente_indexada):
    llm = guion({'herramienta': 'registrar_solicitud_tutor', 'argumentos': DATOS})
    result, _ = generar_respuesta(ConsultaChat(pregunta='Prepara solicitud de tutor para Software, modalidad Proyecto, tema RAG educativo'), llm,
                               evidencia=rag.retrieve('titulación')['chunks'])
    assert result.estado == 'confirmacion'
    pending = result.accion_pendiente
    with store.db() as conn:
        assert store.all_records(conn, 'solicitud_demo') == []
    client = TestClient(app)
    url = '/api/herramientas/agente/confirmar/' + pending.id
    assert client.post(url, json={'token': 'incorrecto' * 5, 'aprobar': True}).status_code == 404
    for endpoint in (url, '/api/agente/confirmar/' + pending.id):
        response = client.post(endpoint, json={'token': pending.token, 'aprobar': True})
        assert response.status_code == 200 and response.json()['estado'] == 'registrada_localmente'
    assert client.post(url, json={'token': pending.token, 'aprobar': False}).status_code == 409
    with store.db() as conn:
        assert len(store.all_records(conn, 'solicitud_demo')) == 1
        audits = [dict(row) for row in conn.execute("SELECT * FROM audit WHERE action='confirmar_solicitud_demo'")]
        assert len(audits) == 1 and audits[0]['actor'].startswith('usuario_demo:')
        assert pending.token not in str(audits)


def test_cancelacion_y_expiracion_no_registran_solicitudes():
    client = TestClient(app)
    pending = actions.preparar(actions.SolicitudTutorIn(**DATOS))
    url = '/api/herramientas/agente/confirmar/' + pending.id
    assert client.post(url, json={'token': pending.token, 'aprobar': False}).json()['estado'] == 'cancelada'
    expired = actions.preparar(actions.SolicitudTutorIn(**DATOS), ttl_minutes=-1)
    assert client.post('/api/herramientas/agente/confirmar/' + expired.id,
                       json={'token': expired.token, 'aprobar': True}).status_code == 410
    with store.db() as conn:
        assert store.all_records(conn, 'solicitud_demo') == []


def test_esquemas_y_validacion_http():
    client = TestClient(app)
    schemas = client.get('/api/herramientas').json()
    assert 'registrar_solicitud_tutor' in schemas['requieren_ok']
    assert schemas['permitidas']['calcular_plazo']['additionalProperties'] is False
    assert client.post('/api/herramientas/calcular-plazo', json={'fecha_inicio': '2026-10-30', 'dias_habiles': -1}).status_code == 422
    assert client.post('/api/herramientas/calcular-plazo', json={'fecha_inicio': '2026-10-30', 'dias_habiles': 1}).json()['fecha_resultado'] == '2026-11-02'


def test_laboratorio_no_crea_propuestas_ni_persiste_capacidades(fuente_indexada):
    llm = guion({'herramienta': 'registrar_solicitud_tutor', 'argumentos': DATOS},
                {'estado': 'rechazo', 'respuesta': 'La simulación no prepara acciones.'})
    result, _ = generar_respuesta(ConsultaChat(pregunta='Prepara solicitud de tutor para Software, modalidad Proyecto, tema RAG educativo'), llm,
                               evidencia=rag.retrieve('titulación')['chunks'], permitir_escrituras=False)
    assert result.estado == 'rechazo' and result.accion_pendiente is None
    with store.db() as conn:
        assert store.all_records(conn, 'action') == []
