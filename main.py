from config.logging_config import setup_logging
from config.database import test_connection

def main():
    # 1. Inicializar logging
    setup_logging()

    # 2. Verificar conexión a la base de datos antes de lanzar la UI
    print("=" * 50)
    print("  HospitalDB - Sistema de Gestión Hospitalaria")
    print("=" * 50)

    if not test_connection():
        print("\n❌ No se pudo conectar a la base de datos.")
        print("   Verifica el archivo config/.env y que MySQL esté corriendo.")
        return

    print("\n✅ Conexión establecida. Iniciando aplicación...\n")

    # 3. Lanzar la interfaz gráfica
    # from app.views.login import LoginWindow
    # app = LoginWindow()
    # app.mainloop()
    print("[ UI no implementada aún — pendiente Módulo de Vistas ]")


if __name__ == "__main__":
    main()