import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../config/.env"))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

BACKUP_DIR    = Path(__file__).parent.parent / "backups"
MAX_BACKUPS   = 7
DB_HOST       = os.getenv("DB_HOST", "localhost")
DB_PORT       = os.getenv("DB_PORT", "3306")
DB_NAME       = os.getenv("DB_NAME", "HospitalDB")
DB_USER       = os.getenv("DB_USER", "root")
DB_PASSWORD   = os.getenv("DB_PASSWORD", "")


def generar_backup() -> str | None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre      = f"hospitaldb_backup_{timestamp}.sql"
    ruta_backup = BACKUP_DIR / nombre

    # Comando mysqldump
    cmd = [
        "mysqldump",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--add-drop-table", 
        DB_NAME,
    ]

    logger.info("Iniciando backup de '%s'...", DB_NAME)

    try:
        with open(ruta_backup, "w", encoding="utf-8") as f:
            resultado = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
            )

        if resultado.returncode != 0:
            logger.error("Error en mysqldump: %s", resultado.stderr)
            ruta_backup.unlink(missing_ok=True)
            return None

        size_kb = ruta_backup.stat().st_size // 1024
        logger.info(" Backup generado: %s (%s KB)", nombre, size_kb)
        return str(ruta_backup)

    except FileNotFoundError:
        logger.error(
            "mysqldump no encontrado. Agrega MySQL/bin al PATH o instala MySQL Client."
        )
        return None
    except Exception as e:
        logger.error("Error inesperado durante el backup: %s", e)
        return None


def limpiar_backups_antiguos():
    backups = sorted(BACKUP_DIR.glob("hospitaldb_backup_*.sql"))

    if len(backups) > MAX_BACKUPS:
        a_eliminar = backups[:len(backups) - MAX_BACKUPS]
        for archivo in a_eliminar:
            archivo.unlink()
            logger.info("Backup antiguo eliminado: %s", archivo.name)


def restaurar_backup(ruta_sql: str):
    cmd = [
        "mysql",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--user={DB_USER}",
        f"--password={DB_PASSWORD}",
        DB_NAME,
    ]

    logger.info("Restaurando backup desde: %s", ruta_sql)

    with open(ruta_sql, "r", encoding="utf-8") as f:
        resultado = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)

    if resultado.returncode != 0:
        logger.error("Error en restauración: %s", resultado.stderr)
        return False

    logger.info("ase de datos restaurada correctamente.")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("  HospitalDB — Script de Backup")
    print("=" * 50)

    ruta = generar_backup()

    if ruta:
        limpiar_backups_antiguos()
        print(f"\n Backup guardado en: {ruta}")
        print(f"   Política: se conservan los últimos {MAX_BACKUPS} backups.")
    else:
        print("\n El backup falló. Revisa los logs.")