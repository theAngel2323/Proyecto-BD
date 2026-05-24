import logging
from config.database import db_cursor

logger = logging.getLogger(__name__)


def agendar_cita(datos: dict, id_usuario: int) -> int:

    with db_cursor() as cursor:
        cursor.execute("""
            SELECT id_cita FROM cita
            WHERE MEDICO_id_medico = %s
              AND fecha_hora       = %s
              AND estado NOT IN ('Cancelada')
        """, (datos["id_medico"], datos["fecha_hora"]))

        if cursor.fetchone():
            raise ValueError("El médico ya tiene una cita agendada en ese horario.")

        cursor.execute("""
            INSERT INTO cita
                (fecha_hora, estado, motivo,
                 PACIENTE_id_paciente, MEDICO_id_medico, AREA_HOSPITAL_id_area)
            VALUES (%s, 'Pendiente', %s, %s, %s, %s)
        """, (
            datos["fecha_hora"],
            datos.get("motivo"),
            datos["id_paciente"],
            datos["id_medico"],
            datos["id_area"],
        ))

        id_cita = cursor.lastrowid
        _auditoria(cursor, id_usuario, "INSERT", "cita", id_cita)
        logger.info("Cita agendada → id=%s", id_cita)
        return id_cita


def cancelar_cita(id_cita: int, id_usuario: int) -> bool:
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE cita SET estado = 'Cancelada'
            WHERE id_cita = %s AND estado = 'Pendiente'
        """, (id_cita,))

        if cursor.rowcount == 0:
            logger.warning("Cancelar cita: id=%s no encontrada o no está Pendiente", id_cita)
            return False

        _auditoria(cursor, id_usuario, "CANCELAR", "cita", id_cita)
        logger.info("Cita cancelada → id=%s", id_cita)
        return True


def completar_cita(id_cita: int, id_usuario: int) -> bool:
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE cita SET estado = 'Completada'
            WHERE id_cita = %s AND estado = 'Pendiente'
        """, (id_cita,))

        if cursor.rowcount == 0:
            return False

        _auditoria(cursor, id_usuario, "COMPLETAR", "cita", id_cita)
        return True


def citas_por_medico(id_medico: int, solo_pendientes: bool = False) -> list:
    with db_cursor() as cursor:
        filtro = "AND c.estado = 'Pendiente'" if solo_pendientes else ""
        cursor.execute(f"""
            SELECT
                c.id_cita,
                c.fecha_hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre,' ',p.apellido) AS paciente,
                a.nombre_area                   AS area
            FROM cita c
            JOIN paciente      p ON p.id_paciente = c.PACIENTE_id_paciente
            JOIN area_hospital a ON a.id_area     = c.AREA_HOSPITAL_id_area
            WHERE c.MEDICO_id_medico = %s {filtro}
            ORDER BY c.fecha_hora
        """, (id_medico,))
        return cursor.fetchall()


def citas_por_fecha(fecha: str) -> list:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                c.id_cita,
                c.fecha_hora,
                c.estado,
                c.motivo,
                CONCAT(p.nombre,' ',p.apellido) AS paciente,
                CONCAT(m.nombre,' ',m.apellido) AS medico,
                a.nombre_area                   AS area
            FROM cita c
            JOIN paciente      p ON p.id_paciente = c.PACIENTE_id_paciente
            JOIN medico        m ON m.id_medico   = c.MEDICO_id_medico
            JOIN area_hospital a ON a.id_area     = c.AREA_HOSPITAL_id_area
            WHERE DATE(c.fecha_hora) = %s
            ORDER BY c.fecha_hora
        """, (fecha,))
        return cursor.fetchall()


def _auditoria(cursor, id_usuario, accion, tabla, id_registro=None):
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s)
    """, (accion, tabla, id_registro, id_usuario))