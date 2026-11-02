"""Busca patrones reconocibles sin imprimir valores secretos."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [re.compile(r'AIza[0-9A-Za-z_-]{35}'), re.compile(r'sk-(?:proj-)?[A-Za-z0-9_-]{24,}'),
            re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]


def revisar():
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    findings = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file() or path.suffix.lower() not in ('.py', '.ts', '.tsx', '.md', '.json', '.yaml', '.yml', '.toml', '.example', '.txt'):
            continue
        for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f'{relative}:{number}')
    return findings


if __name__ == '__main__':
    findings = revisar()
    print('\n'.join(findings) if findings else 'Sin patrones de secretos en archivos versionables. No se inspecciona ni imprime .env.')
    raise SystemExit(1 if findings else 0)
