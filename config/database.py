"""
HospitalDB - Módulo de conexión a la base de datos
====================================================
Gestiona la conexión a MySQL usando variables de entorno.
Soporta conexión local, remota y con SSL.
Driver utilizado: mysql-connector-python
"""

import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, Error

# Cargar variables desde el archivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)


def _build_config() -> dict:
    """
    Lee las variables de entorno y construye el diccionario
    de configuración para la conexión a MySQL.

    Partes del string de conexión:
      host     → Dirección del servidor MySQL
      port     → Puerto (por defecto 3306)
      database → Nombre de la base de datos
      user     → Usuario de la base de datos
      password → Contraseña del usuario
      charset  → Codificación de caracteres

    Retorna un dict listo para mysql.connector.
    """
    config = {
        "host":     os.getenv("DB_HOST", "localhost"),
        "port":     int(os.getenv("DB_PORT", 3306)),
        "database": os.getenv("DB_NAME", "hospitaldb"),
        "user":     os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "charset":  os.getenv("DB_CHARSET", "utf8mb4"),
        "use_pure": True,           # Driver puro Python (sin dependencias nativas)
        "autocommit": False,        # Control manual de transacciones
    }

    # ---- Configuración SSL (conexión remota segura) ----
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        config["ssl_ca"]     = ssl_ca
        config["ssl_cert"]   = os.getenv("DB_SSL_CERT")
        config["ssl_key"]    = os.getenv("DB_SSL_KEY")
        config["ssl_verify_cert"] = os.getenv("DB_SSL_VERIFY", "True") == "True"
        logger.info("Conexión configurada CON SSL habilitado.")
    else:
        logger.info("Conexión configurada SIN SSL (modo local/desarrollo).")

    return config


# ============================================================
# VARIACIÓN 1: Conexión directa (simple, para scripts y ETL)
# ============================================================
def get_connection() -> mysql.connector.MySQLConnection:
    """
    Abre y retorna una conexión directa a MySQL.
    El llamador es responsable de cerrarla con conn.close().

    Ejemplo de uso:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM paciente")
        conn.close()
    """
    try:
        config = _build_config()
        conn = mysql.connector.connect(**config)
        logger.debug(
            "Conexión directa establecida → %s:%s/%s",
            config["host"], config["port"], config["database"]
        )
        return conn
    except Error as e:
        logger.error("Error al conectar a la base de datos: %s", e)
        raise


# ============================================================
# VARIACIÓN 2: Pool de conexiones (para la aplicación web/GUI)
# ============================================================
_pool: pooling.MySQLConnectionPool | None = None


def _get_pool() -> pooling.MySQLConnectionPool:
    """Inicializa el pool de conexiones (singleton)."""
    global _pool
    if _pool is None:
        config = _build_config()
        _pool = pooling.MySQLConnectionPool(
            pool_name="hospitaldb_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
            **config,
        )
        logger.info(
            "Pool de conexiones inicializado (tamaño=%s) → %s:%s/%s",
            os.getenv("DB_POOL_SIZE", 5),
            config["host"], config["port"], config["database"],
        )
    return _pool


def get_pooled_connection():
    """
    Obtiene una conexión del pool.
    Se recomienda usar junto al context manager `db_cursor` de abajo.
    """
    try:
        return _get_pool().get_connection()
    except Error as e:
        logger.error("Error al obtener conexión del pool: %s", e)
        raise


# ============================================================
# Context Manager: manejo seguro de cursor + transacciones
# ============================================================
@contextmanager
def db_cursor(use_pool: bool = True):
    """
    Context manager que provee un cursor listo para usar.
    Hace COMMIT automático al salir sin errores,
    y ROLLBACK si ocurre una excepción.

    Ejemplo de uso:
        with db_cursor() as cursor:
            cursor.execute("INSERT INTO paciente ...")
            # COMMIT automático al terminar el bloque
    """
    conn = get_pooled_connection() if use_pool else get_connection()
    cursor = conn.cursor(dictionary=True)   # Resultados como dict
    try:
        yield cursor
        conn.commit()
        logger.debug("Transacción confirmada (COMMIT).")
    except Error as e:
        conn.rollback()
        logger.error("Error en transacción, ejecutando ROLLBACK: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================
# Utilidad: verificar conectividad
# ============================================================
def test_connection() -> bool:
    """
    Verifica que la conexión a la base de datos sea exitosa.
    Retorna True si la conexión es correcta, False en caso contrario.
    Útil para health-checks y arranque de la aplicación.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        logger.info("Conexión exitosa. MySQL version: %s", version[0])
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error("Fallo en la prueba de conexión: %s", e)
        return False


if __name__ == "__main__":
    # Prueba rápida al ejecutar el módulo directamente
    logging.basicConfig(level=logging.DEBUG)
    ok = test_connection()
    print("✅ Conexión OK" if ok else "❌ Conexión fallida")