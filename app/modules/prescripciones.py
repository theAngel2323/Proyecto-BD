import logging
from config.database import db_cursor

logger = logging.getLogger(__name__)


#registro de diagnostico
def registrar_diagnostico(datos: dict, id_usuario: int) -> int:
    """
    Registra un diagnóstico asociado a una cita.

    Args:
        datos: codigo_cie10, descripcion, id_cita, id_medico
    """
    with db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO diagnostico
                (codigo_cie10, descripcion, CITA_id_cita, MEDICO_id_medico)
            VALUES (%s, %s, %s, %s)
        """, (
            datos.get("codigo_cie10"),
            datos["descripcion"],
            datos["id_cita"],
            datos["id_medico"],
        ))

        id_diagnostico = cursor.lastrowid
        _auditoria(cursor, id_usuario, "INSERT", "diagnostico", id_diagnostico)
        logger.info("Diagnóstico registrado → id=%s", id_diagnostico)
        return id_diagnostico


#preescribir medicamento

def prescribir_medicamento(datos: dict, id_usuario: int) -> dict:
 
    with db_cursor() as cursor:

        cursor.execute("""
            SELECT stock_actual, nombre_generico
            FROM medicamento
            WHERE id_medicamento = %s
        """, (datos["id_medicamento"],))

        medicamento = cursor.fetchone()
        if not medicamento:
            raise ValueError("Medicamento no encontrado.")

        cantidad = datos.get("cantidad_dispensada", 1)

        if medicamento["stock_actual"] < cantidad:
            raise ValueError(
                f"Stock insuficiente para '{medicamento['nombre_generico']}'. "
                f"Disponible: {medicamento['stock_actual']}, solicitado: {cantidad}."
            )

        cursor.execute("""
            INSERT INTO prescripcion
                (dosis, frecuencia, duracion_dias,
                 DIAGNOSTICO_id_diagnostico, MEDICO_id_medico,
                 MEDICAMENTO_id_medicamento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos["dosis"],
            datos["frecuencia"],
            datos["duracion_dias"],
            datos["id_diagnostico"],
            datos["id_medico"],
            datos["id_medicamento"],
        ))
        id_prescripcion = cursor.lastrowid

        nuevo_stock = medicamento["stock_actual"] - cantidad
        cursor.execute("""
            UPDATE medicamento
            SET stock_actual = %s
            WHERE id_medicamento = %s
        """, (nuevo_stock, datos["id_medicamento"]))

        cursor.execute("""
            INSERT INTO inventario_movimiento
                (tipo_movimiento, cantidad, stock_resultante, motivo,
                 MEDICAMENTO_id_medicamento)
            VALUES ('SALIDA', %s, %s, 'Prescripción médica', %s)
        """, (cantidad, nuevo_stock, datos["id_medicamento"]))

        _auditoria(cursor, id_usuario, "INSERT", "prescripcion", id_prescripcion)
        logger.info(
            "Prescripción registrada → id=%s | stock %s restante=%s",
            id_prescripcion, medicamento["nombre_generico"], nuevo_stock
        )

        # COMMIT automático al salir del bloque db_cursor sin error
        return {
            "id_prescripcion":  id_prescripcion,
            "stock_resultante": nuevo_stock,
        }


#Consultas
def diagnosticos_por_cita(id_cita: int) -> list:
    """Lista los diagnósticos de una cita con sus prescripciones."""
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                d.id_diagnostico,
                d.codigo_cie10,
                d.descripcion,
                d.fecha_diagnostico,
                p.id_prescripcion,
                p.dosis,
                p.frecuencia,
                p.duracion_dias,
                m.nombre_generico  AS medicamento,
                m.presentacion
            FROM diagnostico d
            LEFT JOIN prescripcion p ON p.DIAGNOSTICO_id_diagnostico = d.id_diagnostico
            LEFT JOIN medicamento  m ON m.id_medicamento = p.MEDICAMENTO_id_medicamento
            WHERE d.CITA_id_cita = %s
            ORDER BY d.fecha_diagnostico DESC
        """, (id_cita,))
        return cursor.fetchall()


def medicamentos_mas_prescritos(limite: int = 10) -> list:
    """Top N medicamentos más prescritos (útil para dashboards)."""
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                m.nombre_generico,
                m.nombre_comercial,
                COUNT(p.id_prescripcion) AS total_prescripciones
            FROM prescripcion p
            JOIN medicamento m ON m.id_medicamento = p.MEDICAMENTO_id_medicamento
            GROUP BY m.id_medicamento
            ORDER BY total_prescripciones DESC
            LIMIT %s
        """, (limite,))
        return cursor.fetchall()


def _auditoria(cursor, id_usuario, accion, tabla, id_registro=None):
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s)
    """, (accion, tabla, id_registro, id_usuario))