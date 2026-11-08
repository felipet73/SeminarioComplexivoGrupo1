import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('detector_secretos', ROOT / 'scripts/check_secrets.py')
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)


def test_detecta_constantes_de_baja_entropia_sin_imprimir_valor():
    code = 'SECRET_KEY = (\n "valor-ficticio-prueba"\n)\nADMIN_PASSWORD_HASH = pwd_context.hash("password-ficticio")'
    result = detector.revisar_texto('backend/app/inseguro.py', code)
    assert result == ['backend/app/inseguro.py:1', 'backend/app/inseguro.py:4']
    assert 'valor-ficticio' not in str(result) and 'password-ficticio' not in str(result)


def test_permite_secretos_vacios_y_lectura_desde_entorno():
    code = 'admin_password: str = ""\nSECRET_KEY = os.environ["JWT_SECRET"]'
    assert detector.revisar_texto('backend/app/config.py', code) == []
    assert detector.revisar_texto('backend/tests/config.py', 'SECRET_KEY = "solo-doble-de-prueba"') == []


def test_detecta_dsn_postgres_con_password_sin_imprimirlo():
    value = 'postgresql://' + 'usuario:valor-ficticio@localhost/base'
    result = detector.revisar_texto('config.txt', value)
    assert result == ['config.txt:1']
    assert 'valor-ficticio' not in str(result)
    assert detector.revisar_texto('config.txt', 'RAG_DATABASE_URL=') == []
