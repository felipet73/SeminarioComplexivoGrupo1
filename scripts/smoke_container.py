"""Prueba HTTP de la imagen: sin credenciales ni consumo de modelos."""
import argparse
import json
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def comprobar(url):
    def get(path):
        with urlopen(url.rstrip('/')+path, timeout=5) as response:
            return json.load(response)
    for intento in range(20):
        try:
            assert get('/health')['status'] == 'ok'
            break
        except (URLError, TimeoutError, ConnectionError):
            if intento == 19:
                raise
            time.sleep(1)
    ready = get('/ready')
    assert ready['fragmentos_elegibles'] > 0
    tools = get('/api/herramientas')
    assert 'generar_checklist' in tools['permitidas']
    assert tools['max_iteraciones'] > 0
    req = Request(url.rstrip('/')+'/api/herramientas/calcular-plazo',
                  data=json.dumps({'fecha_inicio':'2026-10-30','dias_habiles':1}).encode(),
                  headers={'Content-Type':'application/json'})
    with urlopen(req, timeout=5) as response:
        assert json.load(response)['fecha_resultado'] == '2026-11-02'
    try:
        get('/admin/recargar-reglamentos')
    except HTTPError as error:
        assert error.code == 404
    else:
        raise AssertionError('No debe existir la ruta administrativa retirada')
    print(json.dumps({'health':'ok', 'ready':ready, 'herramientas':'ok', 'calendario':'ok'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    comprobar(parser.parse_args().url)
