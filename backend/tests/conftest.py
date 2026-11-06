import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
from app.services import metrics
from app.services import admin_store
from app import admin_auth
import shutil

# Carga automática del archivo .env ubicado en la raíz del proyecto (un nivel arriba de backend/)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

@pytest.fixture
def fuente_indexada():
    from app.services import rag
    doc = rag.save_document('norma.txt', 'Artículo 1. Titulación. Los requisitos de titulación se consultan según la carrera y el curso con Secretaría Académica.'.encode(),
                            dict(title='Normativa de prueba', kind='normativa', source_url='', valid_from='2020-01-01', valid_to=None, approved=True, enabled=True, notes=''), 'test')
    return rag.index_document(doc['id'], 'test')['chunks'][0]

@pytest.fixture(autouse=True)
def metricas_aisladas(tmp_path, monkeypatch):
    monkeypatch.setattr(metrics, 'LOG_PATH', tmp_path / 'metrics.jsonl')
    original=admin_store.PROMPT_DIR
    copied=tmp_path/'prompts'
    copied.mkdir()
    for path in original.glob('system_v[123].md'):
        shutil.copy2(path,copied/path.name)
    monkeypatch.setattr(admin_store,'DATA_DIR',tmp_path/'admin')
    
    # LÍNEA ELIMINADA/COMENTADA: Evitamos forzar 'lexical' globalmente 
    # porque interfiere con los tests que esperan la estrategia por defecto.
    # monkeypatch.setattr(admin_store,'DEFAULTS',dict(admin_store.DEFAULTS, strategy='lexical'))
    
    monkeypatch.setattr(admin_store,'PROMPT_DIR',copied)
    admin_auth.SESSIONS.clear()
    admin_auth.FAILURES.clear()