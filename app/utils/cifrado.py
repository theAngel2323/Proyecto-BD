import os
import logging
from config.database import db_cursor
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../config/.env"))

logger = logging.getLogger(__name__)

# Clave de cifrado AES — viene del .env
AES_KEY = os.getenv("AES_SECRET_KEY", "HospitalDB_AES_Key_2026!")

def guardar_dpi_cifrado(id_paciente: int, dpi: str) -> bool:
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE paciente
            SET dpi_paciente = AES_ENCRYPT(%s, %s)
            WHERE id_paciente = %s
        """, (dpi, AES_KEY, id_paciente))

        logger.info("DPI cifrado guardado → paciente id=%s", id_paciente)
        return cursor.rowcount > 0


def obtener_dpi_descifrado(id_paciente: int) -> str | None:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT CAST(AES_DECRYPT(dpi_paciente, %s) AS CHAR) AS dpi
            FROM paciente
            WHERE id_paciente = %s
        """, (AES_KEY, id_paciente))

        row = cursor.fetchone()
        if not row or not row["dpi"]:
            return None

        return row["dpi"]

def migrar_dpis_a_cifrado() -> int:

    with db_cursor() as cursor:
        cursor.execute("""
            SELECT id_paciente, dpi_paciente
            FROM paciente
            WHERE dpi_paciente IS NOT NULL
              AND LENGTH(dpi_paciente) <= 13
        """)
        pacientes = cursor.fetchall()

        migrados = 0
        for p in pacientes:
            cursor.execute("""
                UPDATE paciente
                SET dpi_paciente = AES_ENCRYPT(%s, %s)
                WHERE id_paciente = %s
            """, (p["dpi_paciente"], AES_KEY, p["id_paciente"]))
            migrados += 1

        logger.info("Migración completada: %s DPIs cifrados.", migrados)
        return migrados


def hashear_diagnostico(descripcion: str) -> str:
    with db_cursor() as cursor:
        cursor.execute("SELECT SHA2(%s, 256) AS hash", (descripcion,))
        row = cursor.fetchone()
        return row["hash"] if row else None