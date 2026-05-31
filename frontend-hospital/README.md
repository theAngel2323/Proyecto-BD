# HospitalDB - Frontend

Sistema Integrado de Gestion Hospitalaria
Universidad Panamericana de Guatemala - BD2 - 2026

---

## Estructura del proyecto

    frontend-hospital/
      index.html            Login con autenticacion real
      dashboard.html        Dashboard con KPIs y ultimas citas
      pacientes.html        Gestion completa de pacientes
      citas.html            Agenda medica con filtros
      prescripciones.html   Prescripciones y diagnosticos
      ingresos.html         Control de ingresos y egresos
      administracion.html   Usuarios y roles (datos de ejemplo)
      etl.html              Carga masiva de datos ETL
      reportes.html         Tableros y graficas con datos reales
      css/
        styles.css          Estilos globales del sistema
      js/
        app.js              Configuracion de API y funciones helper
        layout.js           Sidebar y topnav dinamicos

---

## Requisitos

- Backend HospitalDB corriendo en http://127.0.0.1:8000
- VS Code con la extension Live Server instalada
- Navegador moderno: Chrome, Firefox o Edge
- No requiere instalar Node.js ni dependencias adicionales

---

## Como ejecutar

### Paso 1 - Iniciar el backend

En la carpeta raiz del proyecto con el venv activo:

    venv\Scripts\activate
    python -m uvicorn api.main:app --reload

Verificar que aparezca:

    INFO: Uvicorn running on http://127.0.0.1:8000
    INFO: Application startup complete.

### Paso 2 - Abrir el frontend

En VS Code, clic derecho sobre frontend-hospital/index.html
y seleccionar Open with Live Server.

El sistema abre en:

    http://127.0.0.1:5500/frontend-hospital/index.html

### Paso 3 - Iniciar sesion

Usar las credenciales del sistema. Ver seccion de credenciales abajo.

---

## Credenciales de prueba

    usr_admin   / admin123   Administrador
    dr_mendoza  / medico123  Medico
    dr_garcia   / medico123  Medico
    enf_juarez  / enf123     Enfermero
    enf_flores  / enf123     Enfermero

---

## Modulos del sistema

### Login
- Endpoint: POST /api/auth/login
- Estado: Conectado al backend
- Descripcion: Autenticacion con usuario y contraseña hasheada con bcrypt

### Dashboard
- Endpoints: GET /api/pacientes/, GET /api/citas/, GET /api/inventario/
- Estado: Conectado al backend
- Descripcion: KPIs en tiempo real, ultimas citas y distribucion por estado

### Pacientes
- Endpoints: GET, POST /api/pacientes/ | PUT, DELETE /api/pacientes/{id}
- Estado: Conectado al backend
- Descripcion: Registro, busqueda, edicion y desactivacion logica de pacientes

### Citas Medicas
- Endpoints: GET, POST /api/citas/ | PATCH completar | PATCH cancelar
- Estado: Conectado al backend
- Descripcion: Agenda medica con filtros por fecha, medico y estado

### Prescripciones
- Endpoints: POST /api/prescripciones/diagnostico | POST /api/prescripciones/
- Estado: Conectado al backend
- Descripcion: Flujo de cita a diagnostico a medicamento con control de stock

### Ingresos
- Endpoints: GET, POST /api/ingresos/ | GET /api/ingresos/ocupacion | PATCH egreso
- Estado: Conectado al backend
- Descripcion: Control de hospitalizaciones y egresos por area

### Reportes
- Endpoints: GET top-medicamentos | GET ocupacion | GET stock-critico
- Estado: Conectado al backend
- Descripcion: Graficas de citas por mes, citas por estado, medicamentos
  prescritos, ocupacion por departamento y stock critico

### Administracion
- Endpoints: Sin endpoint en el backend actual
- Estado: Datos de ejemplo
- Descripcion: Interfaz de usuarios, roles y auditoria de accesos

### Carga de Datos ETL
- Endpoints: Sin endpoint en el backend actual
- Estado: Simulacion visual
- Descripcion: Interfaz para importar CSV y Excel con mapeo de campos

---

## Configuracion de la URL del backend

Si el backend corre en un puerto diferente, editar la primera linea de js/app.js:

    const API_BASE = 'http://127.0.0.1:8000/api';

Cambiar 8000 por el puerto correcto.

---

## Tecnologias utilizadas

    HTML5 / CSS3     -- Estructura y estilos
    JavaScript ES6   -- Logica del cliente sin frameworks
    Tabler Icons     -- Iconografia via CDN
    Chart.js 4.4.0   -- Graficas y tableros via CDN
    DM Sans          -- Tipografia via Google Fonts CDN

---

## Notas importantes

- El frontend no requiere compilacion ni herramientas de build
- Todas las llamadas a la API incluyen el token Bearer automaticamente
- El token de sesion se guarda en localStorage bajo hdb_token y hdb_user
- Si la sesion expira, el sistema redirige automaticamente al login
- El modulo de Administracion muestra datos de ejemplo porque el backend
  no tiene endpoints de gestion de usuarios en esta version
- El modulo ETL simula visualmente el proceso; el script real se ejecuta
  desde el backend por separado
- Abrir los archivos HTML directamente sin Live Server causa errores de CORS
