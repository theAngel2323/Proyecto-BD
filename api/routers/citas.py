from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import Depends

from api.dependencies import get_usuario_actual
from app.modules.citas import (
    agendar_cita, cancelar_cita, completar_cita,
    citas_por_medico, citas_por_fecha,
)

router = APIRouter()


class CitaBody(BaseModel):
    fecha_hora:  datetime
    motivo:      Optional[str] = None
    id_paciente: int
    id_medico:   int
    id_area:     int


# ---- GET /api/citas?fecha=2026-06-01 ----
@router.get("/")
def listar_citas(
    fecha:     Optional[str] = Query(default=None, description="Formato YYYY-MM-DD"),
    id_medico: Optional[int] = Query(default=None),
    solo_pendientes: bool = Query(default=False),
    usuario: dict = Depends(get_usuario_actual),
):
    if fecha:
        return citas_por_fecha(fecha)
    if id_medico:
        return citas_por_medico(id_medico, solo_pendientes)
    return {"detalle": "Especifica ?fecha=YYYY-MM-DD o ?id_medico=N"}


# ---- POST /api/citas ----
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_cita(
    body: CitaBody,
    usuario: dict = Depends(get_usuario_actual),
):
    try:
        id_cita = agendar_cita(body.model_dump(), usuario["id_usuario"])
        return {"id_cita": id_cita, "mensaje": "Cita agendada correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- PATCH /api/citas/{id}/cancelar ----
@router.patch("/{id_cita}/cancelar")
def cancelar(
    id_cita: int,
    usuario: dict = Depends(get_usuario_actual),
):
    ok = cancelar_cita(id_cita, usuario["id_usuario"])
    if not ok:
        raise HTTPException(status_code=404, detail="Cita no encontrada o no está Pendiente.")
    return {"mensaje": "Cita cancelada correctamente."}


# ---- PATCH /api/citas/{id}/completar ----
@router.patch("/{id_cita}/completar")
def completar(
    id_cita: int,
    usuario: dict = Depends(get_usuario_actual),
):
    ok = completar_cita(id_cita, usuario["id_usuario"])
    if not ok:
        raise HTTPException(status_code=404, detail="Cita no encontrada o no está Pendiente.")
    return {"mensaje": "Cita completada correctamente."}