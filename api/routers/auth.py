from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.utils.auth import login, logout, sesion_activa

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    forzar:   bool = False   # True para cerrar sesión activa y crear una nueva


class LogoutRequest(BaseModel):
    token: str


@router.post("/login")
def endpoint_login(body: LoginRequest, request: Request):
    """
    Autentica un usuario y retorna el token de sesión.

    Si ya existe una sesión activa retorna un aviso con el tiempo restante.
    Enviar forzar=true para invalidar la sesión anterior y crear una nueva.
    """
    ip = request.client.host if request.client else None

    # Verificar si ya hay sesión activa
    if not body.forzar:
        activa = sesion_activa(body.username)
        if activa:
            return {
                "sesion_activa": True,
                "mensaje": f"Ya tienes una sesión activa. Tiempo restante: {activa['tiempo_restante']}.",
                "token":        activa["token"],
                "username":     activa["username"],
                "rol":          activa["rol"],
                "expiracion":   activa["expiracion"],
                "tiempo_restante": activa["tiempo_restante"],
            }

    # Login normal (invalida sesiones anteriores si forzar=true o no había sesión)
    sesion = login(body.username, body.password, ip_origen=ip)

    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o cuenta bloqueada.",
        )

    return {**sesion, "sesion_activa": False}


@router.post("/logout")
def endpoint_logout(body: LogoutRequest, request: Request):
    """Cierra la sesión activa del usuario."""
    ip = request.client.host if request.client else None
    logout(body.token, ip_origen=ip)
    return {"mensaje": "Sesión cerrada correctamente."}