import os
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def setup_logging():

    log_level = getattr(logging, os.getenv("APP_LOG_LEVEL", "INFO").upper(), logging.INFO)
    log_file  = os.getenv("LOG_FILE", "logs/hospitaldb.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 5_242_880))   # 5 MB por defecto
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))

    # Crear carpeta de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    fmt = "%(asctime)s [%(levelname)s] %(name)s → %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers = []

    # Handler de archivo rotativo
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(fmt, date_fmt))
    handlers.append(file_handler)

    # Handler de consola (con colores si colorlog está disponible)
    try:
        import colorlog
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s" + fmt,
            datefmt=date_fmt,
            log_colors={
                "DEBUG": "cyan", "INFO": "green",
                "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red",
            }
        ))
    except ImportError:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt, date_fmt))
    handlers.append(console_handler)

    logging.basicConfig(level=log_level, handlers=handlers)
    logging.getLogger(__name__).info("Sistema de logging inicializado.")