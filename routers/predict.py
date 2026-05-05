from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np

router = APIRouter()

REPO_ID = "Main921/mlops-analise-credito-v1"
FILENAME = "modelo_credito.pkl"
_model = None


def get_model():
    global _model
    if _model is None:
        from model_utils import load_model
        _model = load_model(REPO_ID, FILENAME)
    return _model


class PredictInput(BaseModel):
    renda_mensal: float = Field(gt=0, description="Renda mensal em reais")
    divida_atual: float = Field(ge=0, description="Dívida atual total em reais")
    score_pagamento: int = Field(ge=0, le=100, description="Score de pagamento (0-100)")
    idade: int = Field(ge=18, le=120, description="Idade do cliente em anos")
    num_dependentes: int = Field(ge=0, le=10, description="Número de dependentes")


class PredictOutput(BaseModel):
    prediction: int
    probability: float
    label: str
    model_version: str
    confidence: str


def _confidence_label(probability: float) -> str:
    if probability >= 0.85:
        return "MUITO ALTA"
    if probability >= 0.70:
        return "ALTA"
    if probability >= 0.55:
        return "MÉDIA"
    return "BAIXA"


@router.post("/predict", response_model=PredictOutput)
async def predict(input: PredictInput):
    model = get_model()

    features = np.array([[
        input.renda_mensal,
        input.divida_atual,
        input.score_pagamento,
        input.idade,
        input.num_dependentes
    ]])

    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])

    return PredictOutput(
        prediction=prediction,
        probability=round(probability, 4),
        label="INADIMPLENTE" if prediction == 1 else "BOM PAGADOR",
        model_version=REPO_ID,
        confidence=_confidence_label(probability)
    )


@router.get("/health")
async def health():
    try:
        model = get_model()
        model.predict(np.zeros((1, 5)))
        body = {"api": "ok", "model": "ok", "model_repo": REPO_ID, "detail": None}
        status_code = 200
    except Exception as e:
        body = {"api": "ok", "model": "degraded", "model_repo": REPO_ID, "detail": str(e)}
        status_code = 503

    return JSONResponse(content=body, status_code=status_code)
