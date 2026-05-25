-- ============================================================
--  HospitalDB - Script DDL
--  Base de Datos II - Universidad Panamericana de Guatemala
-- ============================================================

CREATE DATABASE IF NOT EXISTS HospitalDB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE HospitalDB;

-- ============================================================
-- TABLAS BASE (sin dependencias)
-- ============================================================

CREATE TABLE area_hospital (
    id_area             INT             NOT NULL AUTO_INCREMENT,
    nombre_area         VARCHAR(50)     NOT NULL,
    descripcion         VARCHAR(50)     NULL,
    capacidad_camas     INT             NOT NULL DEFAULT 0,
    PRIMARY KEY (id_area)
);

CREATE TABLE paciente (
    id_paciente         INT             NOT NULL AUTO_INCREMENT,
    nombre              VARCHAR(50)     NOT NULL,
    apellido            VARCHAR(50)     NOT NULL,
    fecha_nacimiento    DATE            NOT NULL,
    dpi_paciente        VARCHAR(13)     NULL,
    telefono            VARCHAR(45)     NULL,
    fecha_registro      DATE            NOT NULL DEFAULT (CURRENT_DATE),
    activo              TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (id_paciente)
);

CREATE TABLE medicamento (
    id_medicamento      INT             NOT NULL AUTO_INCREMENT,
    nombre_generico     VARCHAR(100)    NOT NULL,
    nombre_comercial    VARCHAR(100)    NULL,
    presentacion        VARCHAR(100)    NULL,
    stock_actual        INT             NOT NULL DEFAULT 0,
    stock_minimo        INT             NOT NULL DEFAULT 0,
    PRIMARY KEY (id_medicamento)
);

CREATE TABLE rol (
    id_rol              INT             NOT NULL AUTO_INCREMENT,
    nombre_rol          VARCHAR(50)     NOT NULL,
    descripcion         VARCHAR(50)     NULL,
    PRIMARY KEY (id_rol)
);

-- ============================================================
-- TABLAS CON DEPENDENCIAS DE PRIMER NIVEL
-- ============================================================

CREATE TABLE medico (
    id_medico               INT             NOT NULL AUTO_INCREMENT,
    nombre                  VARCHAR(100)    NOT NULL,
    apellido                VARCHAR(100)    NOT NULL,
    especialidad            VARCHAR(100)    NOT NULL,
    numero_colegiado        VARCHAR(100)    NOT NULL,
    activo                  TINYINT(1)      NOT NULL DEFAULT 1,
    AREA_HOSPITAL_id_area   INT             NOT NULL,
    PRIMARY KEY (id_medico),
    CONSTRAINT fk_medico_area
        FOREIGN KEY (AREA_HOSPITAL_id_area)
        REFERENCES area_hospital (id_area)
);

CREATE TABLE enfermero (
    id_enfermero        INT             NOT NULL AUTO_INCREMENT,
    nombre              VARCHAR(100)    NOT NULL,
    apellido            VARCHAR(100)    NOT NULL,
    turno               VARCHAR(50)     NULL,
    activo              TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (id_enfermero)
);

-- ============================================================
-- USUARIO_SISTEMA (depende de medico y enfermero)
-- ============================================================

CREATE TABLE usuario_sistema (
    id_usuario              INT             NOT NULL AUTO_INCREMENT,
    username                VARCHAR(50)     NOT NULL UNIQUE,
    ultimo_acceso           DATETIME        NULL,
    intentos_fallidos       INT             NOT NULL DEFAULT 0,
    activo                  INT             NOT NULL DEFAULT 1,
    MEDICO_id_medico        INT             NULL,
    ENFERMERO_id_enfermero  INT             NULL,
    PRIMARY KEY (id_usuario),
    CONSTRAINT fk_usuario_medico
        FOREIGN KEY (MEDICO_id_medico)
        REFERENCES medico (id_medico),
    CONSTRAINT fk_usuario_enfermero
        FOREIGN KEY (ENFERMERO_id_enfermero)
        REFERENCES enfermero (id_enfermero)
);

