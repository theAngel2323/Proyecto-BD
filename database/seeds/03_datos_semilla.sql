-- ============================================================
--  HospitalDB - Datos Semilla
--  Base de Datos II - Universidad Panamericana de Guatemala
-- ============================================================

USE HospitalDB;

INSERT INTO area_hospital (nombre_area, descripcion, capacidad_camas) VALUES
('Emergencias',       'Atención de urgencias',           20),
('Medicina Interna',  'Enfermedades internas',            30),
('Pediatría',         'Atención a menores de edad',       25),
('Cirugía General',   'Procedimientos quirúrgicos',       15),
('Ginecología',       'Salud femenina y obstetricia',     20),
('Traumatología',     'Lesiones óseas y musculares',      18),
('Cardiología',       'Enfermedades del corazón',         12),
('UCI',               'Unidad de cuidados intensivos',    10);

INSERT INTO medico (nombre, apellido, especialidad, numero_colegiado, activo, AREA_HOSPITAL_id_area) VALUES
('Carlos',   'Mendoza',   'Medicina de Emergencias', 'COL-001', 1, 1),
('Ana',      'García',    'Medicina Interna',        'COL-002', 1, 2),
('Roberto',  'López',     'Pediatría',               'COL-003', 1, 3),
('María',    'Hernández', 'Cirugía General',         'COL-004', 1, 4),
('Jorge',    'Ramírez',   'Ginecología',             'COL-005', 1, 5),
('Laura',    'Castillo',  'Traumatología',           'COL-006', 1, 6),
('Fernando', 'Torres',    'Cardiología',             'COL-007', 1, 7),
('Sofía',    'Vásquez',   'Medicina Intensiva',      'COL-008', 1, 8);

INSERT INTO enfermero (nombre, apellido, turno, activo) VALUES
('Pedro',    'Juárez',    'Mañana',  1),
('Carmen',   'Flores',    'Tarde',   1),
('Miguel',   'Ortiz',     'Noche',   1),
('Sandra',   'Morales',   'Mañana',  1),
('Luis',     'Reyes',     'Tarde',   1);

INSERT INTO paciente (nombre, apellido, fecha_nacimiento, dpi_paciente, telefono, fecha_registro, activo) VALUES
('Juan',      'Pérez',      '1985-03-15', '1234567890101', '55551001', '2026-01-10', 1),
('María',     'González',   '1990-07-22', '2345678901202', '55551002', '2026-01-12', 1),
('Carlos',    'Rodríguez',  '1978-11-05', '3456789012303', '55551003', '2026-01-15', 1),
('Ana',       'Martínez',   '2000-02-28', '4567890123404', '55551004', '2026-01-20', 1),
('Luis',      'García',     '1965-09-10', '5678901234505', '55551005', '2026-01-22', 1),
('Rosa',      'López',      '1995-04-18', '6789012345606', '55551006', '2026-02-01', 1),
('Diego',     'Hernández',  '1988-06-30', '7890123456707', '55551007', '2026-02-03', 1),
('Sofía',     'Torres',     '2010-12-01', '8901234567808', '55551008', '2026-02-05', 1),
('Pedro',     'Ramírez',    '1972-08-14', '9012345678909', '55551009', '2026-02-10', 1),
('Elena',     'Castillo',   '1993-01-25', '0123456789010', '55551010', '2026-02-12', 1),
('Marco',     'Vásquez',    '1980-05-07', '1234509876101', '55551011', '2026-02-15', 1),
('Isabel',    'Morales',    '2005-03-19', '2345610987202', '55551012', '2026-02-18', 1),
('Andrés',    'Reyes',      '1970-10-23', '3456721098303', '55551013', '2026-03-01', 1),
('Valeria',   'Juárez',     '1998-07-11', '4567832109404', '55551014', '2026-03-03', 1),
('Roberto',   'Flores',     '1983-02-16', '5678943210505', '55551015', '2026-03-05', 1),
('Claudia',   'Ortiz',      '2001-09-04', '6789054321606', '55551016', '2026-03-08', 1),
('Fernando',  'Mendoza',    '1976-11-28', '7890165432707', '55551017', '2026-03-10', 1),
('Patricia',  'Cruz',       '1992-04-09', '8901276543808', '55551018', '2026-03-12', 1),
('Héctor',    'Aguilar',    '1968-06-17', '9012387654909', '55551019', '2026-03-15', 1),
('Mónica',    'Pineda',     '1987-12-30', '0123498765010', '55551020', '2026-03-18', 1);

