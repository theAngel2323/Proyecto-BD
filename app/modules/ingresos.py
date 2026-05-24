import logging
from datetime import datetime
from config.database import db_cursor

logger = logging.getLogger(__name__)


def registrar_ingreso(datos: dict, id_usuario: int) -> int:
    with db_cursor() as cursor:

        cursor.execute("""
            SELECT
                a.capacidad_camas,
                COUNT(i.id_ingreso) AS camas_ocupadas
            FROM area_hospital a
            LEFT JOIN ingreso i
                ON i.AREA_HOSPITAL_id_area = a.id_area
               AND i.estado = 'Activo'
            WHERE a.id_area = %s
            GROUP BY a.id_area
        """, (datos["id_area"],))

        area = cursor.fetchone()
        if not area:
            raise ValueError("Área no encontrada.")

        if area["camas_ocupadas"] >= area["capacidad_camas"]:
            raise ValueError(
                f"Área sin camas disponibles. "
                f"Capacidad: {area['capacidad_camas']}, "
                f"Ocupadas: {area['camas_ocupadas']}."
            )

        cursor.execute("""
            INSERT INTO ingreso
                (fecha_ingreso, motivo_ingreso, estado,
                 AREA_HOSPITAL_id_area, PACIENTE_id_paciente, MEDICO_id_medico)
            VALUES (NOW(), %s, 'Activo', %s, %s, %s)
        """, (
            datos.get("motivo_ingreso"),
            datos["id_area"],
            datos["id_paciente"],
            datos["id_medico"],
        ))

        id_ingreso = cursor.lastrowid
        _auditoria(cursor, id_usuario, "INSERT", "ingreso", id_ingreso)
        logger.info("Ingreso registrado → id=%s | área=%s", id_ingreso, datos["id_area"])
        return id_ingreso


def registrar_egreso(id_ingreso: int, id_usuario: int) -> bool:
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE ingreso
            SET fecha_egreso = NOW(),
                estado       = 'Egresado'
            WHERE id_ingreso = %s AND estado = 'Activo'
        """, (id_ingreso,))

        if cursor.rowcount == 0:
            logger.warning("Egreso: ingreso id=%s no encontrado o ya cerrado", id_ingreso)
            return False

        _auditoria(cursor, id_usuario, "EGRESO", "ingreso", id_ingreso)
        logger.info("Egreso registrado → ingreso id=%s", id_ingreso)
        return True


def ingresos_activos(id_area: int = None) -> list:

    with db_cursor() as cursor:
        filtro = "AND i.AREA_HOSPITAL_id_area = %s" if id_area else ""
        params = (id_area,) if id_area else ()

        cursor.execute(f"""
            SELECT
                i.id_ingreso,
                i.fecha_ingreso,
                i.motivo_ingreso,
                CONCAT(p.nombre,' ',p.apellido) AS paciente,
                CONCAT(m.nombre,' ',m.apellido) AS medico,
                a.nombre_area                   AS area,
                TIMESTAMPDIFF(DAY, i.fecha_ingreso, NOW()) AS dias_ingresado
            FROM ingreso i
            JOIN paciente      p ON p.id_paciente = i.PACIENTE_id_paciente
            JOIN medico        m ON m.id_medico   = i.MEDICO_id_medico
            JOIN area_hospital a ON a.id_area     = i.AREA_HOSPITAL_id_area
            WHERE i.estado = 'Activo' {filtro}
            ORDER BY i.fecha_ingreso
        """, params)

        return cursor.fetchall()


def ocupacion_por_area() -> list:

    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                a.id_area,
                a.nombre_area,
                a.capacidad_camas,
                COUNT(i.id_ingreso)                           AS camas_ocupadas,
                a.capacidad_camas - COUNT(i.id_ingreso)       AS camas_disponibles,
                ROUND(COUNT(i.id_ingreso) / a.capacidad_camas * 100, 1) AS tasa_ocupacion
            FROM area_hospital a
            LEFT JOIN ingreso i
                ON i.AREA_HOSPITAL_id_area = a.id_area
               AND i.estado = 'Activo'
            GROUP BY a.id_area
            ORDER BY tasa_ocupacion DESC
        """)
        return cursor.fetchall()


def _auditoria(cursor, id_usuario, accion, tabla, id_registro=None):
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s)
    """, (accion, tabla, id_registro, id_usuario))