-- ============================================================
-- TABLAS DE SEGURIDAD
-- ============================================================

CREATE TABLE usuario_rol (
    fecha_asignacion        INT             NULL,
    ROL_id_rol              INT             NOT NULL,
    USUARIO_SISTEMA_id_usuario INT          NOT NULL,
    PRIMARY KEY (ROL_id_rol, USUARIO_SISTEMA_id_usuario),
    CONSTRAINT fk_usuariorol_rol
        FOREIGN KEY (ROL_id_rol)
        REFERENCES rol (id_rol),
    CONSTRAINT fk_usuariorol_usuario
        FOREIGN KEY (USUARIO_SISTEMA_id_usuario)
        REFERENCES usuario_sistema (id_usuario)
);

CREATE TABLE privilegio (
    id_privilegio       INT             NOT NULL AUTO_INCREMENT,
    tabla               VARCHAR(100)    NOT NULL,
    puede_select        INT             NOT NULL DEFAULT 0,
    puede_update        INT             NOT NULL DEFAULT 0,
    puede_insert        INT             NOT NULL DEFAULT 0,
    puede_delete        INT             NOT NULL DEFAULT 0,
    ROL_id_rol          INT             NOT NULL,
    PRIMARY KEY (id_privilegio),
    CONSTRAINT fk_privilegio_rol
        FOREIGN KEY (ROL_id_rol)
        REFERENCES rol (id_rol)
);

CREATE TABLE sesion (
    id_sesion                   INT             NOT NULL AUTO_INCREMENT,
    token_sesion                VARCHAR(100)    NOT NULL,
    fecha_inicio                DATETIME        NOT NULL,
    fecha_expiracion            DATETIME        NOT NULL,
    ip_origen                   VARCHAR(50)     NULL,
    activa                      TINYINT(1)      NOT NULL DEFAULT 1,
    USUARIO_SISTEMA_id_usuario  INT             NOT NULL,
    PRIMARY KEY (id_sesion),
    CONSTRAINT fk_sesion_usuario
        FOREIGN KEY (USUARIO_SISTEMA_id_usuario)
        REFERENCES usuario_sistema (id_usuario)
);

CREATE TABLE auditoria (
    id_auditoria                INT             NOT NULL AUTO_INCREMENT,
    accion                      VARCHAR(100)    NOT NULL,
    tabla_afectada              VARCHAR(100)    NOT NULL,
    id_registro                 INT             NULL,
    datos_anteriores            VARCHAR(200)    NULL,
    fecha_hora                  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_origen                   VARCHAR(100)    NULL,
    USUARIO_SISTEMA_id_usuario  INT             NOT NULL,
    PRIMARY KEY (id_auditoria),
    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (USUARIO_SISTEMA_id_usuario)
        REFERENCES usuario_sistema (id_usuario)
);

-- ============================================================
-- TABLAS CLÍNICAS
-- ============================================================

CREATE TABLE cita (
    id_cita                 INT             NOT NULL AUTO_INCREMENT,
    fecha_hora              DATETIME        NOT NULL,
    estado                  VARCHAR(45)     NOT NULL DEFAULT 'Pendiente',
    motivo                  VARCHAR(100)    NULL,
    PACIENTE_id_paciente    INT             NOT NULL,
    MEDICO_id_medico        INT             NOT NULL,
    AREA_HOSPITAL_id_area   INT             NOT NULL,
    PRIMARY KEY (id_cita),
    CONSTRAINT fk_cita_paciente
        FOREIGN KEY (PACIENTE_id_paciente)
        REFERENCES paciente (id_paciente),
    CONSTRAINT fk_cita_medico
        FOREIGN KEY (MEDICO_id_medico)
        REFERENCES medico (id_medico),
    CONSTRAINT fk_cita_area
        FOREIGN KEY (AREA_HOSPITAL_id_area)
        REFERENCES area_hospital (id_area)
);

