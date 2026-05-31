import logging
from config.database import db_cursor
from app.utils.cifrado import guardar_dpi_cifrado

logger = logging.getLogger(__name__)

def registrar_paciente(datos: dict, id_usuario: int) -> int:
    with db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO paciente
                (nombre, apellido, fecha_nacimiento, dpi_paciente, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datos["nombre"],
            datos["apellido"],
            datos["fecha_nacimiento"],
            datos.get("dpi_paciente"),
            datos.get("telefono"),
        ))

        id_paciente = cursor.lastrowid

        # Cifrar DPI si fue proporcionado
        if datos.get("dpi_paciente"):
            guardar_dpi_cifrado(id_paciente, datos["dpi_paciente"])

        _auditoria(cursor, id_usuario, "INSERT", "paciente", id_paciente)
        logger.info("Paciente registrado → id=%s", id_paciente)
        return id_paciente


def buscar_pacientes(termino: str = "", solo_activos: bool = True) -> list:
    with db_cursor() as cursor:
        filtro_activo = "AND activo = 1" if solo_activos else ""
        cursor.execute(f"""
            SELECT
                id_paciente,
                nombre,
                apellido,
                fecha_nacimiento,
                dpi_paciente,
                telefono,
                fecha_registro,
                activo,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad
            FROM paciente
            WHERE (nombre    LIKE %s
                OR apellido  LIKE %s
                OR dpi_paciente = %s)
            {filtro_activo}
            ORDER BY apellido, nombre
        """, (f"%{termino}%", f"%{termino}%", termino))

        return cursor.fetchall()


def obtener_paciente(id_paciente: int) -> dict | None:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT
                id_paciente,
                nombre,
                apellido,
                fecha_nacimiento,
                dpi_paciente,
                telefono,
                fecha_registro,
                activo,
                TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad
            FROM paciente
            WHERE id_paciente = %s
        """, (id_paciente,))

        return cursor.fetchone()

def editar_paciente(id_paciente: int, datos: dict, id_usuario: int) -> bool:
    with db_cursor() as cursor:
        # Guardar estado anterior para auditoría
        cursor.execute(
            "SELECT nombre, apellido, telefono FROM paciente WHERE id_paciente = %s",
            (id_paciente,)
        )
        anterior = cursor.fetchone()
        if not anterior:
            logger.warning("Editar paciente: id=%s no encontrado", id_paciente)
            return False

        cursor.execute("""
            UPDATE paciente
            SET nombre           = %s,
                apellido         = %s,
                fecha_nacimiento = %s,
                dpi_paciente = %s,
                telefono         = %s
            WHERE id_paciente = %s
        """, (
            datos["nombre"],
            datos["apellido"],
            datos["fecha_nacimiento"],
            datos.get("dpi_paciente"),
            datos.get("telefono"),
            id_paciente,
        ))

        _auditoria(
            cursor, id_usuario, "UPDATE", "paciente", id_paciente,
            datos_anteriores=str(anterior)
        )
        logger.info("Paciente actualizado → id=%s", id_paciente)
        return True

def desactivar_paciente(id_paciente: int, id_usuario: int) -> bool:
    with db_cursor() as cursor:
        cursor.execute("""
            UPDATE paciente SET activo = 0
            WHERE id_paciente = %s AND activo = 1
        """, (id_paciente,))

        if cursor.rowcount == 0:
            logger.warning("Desactivar paciente: id=%s no encontrado o ya inactivo", id_paciente)
            return False

        _auditoria(cursor, id_usuario, "DELETE_LOGICO", "paciente", id_paciente)
        logger.info("Paciente desactivado → id=%s", id_paciente)
        return True

def historial_paciente(id_paciente: int) -> dict:
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT c.id_cita, c.fecha_hora, c.estado, c.motivo,
                   CONCAT(m.nombre,' ',m.apellido) AS medico,
                   a.nombre_area AS area
            FROM cita c
            JOIN medico        m ON m.id_medico = c.MEDICO_id_medico
            JOIN area_hospital a ON a.id_area   = c.AREA_HOSPITAL_id_area
            WHERE c.PACIENTE_id_paciente = %s
            ORDER BY c.fecha_hora DESC
        """, (id_paciente,))
        citas = cursor.fetchall()

        cursor.execute("""
            SELECT id_ingreso, fecha_ingreso, fecha_egreso,
                   motivo_ingreso, estado, nombre_area
            FROM ingreso i
            JOIN area_hospital a ON a.id_area = i.AREA_HOSPITAL_id_area
            WHERE i.PACIENTE_id_paciente = %s
            ORDER BY fecha_ingreso DESC
        """, (id_paciente,))
        ingresos = cursor.fetchall()

        return {"citas": citas, "ingresos": ingresos}


def _auditoria(cursor, id_usuario, accion, tabla, id_registro=None,
               datos_anteriores=None):
    cursor.execute("""
        INSERT INTO auditoria
            (accion, tabla_afectada, id_registro, datos_anteriores,
             USUARIO_SISTEMA_id_usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, (accion, tabla, id_registro, datos_anteriores, id_usuario))