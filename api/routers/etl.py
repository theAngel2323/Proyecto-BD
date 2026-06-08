from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy import create_engine
import pandas as pd
import io
from sqlalchemy import text

router = APIRouter(tags=["ETL"])

# Configuración del motor SQLAlchemy (Reemplaza la contraseña si es distinta)
# Formato: mysql+pymysql://usuario:password@host/BasedeDatos
DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1/HospitalDB"
engine = create_engine(DATABASE_URL)


@router.post("/procesar")
async def procesar_carga_masiva(
    file: UploadFile = File(...), 
    destino: str = Form(...)
    
):
    try:

        # 1. EXTRACT (Extracción)
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
           
            df = pd.read_csv(io.BytesIO(contents), sep=',', encoding='utf-8-sig')
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado.")

        df.columns = df.columns.str.strip().str.lower()
        
        # EL CHISMOSO: Esto imprimirá en tu terminal exactamente lo que vio Pandas
        print(f"--- ARCHIVO RECIBIDO: {file.filename} ---")
        print(f"--- COLUMNAS DETECTADAS: {df.columns.tolist()} ---")
        
        total_registros = len(df)

        # 2. TRANSFORM (Transformación) & LOAD (Carga)
        if destino == 'Registros de Pacientes':
            # Asegurarnos de que las columnas coincidan exactamente con la base de datos
            columnas_esperadas = ['nombre', 'apellido', 'fecha_nacimiento', 'dpi_paciente', 'telefono']
            
            # Limpieza de datos (Transformaciones)
            df['nombre'] = df['nombre'].astype(str).str.strip().str.title()
            df['apellido'] = df['apellido'].astype(str).str.strip().str.title()
            df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento']).dt.date
            
            # Filtramos solo las columnas que van a la BD
            df_final = df[columnas_esperadas]
            
            # Carga Masiva a MySQL
            df_final.to_sql('paciente', con=engine, if_exists='append', index=False)

        elif destino == 'Inventario Central':
            columnas_esperadas = ['nombre_generico', 'nombre_comercial', 'presentacion', 'stock_actual', 'stock_minimo']
            
            # Transformaciones
            df['nombre_generico'] = df['nombre_generico'].astype(str).str.strip().str.capitalize()
            df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0).astype(int)
            df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(0).astype(int)
            
            df_final = df[columnas_esperadas]
            df_final.to_sql('medicamento', con=engine, if_exists='append', index=False)
            
        else:
            raise HTTPException(status_code=400, detail="Destino no válido.")
        

        # --- REGISTRO AUTOMÁTICO EN EL HISTORIAL ---
        with engine.begin() as connection:
            query = text("""
                INSERT INTO historial_etl 
                (nombre_archivo, destino, total_registros, registros_exitosos, estado) 
                VALUES (:arch, :dest, :tot, :exito, 'Completado')
            """)
            connection.execute(query, {
                "arch": file.filename,
                "dest": destino,
                "tot": total_registros,
                "exito": total_registros
            })

        # Si todo sale bien, retornamos las estadísticas para tu frontend
        return {
            "archivo": file.filename,
            "total": total_registros,
            "exitosos": total_registros,
            "errores": 0,
            "estado": "Completado"
        }

    except Exception as e:
        return {"error": f"Error en el proceso ETL: {str(e)}"}
    

    # --- NUEVO ENDPOINT PARA LEER EL HISTORIAL ---


@router.get("/historial")
async def obtener_historial():
    try:
        with engine.connect() as connection:
            # Traemos los últimos 10 registros ordenados desde el más reciente
            query = text("SELECT * FROM historial_etl ORDER BY fecha_carga DESC LIMIT 10")
            resultado = connection.execute(query)
            

            historial = []
            for row in resultado:
                historial.append({
                    "fecha": str(row.fecha_carga)[:16], # Cortamos los segundos (YYYY-MM-DD HH:MM)
                    "archivo": row.nombre_archivo,
                    "destino": row.destino,
                    "total": row.total_registros,
                    "exitosos": row.registros_exitosos,
                    "errores": row.registros_error,
                    "estado": row.estado
                })
            return historial
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/respaldo-pacientes")
async def generar_respaldo_pacientes():
    try:
        with engine.begin() as connection:
            # 1. Por si ejecutas el botón varias veces, borramos el respaldo viejo primero
            connection.execute(text("DROP TABLE IF EXISTS respaldo_pacientes_2026"))
            
            # 2. Ejecutamos el equivalente a SELECT INTO en MySQL
            query = text("""
                CREATE TABLE respaldo_pacientes_2026 AS 
                SELECT * FROM paciente
            """)
            connection.execute(query)
            
            # 3. Opcional: Contar cuántos registros se respaldaron para mostrarlo en pantalla
            resultado = connection.execute(text("SELECT COUNT(*) FROM respaldo_pacientes_2026"))
            total = resultado.scalar()

        return {
            "mensaje": "Respaldo generado exitosamente",
            "tabla": "respaldo_pacientes_2026",
            "total_registros": total
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando respaldo: {str(e)}")