CREATE TABLE ingreso (
    id_ingreso              INT             NOT NULL AUTO_INCREMENT,
    fecha_ingreso           DATETIME        NOT NULL,
    fecha_egreso            DATETIME        NULL,
    motivo_ingreso          VARCHAR(100)    NULL,
    estado                  VARCHAR(45)     NOT NULL DEFAULT 'Activo',
    AREA_HOSPITAL_id_area   INT             NOT NULL,
    PACIENTE_id_paciente    INT             NOT NULL,
    MEDICO_id_medico        INT             NOT NULL,
    PRIMARY KEY (id_ingreso),
    CONSTRAINT fk_ingreso_area
        FOREIGN KEY (AREA_HOSPITAL_id_area)
        REFERENCES area_hospital (id_area),
    CONSTRAINT fk_ingreso_paciente
        FOREIGN KEY (PACIENTE_id_paciente)
        REFERENCES paciente (id_paciente),
    CONSTRAINT fk_ingreso_medico
        FOREIGN KEY (MEDICO_id_medico)
        REFERENCES medico (id_medico)
);

CREATE TABLE diagnostico (
    id_diagnostico      INT             NOT NULL AUTO_INCREMENT,
    codigo_cie10        VARCHAR(50)     NULL,
    descripcion         VARCHAR(100)    NOT NULL,
    fecha_diagnostico   DATE            NOT NULL DEFAULT (CURRENT_DATE),
    CITA_id_cita        INT             NOT NULL,
    MEDICO_id_medico    INT             NOT NULL,
    PRIMARY KEY (id_diagnostico),
    CONSTRAINT fk_diagnostico_cita
        FOREIGN KEY (CITA_id_cita)
        REFERENCES cita (id_cita),
    CONSTRAINT fk_diagnostico_medico
        FOREIGN KEY (MEDICO_id_medico)
        REFERENCES medico (id_medico)
);

CREATE TABLE prescripcion (
    id_prescripcion             INT             NOT NULL AUTO_INCREMENT,
    dosis                       VARCHAR(100)    NOT NULL,
    frecuencia                  VARCHAR(100)    NOT NULL,
    duracion_dias               INT             NOT NULL,
    fecha_prescripcion          DATE            NOT NULL DEFAULT (CURRENT_DATE),
    DIAGNOSTICO_id_diagnostico  INT             NOT NULL,
    MEDICO_id_medico            INT             NOT NULL,
    MEDICAMENTO_id_medicamento  INT             NOT NULL,
    PRIMARY KEY (id_prescripcion),
    CONSTRAINT fk_prescripcion_diagnostico
        FOREIGN KEY (DIAGNOSTICO_id_diagnostico)
        REFERENCES diagnostico (id_diagnostico),
    CONSTRAINT fk_prescripcion_medico
        FOREIGN KEY (MEDICO_id_medico)
        REFERENCES medico (id_medico),
    CONSTRAINT fk_prescripcion_medicamento
        FOREIGN KEY (MEDICAMENTO_id_medicamento)
        REFERENCES medicamento (id_medicamento)
);

CREATE TABLE inventario_movimiento (
    id_movimiento               INT             NOT NULL AUTO_INCREMENT,
    tipo_movimiento             VARCHAR(45)     NOT NULL,
    cantidad                    INT             NOT NULL,
    stock_resultante            INT             NOT NULL,
    fecha_hora                  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo                      VARCHAR(100)    NULL,
    MEDICAMENTO_id_medicamento  INT             NOT NULL,
    PRIMARY KEY (id_movimiento),
    CONSTRAINT fk_inventario_medicamento
        FOREIGN KEY (MEDICAMENTO_id_medicamento)
        REFERENCES medicamento (id_medicamento)
);

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================