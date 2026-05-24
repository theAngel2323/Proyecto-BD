from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends

from api.dependencies import get_usuario_actual
from app.modules.prescripciones import (
    registrar_diagnostico, prescribir_medicamento,
    diagnosticos_por_cita, medicamentos_mas_prescritos,
)

router = APIRouter()


class DiagnosticoBody(BaseModel):
    codigo_cie10: Optional[str] = None
    descripcion:  str
    id_cita:      int
    id_medico:    int


class PrescripcionBody(BaseModel):
    id_diagnostico:      int
    id_medico:           int
    id_medicamento:      int
    dosis:               str
    frecuencia:          str
    duracion_dias:       int
    cantidad_dispensada: int = 1


# ---- POST /api/prescripciones/diagnostico ----
@router.post("/diagnostico", status_code=status.HTTP_201_CREATED)
def crear_diagnostico(
    body: DiagnosticoBody,
    usuario: dict = Depends(get_usuario_actual),
):
    id_diag = registrar_diagnostico(body.model_dump(), usuario["id_usuario"])
    return {"id_diagnostico": id_diag, "mensaje": "Diagnóstico registrado correctamente."}


# ---- POST /api/prescripciones ----
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_prescripcion(
    body: PrescripcionBody,
    usuario: dict = Depends(get_usuario_actual),
):
    try:
        resultado = prescribir_medicamento(body.model_dump(), usuario["id_usuario"])
        return {**resultado, "mensaje": "Prescripción registrada y stock actualizado."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---- GET /api/prescripciones/cita/{id} ----
@router.get("/cita/{id_cita}")
def diagnosticos_cita(
    id_cita: int,
    usuario: dict = Depends(get_usuario_actual),
):
    return diagnosticos_por_cita(id_cita)


# ---- GET /api/prescripciones/top-medicamentos ----
@router.get("/top-medicamentos")
def top_medicamentos(
    limite: int = 10,
    usuario: dict = Depends(get_usuario_actual),
):
    return medicamentos_mas_prescritos(limite)