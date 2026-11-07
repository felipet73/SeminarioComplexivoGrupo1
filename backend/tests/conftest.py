import pytest
from app.services import metrics
from app.services import admin_store
from app import admin_auth
from app.config import Settings, get_settings
from app.services import rag
from app.services.llm import GeminiProvider, OpenAIProvider
import shutil

@pytest.fixture
def fuente_indexada():
    from app.services import rag
    doc = rag.save_document('norma.txt', 'Artículo 1. Titulación. Los requisitos de titulación se consultan según la carrera y el curso con Secretaría Académica.'.encode(),
                            dict(title='Normativa de prueba', kind='normativa', source_url='', valid_from='2020-01-01', valid_to=None, approved=True, enabled=True, notes=''), 'test')
    return rag.index_document(doc['id'], 'test')['chunks'][0]

@pytest.fixture(autouse=True)
def metricas_aisladas(tmp_path, monkeypatch):
    from app import main
    from app.rate_limit import LimiteConsultas
    monkeypatch.setattr(main, 'limite_chat', LimiteConsultas(30, 60))
    # Ni el .env privado ni las claves del equipo deben decidir el resultado.
    monkeypatch.setitem(Settings.model_config, 'env_file', None)
    for name in ('GEMINI_API_KEY', 'OPENAI_API_KEY', 'AI_API_KEY'):
        # También impide heredar claves del .env en los subprocesos del evaluador.
        monkeypatch.setenv(name, '')
    get_settings.cache_clear()
    monkeypatch.setenv('APP_REVISION', 'test-revision')

    def proveedor_real_prohibido(*args, **kwargs):
        raise AssertionError('Las pruebas deben simular los proveedores externos')

    monkeypatch.setattr(rag, '_embed_provider', proveedor_real_prohibido)
    monkeypatch.setattr(GeminiProvider, 'generar', proveedor_real_prohibido)
    monkeypatch.setattr(OpenAIProvider, 'generar', proveedor_real_prohibido)
    monkeypatch.setattr(metrics, 'LOG_PATH', tmp_path / 'metrics.jsonl')
    original=admin_store.PROMPT_DIR
    copied=tmp_path/'prompts'
    copied.mkdir()
    for path in original.glob('system_v[123].md'):
        shutil.copy2(path,copied/path.name)
    monkeypatch.setattr(admin_store,'DATA_DIR',tmp_path/'admin')
    monkeypatch.setattr(admin_store,'DEFAULTS',dict(admin_store.DEFAULTS, strategy='lexical'))
    monkeypatch.setattr(admin_store,'PROMPT_DIR',copied)
    admin_auth.SESSIONS.clear()
    admin_auth.FAILURES.clear()
    yield
    get_settings.cache_clear()
    admin_auth.SESSIONS.clear()
    admin_auth.FAILURES.clear()
