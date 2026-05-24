import os
import logging
import secrets
from datetime import datetime, timedelta

import bcrypt
from config.database import db_cursor

logger = logging.getLogger(__name__)

SESSION_DURATION_MINUTES = int(os.getenv("SESSION_DURATION_MINUTES", 60))
MAX_INTENTOS_FALLIDOS    = 5

def login(username: str, password: str, ip_origen: str = None) -> dict | None:

    if not username or not password:
        logger.warning("Intento de login con credenciales vacías.")
        return None

    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                u.id_usuario,
                u.username,
                u.password_hash,
                u.activo,
                u.intentos_fallidos,
                r.nombre_rol
            FROM usuario_sistema u
            JOIN usuario_rol     ur ON ur.USUARIO_SISTEMA_id_usuario = u.id_usuario
            JOIN rol              r ON r.id_rol = ur.ROL_id_rol
            WHERE u.username = %s
        """, (username,))
        usuario = cursor.fetchone()

        if not usuario:
            logger.warning("Login fallido — usuario no encontrado: %s", username)
            return None

        if not usuario["activo"]:
            logger.warning("Login fallido — cuenta inactiva: %s", username)
            return None

        if usuario["intentos_fallidos"] >= MAX_INTENTOS_FALLIDOS:
            logger.warning("Login fallido — cuenta bloqueada por intentos: %s", username)
            return None

        password_correcta = bcrypt.checkpw(
            password.encode("utf-8"),
            usuario["password_hash"].encode("utf-8")
        )

        if not password_correcta:
            cursor.execute("""
                UPDATE usuario_sistema
                SET intentos_fallidos = intentos_fallidos + 1
                WHERE id_usuario = %s
            """, (usuario["id_usuario"],))

            _registrar_auditoria(
                cursor,
                id_usuario=usuario["id_usuario"],
                accion="LOGIN_FALLIDO",
                tabla="usuario_sistema",
                id_registro=usuario["id_usuario"],
                ip_origen=ip_origen,
            )
            logger.warning("Login fallido — contraseña incorrecta: %s", username)
            return None

        token = secrets.token_hex(32)
        ahora = datetime.now()
        expiracion = ahora + timedelta(minutes=SESSION_DURATION_MINUTES)

        cursor.execute("""
            UPDATE usuario_sistema
            SET intentos_fallidos = 0,
                ultimo_acceso     = %s
            WHERE id_usuario = %s
        """, (ahora, usuario["id_usuario"]))

        cursor.execute("""
            INSERT INTO sesion
                (token_sesion, fecha_inicio, fecha_expiracion, ip_origen, activa,
                 USUARIO_SISTEMA_id_usuario)
            VALUES (%s, %s, %s, %s, 1, %s)
        """, (token, ahora, expiracion, ip_origen, usuario["id_usuario"]))

        _registrar_auditoria(
            cursor,
            id_usuario=usuario["id_usuario"],
            accion="LOGIN_EXITOSO",
            tabla="usuario_sistema",
            id_registro=usuario["id_usuario"],
            ip_origen=ip_origen,
        )

        logger.info("Login exitoso: %s (rol: %s)", username, usuario["nombre_rol"])

        return {
            "id_usuario": usuario["id_usuario"],
            "username":   usuario["username"],
            "rol":        usuario["nombre_rol"],
            "token":      token,
            "expiracion": expiracion.isoformat(),
        }

def logout(token: str, ip_origen: str = None):
    """Invalida la sesión activa del usuario."""
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE sesion
            SET activa = 0
            WHERE token_sesion = %s AND activa = 1
        """, (token,))

        # Obtener id_usuario para la auditoría
        cursor.execute("""
            SELECT USUARIO_SISTEMA_id_usuario
            FROM sesion WHERE token_sesion = %s
        """, (token,))
        row = cursor.fetchone()

        if row:
            _registrar_auditoria(
                cursor,
                id_usuario=row["USUARIO_SISTEMA_id_usuario"],
                accion="LOGOUT",
                tabla="sesion",
                ip_origen=ip_origen,
            )

        logger.info("Sesión cerrada para token: %s...", token[:8])


def validar_sesion(token: str) -> dict | None:
    """
    Verifica que un token de sesión sea válido y no haya expirado.
    Retorna los datos del usuario o None.
    """
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                s.id_sesion,
                s.fecha_expiracion,
                u.id_usuario,
                u.username,
                r.nombre_rol
            FROM sesion          s
            JOIN usuario_sistema u ON u.id_usuario = s.USUARIO_SISTEMA_id_usuario
            JOIN usuario_rol     ur ON ur.USUARIO_SISTEMA_id_usuario = u.id_usuario
            JOIN rol              r ON r.id_rol = ur.ROL_id_rol
            WHERE s.token_sesion = %s AND s.activa = 1
        """, (token,))

        sesion = cursor.fetchone()

        if not sesion:
            return None

        if datetime.now() > sesion["fecha_expiracion"]:
            # Sesión expirada — invalidar
            cursor.execute("""
                UPDATE sesion SET activa = 0
                WHERE token_sesion = %s
            """, (token,))
            logger.info("Sesión expirada para usuario: %s", sesion["username"])
            return None

        return {
            "id_usuario": sesion["id_usuario"],
            "username":   sesion["username"],
            "rol":        sesion["nombre_rol"],
        }


def _registrar_auditoria(cursor, id_usuario: int, accion: str,
                          tabla: str, id_registro: int = None,
                          datos_anteriores: str = None, ip_origen: str = None):
    """Inserta un registro en la tabla de auditoría."""
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, datos_anteriores,
             fecha_hora, ip_origen, USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s, NOW(), %s, %s)
    """, (accion, tabla, id_registro, datos_anteriores, ip_origen, id_usuario))