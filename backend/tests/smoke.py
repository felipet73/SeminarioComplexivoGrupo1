"""Entrada compatible: python backend/tests/smoke.py URL_BACKEND [opciones]."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.pruebas_funcionales import main
if __name__ == '__main__':
    if len(sys.argv)>1 and not sys.argv[1].startswith('-'):
        sys.argv[1:2] = ['--backend', sys.argv[1]]
    raise SystemExit(main())
