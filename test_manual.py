from config.logging_config import setup_logging
setup_logging()

# --- Probar pacientes ---
from app.modules.pacientes import registrar_paciente, buscar_pacientes

id_p = registrar_paciente({
    "nombre": "Test",
    "apellido": "Prueba",
    "fecha_nacimiento": "1990-01-01",
    "telefono": "55550000"
}, id_usuario=1)
print(f"✅ Paciente creado → id={id_p}")

resultados = buscar_pacientes("Test")
print(f"✅ Búsqueda → {resultados}")

# --- Probar citas ---
from app.modules.citas import agendar_cita

id_c = agendar_cita({
    "fecha_hora": "2026-06-10 09:00:00",
    "motivo": "Prueba de conexión",
    "id_paciente": id_p,
    "id_medico": 1,
    "id_area": 1
}, id_usuario=1)
print(f"✅ Cita agendada → id={id_c}")

# --- Probar auth ---
from app.utils.auth import login

sesion = login("usr_admin", "admin123")
print(f"✅ Login → {sesion}")