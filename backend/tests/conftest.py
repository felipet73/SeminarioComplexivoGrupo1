import pytest
from app.services import metrics

@pytest.fixture(autouse=True)
def metricas_aisladas(tmp_path, monkeypatch):
    monkeypatch.setattr(metrics, 'LOG_PATH', tmp_path / 'metrics.jsonl')
