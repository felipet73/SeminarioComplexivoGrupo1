"""Sesiones opacas locales; contraseña únicamente en configuración del servidor."""
import hashlib
import hmac
import secrets
import time
from threading import Lock
from urllib.parse import urlsplit
from fastapi import HTTPException, Request
from app.config import get_settings

COOKIE = 'uniandes_admin'
SESSIONS = {}
FAILURES = {}
LOCK = Lock()

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def mutation_guard(request: Request):
    if request.method in ('POST','PUT','PATCH','DELETE'):
        origin = request.headers.get('origin')
        if request.headers.get('x-admin-request') != '1' or (origin and urlsplit(origin).netloc != request.headers.get('host')):
            raise HTTPException(403, 'Solicitud administrativa no autorizada.')

def require_admin(request: Request):
    mutation_guard(request)
    token = request.cookies.get(COOKIE, '')
    with LOCK:
        key = digest(token)
        session = SESSIONS.get(key)
        if session and session['expires'] > time.time():
            return session['username']
        SESSIONS.pop(key, None)
    raise HTTPException(401, 'Inicia sesión como administrador.')

def login(request, username, password):
    mutation_guard(request)
    config = get_settings()
    if not config.admin_password:
        raise HTTPException(503, 'Configura ADMIN_PASSWORD en el servidor.')
    ip = request.client.host if request.client else 'local'
    with LOCK:
        current = time.time()
        for key in list(FAILURES):
            if FAILURES[key][1] < current - 300:
                del FAILURES[key]
        count, start = FAILURES.get(ip, (0,current))
        if count >= 5:
            raise HTTPException(429, 'Demasiados intentos. Espera cinco minutos.', headers={'Retry-After':'300'})
        valid = hmac.compare_digest(digest(username), digest(config.admin_username)) & hmac.compare_digest(digest(password), digest(config.admin_password))
        if not valid:
            FAILURES[ip] = (count + 1,start)
            raise HTTPException(401, 'Usuario o contraseña incorrectos.')
        FAILURES.pop(ip, None)
        for key in list(SESSIONS):
            if SESSIONS[key]['expires'] <= current:
                del SESSIONS[key]
        token = secrets.token_urlsafe(40)
        SESSIONS[digest(token)] = {'username':username,'expires':current + config.admin_session_minutes * 60}
        return token
