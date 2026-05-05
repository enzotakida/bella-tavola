from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ReservaInput(BaseModel):
    nome_cliente: str = Field(min_length=3, max_length=100)
    data: str = Field(pattern=r"^\d{2}-\d{2}-\d{4}$")
    horario: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    numero_pessoas: int = Field(ge=1, le=20)
    telefone: Optional[str] = Field(default=None, pattern=r"^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$")
    observacao: Optional[str] = Field(default=None, max_length=500)

    @field_validator("data")
    @classmethod
    def validar_data(cls, v):
        from datetime import date
        dia, mes, ano = map(int, v.split("-"))
        data_reserva = date(ano, mes, dia)
        if data_reserva < date.today():
            raise ValueError("A data da reserva não pode ser no passado")
        return v

class ReservaOutput(BaseModel):
    id: int
    nome_cliente: str
    data: str
    horario: str
    numero_pessoas: int
    telefone: Optional[str]
    observacao: Optional[str]
    status: str
    criado_em: str

class StatusReservaInput(BaseModel):
    status: str = Field(pattern="^(confirmada|cancelada|pendente)$")
