import pytest
from app.services import metrics
from app.services import admin_store
from app import admin_auth
import shutil

@pytest.fixture(autouse=True)
def metricas_aisladas(tmp_path, monkeypatch):
    monkeypatch.setattr(metrics, 'LOG_PATH', tmp_path / 'metrics.jsonl')
    original=admin_store.PROMPT_DIR
    copied=tmp_path/'prompts'
    copied.mkdir()
    for path in original.glob('system_v[123].md'):
        shutil.copy2(path,copied/path.name)
    monkeypatch.setattr(admin_store,'DATA_DIR',tmp_path/'admin')
    monkeypatch.setattr(admin_store,'PROMPT_DIR',copied)
    admin_auth.SESSIONS.clear()
    admin_auth.FAILURES.clear()
