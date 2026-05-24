import logging
from config.database import db_cursor

logger = logging.getLogger(__name__)


def registrar_entrada(id_medicamento: int, cantidad: int,
                       motivo: str, id_usuario: int) -> int:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT stock_actual FROM medicamento
            WHERE id_medicamento = %s
        """, (id_medicamento,))

        med = cursor.fetchone()
        if not med:
            raise ValueError("Medicamento no encontrado.")

        nuevo_stock = med["stock_actual"] + cantidad

        cursor.execute("""
            UPDATE medicamento SET stock_actual = %s
            WHERE id_medicamento = %s
        """, (nuevo_stock, id_medicamento))

        cursor.execute("""
            INSERT INTO inventario_movimiento
                (tipo_movimiento, cantidad, stock_resultante,
                 motivo, MEDICAMENTO_id_medicamento)
            VALUES ('ENTRADA', %s, %s, %s, %s)
        """, (cantidad, nuevo_stock, motivo, id_medicamento))

        id_mov = cursor.lastrowid
        _auditoria(cursor, id_usuario, "ENTRADA_STOCK", "medicamento", id_medicamento)
        logger.info("Entrada inventario → medicamento=%s cantidad=%s nuevo_stock=%s",
                    id_medicamento, cantidad, nuevo_stock)
        return id_mov


def stock_critico() -> list:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT id_medicamento, nombre_generico, nombre_comercial,
                   stock_actual, stock_minimo,
                   (stock_actual - stock_minimo) AS diferencia
            FROM medicamento
            WHERE stock_actual <= stock_minimo
            ORDER BY diferencia
        """)
        return cursor.fetchall()


def historial_movimientos(id_medicamento: int, limite: int = 50) -> list:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT tipo_movimiento, cantidad, stock_resultante,
                   motivo, fecha_hora
            FROM inventario_movimiento
            WHERE MEDICAMENTO_id_medicamento = %s
            ORDER BY fecha_hora DESC
            LIMIT %s
        """, (id_medicamento, limite))
        return cursor.fetchall()


def listar_medicamentos(solo_disponibles: bool = False) -> list:
    with db_cursor() as cursor:
        filtro = "WHERE stock_actual > 0" if solo_disponibles else ""
        cursor.execute(f"""
            SELECT id_medicamento, nombre_generico, nombre_comercial,
                   presentacion, stock_actual, stock_minimo
            FROM medicamento {filtro}
            ORDER BY nombre_generico
        """)
        return cursor.fetchall()


def _auditoria(cursor, id_usuario, accion, tabla, id_registro=None):
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s)
    """, (accion, tabla, id_registro, id_usuario))