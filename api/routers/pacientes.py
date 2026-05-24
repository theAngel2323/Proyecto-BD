from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from datetime import date

from api.dependencies import get_usuario_actual, require_rol
from fastapi import Depends

from app.modules.pacientes import (
    registrar_paciente, buscar_pacientes,
    obtener_paciente, editar_paciente,
    desactivar_paciente, historial_paciente,
)

router = APIRouter()


class PacienteBody(BaseModel):
    nombre:           str
    apellido:         str
    fecha_nacimiento: date
    dpi_paciente:     Optional[str] = None
    telefono:         Optional[str] = None


@router.get("/")
def listar_pacientes(
    termino: str = Query(default="", description="Buscar por nombre, apellido o DPI"),
    solo_activos: bool = Query(default=True),
    usuario: dict = Depends(get_usuario_actual),
):
    return buscar_pacientes(termino, solo_activos)


@router.get("/{id_paciente}")
def detalle_paciente(
    id_paciente: int,
    usuario: dict = Depends(get_usuario_actual),
):
    paciente = obtener_paciente(id_paciente)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")
    return paciente


@router.get("/{id_paciente}/historial")
def ver_historial(
    id_paciente: int,
    usuario: dict = Depends(get_usuario_actual),
):
    return historial_paciente(id_paciente)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_paciente(
    body: PacienteBody,
    usuario: dict = Depends(get_usuario_actual),
):
    id_paciente = registrar_paciente(body.model_dump(), usuario["id_usuario"])
    return {"id_paciente": id_paciente, "mensaje": "Paciente registrado correctamente."}

@router.put("/{id_paciente}")
def actualizar_paciente(
    id_paciente: int,
    body: PacienteBody,
    usuario: dict = Depends(get_usuario_actual),
):
    ok = editar_paciente(id_paciente, body.model_dump(), usuario["id_usuario"])
    if not ok:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")
    return {"mensaje": "Paciente actualizado correctamente."}


@router.delete("/{id_paciente}")
def eliminar_paciente(
    id_paciente: int,
    usuario: dict = Depends(require_rol("Administrador")),
):
    ok = desactivar_paciente(id_paciente, usuario["id_usuario"])
    if not ok:
        raise HTTPException(status_code=404, detail="Paciente no encontrado o ya inactivo.")
    return {"mensaje": "Paciente desactivado correctamente."}