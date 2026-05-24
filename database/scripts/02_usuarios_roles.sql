-- ============================================================
--  HospitalDB - Script de Usuarios, Roles y Privilegios MySQL
--  Módulo 2: Seguridad en la Base de Datos
--  Base de Datos II - Universidad Panamericana de Guatemala
-- ============================================================

USE HospitalDB;
-- ============================================================
-- ROLES A NIVEL DE MYSQL
-- ============================================================

CREATE ROLE IF NOT EXISTS 'rol_admin';
CREATE ROLE IF NOT EXISTS 'rol_medico';
CREATE ROLE IF NOT EXISTS 'rol_enfermero';

-- PRIVILEGIOS POR ROL
-- rol_admin: acceso total
GRANT ALL PRIVILEGES ON HospitalDB.* TO 'rol_admin';

-- rol_medico: acceso clínico (no toca usuarios ni auditoría)
GRANT SELECT, INSERT, UPDATE ON HospitalDB.paciente            TO 'rol_medico';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.cita                TO 'rol_medico';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.diagnostico         TO 'rol_medico';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.prescripcion        TO 'rol_medico';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.ingreso             TO 'rol_medico';
GRANT SELECT                 ON HospitalDB.medicamento         TO 'rol_medico';
GRANT SELECT                 ON HospitalDB.area_hospital       TO 'rol_medico';
GRANT SELECT, INSERT         ON HospitalDB.inventario_movimiento TO 'rol_medico';

-- rol_enfermero: solo lectura clínica + registro de ingresos
GRANT SELECT                 ON HospitalDB.paciente            TO 'rol_enfermero';
GRANT SELECT                 ON HospitalDB.cita                TO 'rol_enfermero';
GRANT SELECT                 ON HospitalDB.diagnostico         TO 'rol_enfermero';
GRANT SELECT                 ON HospitalDB.medicamento         TO 'rol_enfermero';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.ingreso             TO 'rol_enfermero';
GRANT SELECT                 ON HospitalDB.area_hospital       TO 'rol_enfermero';

-- USUARIOS MYSQL

CREATE USER IF NOT EXISTS 'usr_admin'@'localhost'
    IDENTIFIED BY 'Admin$HospitalDB2026!';

CREATE USER IF NOT EXISTS 'usr_medico'@'localhost'
    IDENTIFIED BY 'Medico$HospitalDB2026!';

CREATE USER IF NOT EXISTS 'usr_enfermero'@'localhost'
    IDENTIFIED BY 'Enfermero$HospitalDB2026!';

-- ASIGNAR ROLES A USUARIOS

GRANT 'rol_admin'     TO 'usr_admin'@'localhost';
GRANT 'rol_medico'    TO 'usr_medico'@'localhost';
GRANT 'rol_enfermero' TO 'usr_enfermero'@'localhost';

-- Activar el rol por defecto al conectarse
SET DEFAULT ROLE 'rol_admin'     TO 'usr_admin'@'localhost';
SET DEFAULT ROLE 'rol_medico'    TO 'usr_medico'@'localhost';
SET DEFAULT ROLE 'rol_enfermero' TO 'usr_enfermero'@'localhost';

FLUSH PRIVILEGES;

-- VISTAS DE SEGURIDAD (exponen solo lo necesario por rol)
-- Vista para médicos: pacientes sin DPI (campo sensible oculto)
CREATE OR REPLACE VIEW v_paciente_medico AS
    SELECT
        id_paciente,
        nombre,
        apellido,
        fecha_nacimiento,
        telefono,
        fecha_registro,
        activo
    FROM paciente
    WHERE activo = 1;

-- Vista para enfermeros: solo datos básicos de pacientes activos
CREATE OR REPLACE VIEW v_paciente_enfermero AS
    SELECT
        id_paciente,
        nombre,
        apellido,
        telefono
    FROM paciente
    WHERE activo = 1;

-- Vista de citas del día (uso general para médicos y enfermeros)
CREATE OR REPLACE VIEW v_citas_hoy AS
    SELECT
        c.id_cita,
        c.fecha_hora,
        c.estado,
        c.motivo,
        CONCAT(p.nombre, ' ', p.apellido) AS paciente,
        CONCAT(m.nombre, ' ', m.apellido) AS medico,
        a.nombre_area                      AS area
    FROM cita c
    JOIN paciente      p ON c.PACIENTE_id_paciente  = p.id_paciente
    JOIN medico        m ON c.MEDICO_id_medico       = m.id_medico
    JOIN area_hospital a ON c.AREA_HOSPITAL_id_area  = a.id_area
    WHERE DATE(c.fecha_hora) = CURDATE();

-- Vista de stock crítico (medicamentos bajo mínimo)
CREATE OR REPLACE VIEW v_stock_critico AS
    SELECT
        id_medicamento,
        nombre_generico,
        nombre_comercial,
        stock_actual,
        stock_minimo,
        (stock_actual - stock_minimo) AS diferencia
    FROM medicamento
    WHERE stock_actual <= stock_minimo;

-- Dar acceso a las vistas según rol
GRANT SELECT ON HospitalDB.v_paciente_medico    TO 'rol_medico';
GRANT SELECT ON HospitalDB.v_paciente_enfermero TO 'rol_enfermero';
GRANT SELECT ON HospitalDB.v_citas_hoy          TO 'rol_medico', 'rol_enfermero';
GRANT SELECT ON HospitalDB.v_stock_critico      TO 'rol_medico', 'rol_admin';

