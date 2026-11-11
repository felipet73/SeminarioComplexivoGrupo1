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


def repo_con_evidencia(tmp_path):
    import json
    repo = tmp_path/'repo'
    repo.mkdir()
    subprocess.run(['git','init','-q',str(repo)],check=True)
    (repo/'eval').mkdir()
    (repo/'README.md').write_text('Proyecto de prueba')
    (repo/'eval/casos_http.json').write_text(json.dumps([{'id':str(i)} for i in range(35)]))
    subprocess.run(['git','add','.'],cwd=repo,check=True)
    subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],cwd=repo,check=True)
    sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    data = {'revision_esperada':sha,'correctos':35,'total':35,'omitidos':[],
            'incluye_modelo':True,'solo_backend':False,
            'casos':[{'id':str(i),'ok':True,'revision_obtenida':sha if i == 0 else None} for i in range(35)]}
    return repo,sha,data


def test_paquete_incorpora_reporte_completo_del_mismo_sha_sin_nuevo_commit(tmp_path):
    import hashlib
    import json
    repo,sha,data = repo_con_evidencia(tmp_path)
    source = tmp_path/'reporte.json'
    source.write_text(json.dumps(data))
    output = tmp_path/'entrega.zip'
    report = paquete.empaquetar(repo,output,production_report=source,expected_revision=sha)
    assert report['evidencia_produccion']['revision'] == sha
    assert report['zip_sha256'] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert not report['working_tree_con_cambios']
    with zipfile.ZipFile(output) as archive:
        assert json.loads(archive.read('repo/'+report['evidencia_produccion']['archivo'])) == data


import pytest


@pytest.mark.parametrize('error',['resumen','fallo','omitidos','ids','revision'])
def test_no_crea_entrega_con_evidencia_incompleta_o_de_otro_sha(tmp_path,error):
    import json
    repo,sha,data = repo_con_evidencia(tmp_path)
    if error == 'resumen':
        del data['casos']
    elif error == 'fallo':
        data['casos'][0]['ok'] = False
    elif error == 'omitidos':
        data['omitidos'] = ['caso']
    elif error == 'ids':
        data['casos'][0]['id'] = data['casos'][1]['id']
    else:
        data['revision_esperada'] = 'otro-sha'
    source = tmp_path/'reporte.json'
    source.write_text(json.dumps(data))
    output = tmp_path/'entrega.zip'
    with pytest.raises(ValueError):
        paquete.empaquetar(repo,output,production_report=source,expected_revision=sha)
    assert not output.exists()


def test_no_etiqueta_como_commit_probado_un_arbol_con_cambios(tmp_path):
    import json
    repo,sha,data = repo_con_evidencia(tmp_path)
    (repo/'README.md').write_text('Cambio posterior no probado')
    source = tmp_path/'reporte.json'
    source.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='sin cambios'):
        paquete.empaquetar(repo,tmp_path/'entrega.zip',production_report=source,expected_revision=sha)
