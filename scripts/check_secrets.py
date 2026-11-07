"""Busca patrones reconocibles sin imprimir valores secretos."""
import re
import ast
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [re.compile(r'AIza[0-9A-Za-z_-]{35}'), re.compile(r'sk-(?:proj-)?[A-Za-z0-9_-]{24,}'),
            re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]


def revisar_texto(relative, content):
    numbers = {number for number, line in enumerate(content.splitlines(), 1)
               if any(pattern.search(line) for pattern in PATTERNS)}
    if relative.startswith('backend/app/') and relative.endswith('.py'):
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id.lower() for target in targets if isinstance(target, ast.Name)]
            value = node.value
            sensitive = {'secret_key','jwt_secret','admin_password','api_key','gemini_api_key','openai_api_key'}
            if sensitive.intersection(names) and isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value:
                numbers.add(node.lineno)
            if ('admin_password_hash' in names and isinstance(value, ast.Call) and value.args
                    and isinstance(value.args[0], ast.Constant) and isinstance(value.args[0].value, str)
                    and value.args[0].value):
                numbers.add(node.lineno)
    return [f'{relative}:{number}' for number in sorted(numbers)]


def revisar_historial_legacy():
    """Auditoría explícita del módulo retirado; nunca imprime sus valores."""
    relative = 'backend/app/seguridad.py'
    commits = subprocess.check_output(['git','log','--all','--format=%H','--',relative], cwd=ROOT, text=True).splitlines()
    findings = []
    for commit in commits:
        result = subprocess.run(['git','show',f'{commit}:{relative}'], cwd=ROOT, capture_output=True)
        if result.returncode == 0:
            findings.extend(f'{commit}:{finding}' for finding in revisar_texto(relative, result.stdout.decode('utf-8')))
    return findings


def revisar():
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    findings = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file() or path.suffix.lower() not in ('.py', '.ts', '.tsx', '.md', '.json', '.yaml', '.yml', '.toml', '.example', '.txt'):
            continue
        findings.extend(revisar_texto(relative, path.read_text(encoding='utf-8', errors='replace')))
    return findings


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historial-legacy', action='store_true', help='Audita el módulo retirado en todas las referencias; exit 1 si persiste')
    args = parser.parse_args()
    findings = revisar_historial_legacy() if args.historial_legacy else revisar()
    print('\n'.join(findings) if findings else 'Sin hallazgos en el alcance revisado. No se inspecciona ni imprime .env.')
    raise SystemExit(1 if findings else 0)
