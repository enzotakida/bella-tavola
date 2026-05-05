from fastapi import APIRouter
from typing import Optional
from datetime import datetime
from models.reserva import ReservaInput, ReservaOutput
from database import reservas_db

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.get("/")
async def listar_reservas(data: Optional[str] = None):
    if data:
        return [r for r in reservas_db if r["data"] == data]
    return reservas_db

@router.post("/", response_model=ReservaOutput)
async def criar_reserva(reserva: ReservaInput):
    novo_id = len(reservas_db) + 1
    nova_reserva = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        "status": "pendente",
        **reserva.model_dump()
    }
    reservas_db.append(nova_reserva)
    return nova_reserva
