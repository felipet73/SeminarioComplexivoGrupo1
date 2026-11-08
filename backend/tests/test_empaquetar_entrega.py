"""La entrega excluye secretos aun versionados y no deja un ZIP sobredimensionado."""
import importlib.util
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('empaquetar_entrega', ROOT/'scripts/empaquetar_entrega.py')
paquete = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paquete)


def test_excluye_archivos_privados_aunque_esten_versionados_y_zip_es_reproducible(tmp_path):
    repo = tmp_path/'proyecto'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    for name in ['README.md', '.env', '.env.example', 'privada.key', 'estado.sqlite3', 'node_modules/modulo.js', 'infra/.terraform/provider.bin',
                 'infra/terraform.tfstate', 'infra/terraform.tfstate.backup', 'infra/cambio.tfplan',
                 'infra/terraform.tfvars', 'infra/secrets.tfvars.json', 'infra/terraform.tfvars.example']:
        p = repo/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('contenido ficticio')
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    'commit', '-qm', 'fixture'], check=True)
    a, b = tmp_path/'a.zip', tmp_path/'b.zip'
    report = paquete.empaquetar(repo, a)
    paquete.empaquetar(repo, b)
    assert report['zip_creado'] and a.read_bytes() == b.read_bytes()
    with zipfile.ZipFile(a) as z:
        assert set(z.namelist()) == {'proyecto/README.md', 'proyecto/.env.example', 'proyecto/infra/terraform.tfvars.example'}
    large = tmp_path/'no-entregar.zip'
    report = paquete.empaquetar(repo, large, max_bytes=1)
    assert not report['cumple_limite'] and not report['zip_creado'] and not large.exists()
    assert not list(tmp_path.glob('tmp*.zip'))
