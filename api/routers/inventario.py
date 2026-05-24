from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends

from api.dependencies import get_usuario_actual, require_rol
from app.modules.inventario import (
    registrar_entrada, stock_critico,
    historial_movimientos, listar_medicamentos,
)

router = APIRouter()


class EntradaBody(BaseModel):
    id_medicamento: int
    cantidad:       int
    motivo:         Optional[str] = "Reposición de stock"


# ---- GET /api/inventario ----
@router.get("/")
def listar(
    solo_disponibles: bool = Query(default=False),
    usuario: dict = Depends(get_usuario_actual),
):
    return listar_medicamentos(solo_disponibles)


# ---- GET /api/inventario/stock-critico ----
@router.get("/stock-critico")
def ver_stock_critico(usuario: dict = Depends(get_usuario_actual)):
    """Medicamentos con stock igual o menor al mínimo — útil para alertas en dashboard."""
    return stock_critico()


# ---- GET /api/inventario/{id}/movimientos ----
@router.get("/{id_medicamento}/movimientos")
def ver_movimientos(
    id_medicamento: int,
    limite: int = Query(default=50),
    usuario: dict = Depends(get_usuario_actual),
):
    return historial_movimientos(id_medicamento, limite)


# ---- POST /api/inventario/entrada ----
@router.post("/entrada", status_code=status.HTTP_201_CREATED)
def entrada_stock(
    body: EntradaBody,
    usuario: dict = Depends(require_rol("Administrador")),
):
    try:
        id_mov = registrar_entrada(
            body.id_medicamento, body.cantidad,
            body.motivo, usuario["id_usuario"]
        )
        return {"id_movimiento": id_mov, "mensaje": "Entrada registrada correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))