from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from models.prato import PratoInput, PratoOutput, DisponibilidadeInput
from database import pratos_db

router = APIRouter(prefix="/pratos", tags=["Pratos"])


@router.get("/")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False,
):
    resultado = pratos_db
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado


@router.get("/{prato_id}")
async def buscar_prato(prato_id: int, formato: str = "completo"):
    for prato in pratos_db:
        if prato["id"] == prato_id:
            if formato == "resumido":
                return {"nome": prato["nome"], "preco": prato["preco"]}
            return prato
    raise HTTPException(
        status_code=404, detail=f"Prato com ID {prato_id} não encontrado"
    )


@router.get("/{prato_id}/detalhes")
async def detalhes_prato(prato_id: int, incluir_ingredientes: bool = False):
    for prato in pratos_db:
        if prato["id"] == prato_id:
            if incluir_ingredientes:
                return {
                    **prato,
                    "ingredientes": {
                        1: [
                            "Massa de pizza artesanal",
                            "Molho de tomate",
                            "Mussarela de búfala",
                            "Manjericão fresco",
                            "Azeite extra virgem",
                        ],
                        2: [
                            "Espaguete grano duro",
                            "Pancetta curada",
                            "Gemas de ovo",
                            "Queijo parmessao",
                            "Pimenta preta moída",
                        ],
                        3: [
                            "Massa fresca de lasanha",
                            "Ragù à bolonhesa (carne bovina e suína)",
                            "Molho bechamel",
                            "Queijo",
                        ],
                        4: [
                            "Biscoito champanhe",
                            "Café",
                            "Queijo mascarpone",
                            "Cacau em pó",
                            "licor",
                        ],
                        5: [
                            "Massa de pizza artesanal",
                            "Molho de tomate",
                            "Mussarela",
                            "Alcachofrinhas",
                            "Presunto cozido",
                            "Cogumelos frescos",
                            "Azeitonas pretas",
                        ],
                        6: [
                            "Creme de leite fresco",
                            "Açúcar",
                            "Fava de baunilha",
                            "Gelatina",
                            "Calda artesanal de frutas vermelhas",
                        ],
                    }.get(prato_id, ["Ingredientes não encontrados"]),
                }
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")


@router.post("/", response_model=PratoOutput)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos_db) + 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump(),
    }
    pratos_db.append(novo_prato)
    return novo_prato


@router.post("/{prato_id}/aplicar_desconto")
async def aplicar_desconto(prato_id: int, percentual: float):
    prato = next((p for p in pratos_db if p["id"] == prato_id), None)
    if not prato:
        raise HTTPException(
            status_code=404, detail=f"Prato com ID {prato_id} não encontrado"
        )

    if percentual <= 0 or percentual > 50:
        raise HTTPException(
            status_code=400, detail="Percentual de desconto deve estar entre 1% e 50%"
        )

    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível aplicar desconto em prato indisponível",
        )

    prato["preco"] = prato["preco"] * (1 - percentual / 100)
    return prato


@router.put("/{prato_id}/disponibilidade")
async def alterar_disponibilidade(prato_id: int, body: DisponibilidadeInput):
    for prato in pratos_db:
        if prato["id"] == prato_id:
            prato["disponivel"] = body.disponivel
            return prato
    raise HTTPException(status_code=404, detail="Prato não encontrado")
