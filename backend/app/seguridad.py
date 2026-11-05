# seguridad.py
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# --- 1. CONFIGURACIÓN Y CONTRASEÑA ENCRIPTADA ---
SECRET_KEY = (
    "mi_clave_secreta_super_segura_grupo1"  # En producción, usar variables de entorno
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

ADMIN_USER = "admin_uniandes"
ADMIN_PASSWORD_HASH = pwd_context.hash("admin123")


# --- 2. FUNCIONES DE SEGURIDAD (ENCRIPTADO Y JWT) ---
def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def crear_token_acceso(data: dict):
    para_codificar = data.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    para_codificar.update({"exp": expiracion})
    return jwt.encode(para_codificar, SECRET_KEY, algorithm=ALGORITHM)


def verificar_admin_autenticado(token: str = Depends(oauth2_scheme)):
    exception_unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Acceso denegado al área de administración.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario: str = payload.get("sub")
        if usuario != ADMIN_USER:
            raise exception_unauthorized
        return usuario
    except jwt.PyJWTError:
        raise exception_unauthorized


# --- 3. REGISTRO DE ENDPOINTS ADMINISTRATIVOS EN LA APP ---
def registrar_rutas_seguridad(app: FastAPI):

    @app.post("/admin/login")
    def login_admin(form_data: OAuth2PasswordRequestForm = Depends()):
        if form_data.username != ADMIN_USER or not verificar_password(
            form_data.password, ADMIN_PASSWORD_HASH
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario o contraseña incorrectos",
            )

        access_token = crear_token_acceso(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}

    @app.post("/admin/recargar-reglamentos")
    def recargar_base_conocimiento_rag(
        usuario_admin: str = Depends(verificar_admin_autenticado),
    ):
        """Ruta protegida: Solo el administrador autenticado puede re-ingerir documentos a ChromaDB."""
        return {
            "status": "OK",
            "mensaje": f"Base de conocimientos actualizada exitosamente por {usuario_admin}.",
        }