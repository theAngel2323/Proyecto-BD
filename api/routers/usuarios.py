from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from config.database import db_cursor
import bcrypt

router = APIRouter()

class UsuarioCreate(BaseModel):
    nombre_completo: str
    email: Optional[str] = None
    username: str
    password: str
    rol_id: int
# 1. Creamos el modelo para recibir los datos de tu frontend
class UsuarioUpdate(BaseModel):
    id_rol: int
    activo: bool

# 2. Creamos la ruta PATCH que tu frontend está buscando a gritos

@router.patch("/{id_usuario}")
def actualizar_usuario(id_usuario: int, datos: UsuarioUpdate):
    try:
        with db_cursor() as cursor:
            # 1. Actualizar si está Activo o Suspendido en usuario_sistema
            estado_num = 1 if datos.activo else 0
            cursor.execute("""
                UPDATE usuario_sistema 
                SET activo = %s 
                WHERE id_usuario = %s
            """, (estado_num, id_usuario))
            
            # 2. EL TRUCO: Borrar todos los roles anteriores para evitar duplicados
            cursor.execute("""
                DELETE FROM usuario_rol
                WHERE USUARIO_SISTEMA_id_usuario = %s
            """, (id_usuario,))
            
            # 3. Insertar el nuevo rol exacto que mandó el frontend
            cursor.execute("""
                INSERT INTO usuario_rol (ROL_id_rol, USUARIO_SISTEMA_id_usuario)
                VALUES (%s, %s)
            """, (datos.id_rol, id_usuario))
            
            return {"message": "Usuario y rol actualizados exitosamente"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Modelo para recibir la lista de pestañas
class ModulosUpdate(BaseModel):
    modulos: List[str]

@router.get("/")
def listar_usuarios():
    with db_cursor() as cursor:
        # Hacemos un JOIN desde usuario_sistema -> usuario_rol -> rol
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.username,
                u.nombre_completo,
                u.activo, 
                r.nombre_rol as rol
            FROM usuario_sistema u
            LEFT JOIN usuario_rol ur ON u.id_usuario = ur.USUARIO_SISTEMA_id_usuario
            LEFT JOIN rol r ON ur.ROL_id_rol = r.id_rol
        """)
        return cursor.fetchall()

@router.post("/")
def crear_usuario(user: UsuarioCreate):
    try:
        with db_cursor() as cursor:
            # 1. Encriptamos la contraseña plana usando bcrypt nativo
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
            
            # 2. Insertamos en usuario_sistema (usando el hash)
            cursor.execute("""
                INSERT INTO usuario_sistema (username, nombre_completo, password_hash, activo, intentos_fallidos)
                VALUES (%s, %s, %s, 1, 0)
            """, (user.username, user.nombre_completo, hashed_pw))
            
            id_usuario = cursor.lastrowid
            
            # 3. Asignamos el rol en la tabla intermedia
            cursor.execute("""
                INSERT INTO usuario_rol (USUARIO_SISTEMA_id_usuario, ROL_id_rol)
                VALUES (%s, %s)
            """, (id_usuario, user.rol_id))
            
            # LA SOLUCIÓN: Le decimos directo a MySQL que guarde los cambios
            cursor.execute("COMMIT;")
            
            return {"mensaje": "Usuario creado exitosamente"}
            
    except Exception as e:
        # Esto atrapará cualquier error de SQL y lo mostrará en la terminal
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auditoria")
def listar_auditoria(
    request: Request, # <-- Aquí atrapamos la IP de quien hace la petición
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    # Demostración del Punto 1: Así obtienes la IP real del usuario en cualquier endpoint
    ip_del_usuario = request.client.host 
    
    try:
        offset = (page - 1) * limit
        params = []
        where_clause = "WHERE 1=1"

        # Aplicamos los filtros dinámicamente (Punto 2)
        if search:
            where_clause += " AND u.username LIKE %s"
            params.append(f"%{search}%")
        if fecha_inicio:
            where_clause += " AND DATE(a.fecha_hora) >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            where_clause += " AND DATE(a.fecha_hora) <= %s"
            params.append(fecha_fin)

        query_count = f"SELECT COUNT(*) as total FROM auditoria a LEFT JOIN usuario_sistema u ON a.USUARIO_SISTEMA_id_usuario = u.id_usuario {where_clause}"
        query_data = f"""
            SELECT a.id_auditoria, a.accion, a.tabla_afectada, a.fecha_hora, u.username, a.ip_origen
            FROM auditoria a
            LEFT JOIN usuario_sistema u ON a.USUARIO_SISTEMA_id_usuario = u.id_usuario
            {where_clause}
            ORDER BY a.fecha_hora DESC LIMIT %s OFFSET %s
        """
        
        with db_cursor() as cursor:
            # Primero contamos cuántos registros hay en total con esos filtros
            cursor.execute(query_count, params)
            total_records = cursor.fetchone()
            total = total_records['total'] if type(total_records) is dict else total_records[0]

            # Luego traemos solo los 10 de la página actual
            params_data = params + [limit, offset]
            cursor.execute(query_data, params_data)
            logs = cursor.fetchall()
            
            # Devolvemos un objeto estructurado para que el frontend pueda paginar
            return {
                "data": logs,
                "total": total,
                "page": page,
                "limit": limit
            }
    except Exception as e:
        print(f"Error al leer auditoria: {e}")
        return {"data": [], "total": 0, "page": 1, "limit": 10}
    
      
@router.get("/roles")
def listar_roles():
    with db_cursor() as cursor:
        # Asegúrate de traer la descripcion también
        cursor.execute("SELECT id_rol, nombre_rol, descripcion FROM rol")
        return cursor.fetchall()

@router.get("/roles/{id_rol}/modulos")
def obtener_modulos(id_rol: int):
    with db_cursor() as cursor:
        cursor.execute("""
            SELECT modulo 
            FROM rol_modulo 
            WHERE ROL_id_rol = %s
        """, (id_rol,))
        resultados = cursor.fetchall()
        
        # Como el cursor devuelve diccionarios, extraemos solo los nombres en una lista plana
        # Ejemplo de salida: ["citas", "pacientes", "reportes"]
        modulos = [row['modulo'] if isinstance(row, dict) else row[0] for row in resultados]
        return modulos

@router.put("/roles/{id_rol}/modulos")
def actualizar_modulos(id_rol: int, data: ModulosUpdate):
    try:
        with db_cursor() as cursor:
            # 1. Primero borramos todos los accesos anteriores de este rol
            cursor.execute("DELETE FROM rol_modulo WHERE ROL_id_rol = %s", (id_rol,))
            
            # 2. Si el frontend envió pestañas, las insertamos una por una
            if data.modulos:
                for modulo in data.modulos:
                    cursor.execute("""
                        INSERT INTO rol_modulo (ROL_id_rol, modulo) 
                        VALUES (%s, %s)
                    """, (id_rol, modulo))
            
            # 3. El truco infalible para guardar directo en MySQL
            cursor.execute("COMMIT;")
            return {"mensaje": "Permisos de pestañas actualizados correctamente"}
            
    except Exception as e:
        print(f"Error al guardar módulos: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar permisos")