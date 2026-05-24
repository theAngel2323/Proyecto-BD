# HospitalDB
Sistema Integrado de Gestión Hospitalaria — Proyecto Final BD2  
Universidad Panamericana de Guatemala

---

## Tecnologías
- **Backend:** Python 3.11+
- **Base de datos:** MySQL 8.0+
- **Driver:** mysql-connector-python
- **UI:** CustomTkinter

## Estructura del proyecto
```
HospitalDB/
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias Python
├── config/
│   ├── .env.example         # Plantilla de configuración (copiar a .env)
│   ├── database.py          # Módulo de conexión a MySQL
│   └── logging_config.py    # Configuración de logs
├── app/
│   ├── modules/             # Módulos de negocio (pacientes, citas, etc.)
│   ├── models/              # Modelos de datos
│   ├── views/               # Vistas / pantallas de la UI
│   └── utils/               # Utilidades compartidas
├── database/
│   ├── scripts/             # DDL: CREATE TABLE, usuarios, roles
│   ├── migrations/          # Cambios incrementales al esquema
│   └── seeds/               # Datos semilla para pruebas
├── etl/
│   ├── sources/             # Archivos CSV/Excel de entrada
│   └── transforms/          # Scripts de transformación
├── docs/                    # Manuales técnico y de usuario
├── tests/                   # Pruebas unitarias
└── logs/                    # Logs generados en runtime (gitignored)
```

## Configuración inicial

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd HospitalDB
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar la plantilla
cp config/.env.example config/.env

# Editar config/.env con tus credenciales de MySQL
```

Campos obligatorios en `.env`:
| Variable | Descripción | Ejemplo |
|---|---|---|
| DB_HOST | Servidor MySQL | localhost |
| DB_PORT | Puerto | 3306 |
| DB_NAME | Nombre de la BD | hospitaldb |
| DB_USER | Usuario | app_user |
| DB_PASSWORD | Contraseña | TuPassword! |

### 4. Crear la base de datos
```bash
mysql -u root -p < database/scripts/01_ddl_schema.sql
mysql -u root -p < database/scripts/02_usuarios_roles.sql
mysql -u root -p < database/seeds/03_datos_semilla.sql
```

### 5. Verificar la conexión y ejecutar
```bash
python main.py
```

---

## Variaciones de conexión documentadas
Ver `config/database.py` para:
- **Variación 1:** Conexión directa local (desarrollo)
- **Variación 2:** Pool de conexiones (aplicación en producción)
- **Variación 3:** Conexión remota con SSL (descomentar en `.env`)

## Equipo
| Nombre | Carné | Rol |
|Diana Platero|---|FrontEnd|
|Maria Estrada| 000139485 |Backend |
|Angel| |Pruebas QA y documentación|