-- ============================================================
-- MEDICAMENTOS
-- ============================================================
INSERT INTO medicamento (nombre_generico, nombre_comercial, presentacion, stock_actual, stock_minimo) VALUES
('Paracetamol',       'Tempra',        'Tableta 500mg',     500, 50),
('Ibuprofeno',        'Advil',         'Tableta 400mg',     300, 30),
('Amoxicilina',       'Amoxil',        'Cápsula 500mg',     200, 20),
('Metformina',        'Glucophage',    'Tableta 850mg',     400, 40),
('Enalapril',         'Renitec',       'Tableta 10mg',      250, 25),
('Omeprazol',         'Prilosec',      'Cápsula 20mg',      350, 35),
('Loratadina',        'Claritin',      'Tableta 10mg',      180, 20),
('Diclofenaco',       'Voltaren',      'Tableta 50mg',      220, 25),
('Azitromicina',      'Zithromax',     'Tableta 500mg',      80, 15),
('Insulina NPH',      'Humulin N',     'Frasco 10ml',        40,  5),
('Metronidazol',      'Flagyl',        'Tableta 500mg',     150, 20),
('Ciprofloxacino',    'Cipro',         'Tableta 500mg',      90, 15);

INSERT INTO rol (nombre_rol, descripcion) VALUES
('Administrador', 'Acceso total al sistema'),
('Médico',        'Gestión clínica completa'),
('Enfermero',     'Consulta y registro de ingresos');

INSERT INTO usuario_sistema (username, activo, MEDICO_id_medico, ENFERMERO_id_enfermero) VALUES
('usr_admin',     1, NULL, NULL),
('dr_mendoza',    1, 1,    NULL),
('dr_garcia',     1, 2,    NULL),
('enf_juarez',    1, NULL, 1),
('enf_flores',    1, NULL, 2);

-- ============================================================
-- ASIGNACIÓN DE ROLES A USUARIOS
-- ============================================================
INSERT INTO usuario_rol (ROL_id_rol, USUARIO_SISTEMA_id_usuario) VALUES
(1, 1),  -- usr_admin     → Administrador
(2, 2),  -- dr_mendoza    → Médico
(2, 3),  -- dr_garcia     → Médico
(3, 4),  -- enf_juarez    → Enfermero
(3, 5);  -- enf_flores    → Enfermero


INSERT INTO cita (fecha_hora, estado, motivo, PACIENTE_id_paciente, MEDICO_id_medico, AREA_HOSPITAL_id_area) VALUES
('2026-05-01 08:00:00', 'Completada', 'Control general',        1, 2, 2),
('2026-05-01 09:00:00', 'Completada', 'Dolor abdominal',        2, 4, 4),
('2026-05-02 10:00:00', 'Completada', 'Fiebre pediátrica',      8, 3, 3),
('2026-05-05 08:30:00', 'Completada', 'Control diabetes',       5, 2, 2),
('2026-05-06 11:00:00', 'Completada', 'Dolor de pecho',         9, 7, 7),
('2026-05-10 09:00:00', 'Completada', 'Control prenatal',       6, 5, 5),
('2026-05-12 14:00:00', 'Completada', 'Fractura muñeca',       10, 6, 6),
('2026-05-15 08:00:00', 'Pendiente',  'Control hipertensión',   3, 2, 2),
('2026-05-20 10:30:00', 'Pendiente',  'Revisión post-cirugía',  4, 4, 4),
('2026-06-01 09:00:00', 'Pendiente',  'Control general',        7, 2, 2),
('2026-06-02 11:00:00', 'Pendiente',  'Consulta cardiología',  11, 7, 7),
('2026-06-03 08:00:00', 'Pendiente',  'Dolor rodilla',         12, 6, 6),
('2026-06-04 10:00:00', 'Pendiente',  'Control pediátrico',    13, 3, 3),
('2026-06-05 09:30:00', 'Pendiente',  'Revisión ginecológica', 14, 5, 5),
('2026-06-06 08:00:00', 'Pendiente',  'Emergencia general',    15, 1, 1);
