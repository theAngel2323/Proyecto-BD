import mysql.connector
from faker import Faker
import random

# Configuración de conexión
db_config = {
    'host': '127.0.0.1',
    'user': 'root', # Cambia por tu usuario
    'password': 'root', # Cambia por tu contraseña
    'database': 'HospitalDB'
}

fake = Faker('es_ES') # Datos en español de Guatemala

def populate():
    conn = mysql.connector.connect(**db_config)
    print("¡Conexión exitosa a la base de datos!")
    cursor = conn.cursor()

    print("--- Iniciando poblado de base de datos ---")

    # 1. Poblar Area Hospital
    areas = ['Emergencia', 'Pediatría', 'Cirugía', 'UCI', 'Consulta Externa']
    for a in areas:
        cursor.execute("INSERT INTO area_hospital (nombre_area, capacidad_camas) VALUES (%s, %s)", (a, 20))

    # 2. Poblar Medicamentos
    for _ in range(200):
        cursor.execute("INSERT INTO medicamento (nombre_generico, stock_actual, stock_minimo) VALUES (%s, %s, %s)", 
                       (fake.word().capitalize(), random.randint(10, 500), 50))

    # 3. Poblar Pacientes
    for _ in range(400):
        cursor.execute("INSERT INTO paciente (nombre, apellido, fecha_nacimiento, dpi_paciente) VALUES (%s, %s, %s, %s)", 
                       (fake.first_name(), fake.last_name(), fake.date_of_birth(minimum_age=0, maximum_age=90), fake.random_number(digits=13, fix_len=True)))

    # 4. Poblar Médicos (Asumiendo que las áreas tienen IDs del 1 al 5)
    for _ in range(50):
        cursor.execute("INSERT INTO medico (nombre, apellido, especialidad, numero_colegiado, AREA_HOSPITAL_id_area) VALUES (%s, %s, %s, %s, %s)",
                       (fake.first_name(), fake.last_name(), "General", str(random.randint(1000, 9999)), random.randint(1, 5)))


   # 1. Obtenemos listas reales de IDs en lugar de adivinar rangos
    cursor.execute("SELECT id_paciente FROM paciente")
    lista_pacientes = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT id_medico FROM medico")
    lista_medicos = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT id_area FROM area_hospital")
    lista_areas = [r[0] for r in cursor.fetchall()]

    # 2. Insertamos citas usando random.choice sobre las listas reales
    print("--- Insertando citas ---")
    for _ in range(250):
        paciente_id = random.choice(lista_pacientes)
        medico_id = random.choice(lista_medicos)
        area_id = random.choice(lista_areas)
        
        cursor.execute("INSERT INTO cita (fecha_hora, PACIENTE_id_paciente, MEDICO_id_medico, AREA_HOSPITAL_id_area) VALUES (%s, %s, %s, %s)",
                       (fake.date_time_this_year(), paciente_id, medico_id, area_id))


    conn.commit()
    print("--- ¡Éxito! 1,000+ registros insertados ---")
    cursor.close()
    conn.close()
    
    

if __name__ == "__main__":
    populate()