from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends

from api.dependencies import get_usuario_actual
from app.modules.ingresos import (
    registrar_ingreso, registrar_egreso,
    ingresos_activos, ocupacion_por_area,
)

router = APIRouter()


class IngresoBody(BaseModel):
    id_paciente:    int
    id_medico:      int
    id_area:        int
    motivo_ingreso: Optional[str] = None


# ---- GET /api/ingresos ----
@router.get("/")
def listar_ingresos(
    id_area: Optional[int] = Query(default=None),
    usuario: dict = Depends(get_usuario_actual),
):
    return ingresos_activos(id_area)


# ---- GET /api/ingresos/ocupacion ----
@router.get("/ocupacion")
def ver_ocupacion(usuario: dict = Depends(get_usuario_actual)):
    """Tasa de ocupación por área — campo calculado para dashboards."""
    return ocupacion_por_area()


# ---- POST /api/ingresos ----
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_ingreso(
    body: IngresoBody,
    usuario: dict = Depends(get_usuario_actual),
):
    try:
        id_ingreso = registrar_ingreso(body.model_dump(), usuario["id_usuario"])
        return {"id_ingreso": id_ingreso, "mensaje": "Ingreso registrado correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- PATCH /api/ingresos/{id}/egreso ----
@router.patch("/{id_ingreso}/egreso")
def dar_egreso(
    id_ingreso: int,
    usuario: dict = Depends(get_usuario_actual),
):
    ok = registrar_egreso(id_ingreso, usuario["id_usuario"])
    if not ok:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado o ya cerrado.")
    return {"mensaje": "Egreso registrado correctamente."}