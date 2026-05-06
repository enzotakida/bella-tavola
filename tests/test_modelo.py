import pytest
import numpy as np

REPO_ID = "Main921/mlops-analise-credito-v1"

PAYLOAD_VALIDO = {
    "renda_mensal": 5000.0,
    "divida_atual": 1000.0,
    "score_pagamento": 75,
    "idade": 35,
    "num_dependentes": 2,
}


@pytest.fixture(scope="module")
def modelo():
    from model_utils import load_model

    return load_model(REPO_ID)


@pytest.fixture
def amostra_valida():
    return np.array([[5000.0, 1000.0, 75, 35, 2]])


# --- Exercício 5.2: testes do modelo ---


@pytest.mark.integracao
def test_modelo_carregado_nao_e_none(modelo):
    assert modelo is not None


@pytest.mark.integracao
def test_modelo_tem_metodo_predict(modelo):
    assert hasattr(modelo, "predict")
    assert callable(modelo.predict)


@pytest.mark.integracao
def test_modelo_tem_metodo_predict_proba(modelo):
    assert hasattr(modelo, "predict_proba")
    assert callable(modelo.predict_proba)


@pytest.mark.integracao
def test_predict_retorna_array_com_formato_correto(modelo, amostra_valida):
    resultado = modelo.predict(amostra_valida)
    assert resultado.shape == (1,)
    assert resultado[0] in [0, 1]


@pytest.mark.integracao
def test_predict_proba_retorna_probabilidades_validas(modelo, amostra_valida):
    probas = modelo.predict_proba(amostra_valida)
    assert probas.shape == (1, 2)
    assert abs(probas[0].sum() - 1.0) < 1e-6
    assert all(0 <= p <= 1 for p in probas[0])


# --- Exercício 5.3: testes do endpoint /ml/predict ---


@pytest.mark.integracao
def test_predict_retorna_200(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    assert response.status_code == 200


@pytest.mark.integracao
def test_predict_retorna_campos_esperados(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    dados = response.json()
    assert "prediction" in dados
    assert "probability" in dados
    assert "label" in dados
    assert "model_version" in dados


@pytest.mark.integracao
def test_predict_prediction_e_binario(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    prediction = response.json()["prediction"]
    assert prediction in [0, 1]


@pytest.mark.integracao
def test_predict_probability_entre_zero_e_um(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    probability = response.json()["probability"]
    assert isinstance(probability, float)
    assert 0.0 <= probability <= 1.0


@pytest.mark.integracao
def test_predict_label_e_string_nao_vazia(client):
    response = client.post("/ml/predict", json=PAYLOAD_VALIDO)
    label = response.json()["label"]
    assert isinstance(label, str)
    assert len(label) > 0


@pytest.mark.integracao
def test_predict_sem_campo_obrigatorio_retorna_422(client):
    payload_incompleto = {"renda_mensal": 5000.0}
    response = client.post("/ml/predict", json=payload_incompleto)
    assert response.status_code == 422


@pytest.mark.integracao
@pytest.mark.parametrize(
    "campo,valor_invalido",
    [
        ("score_pagamento", 101),
        ("score_pagamento", -1),
        ("idade", 17),
        ("renda_mensal", -100.0),
        ("num_dependentes", -1),
    ],
)
def test_predict_campo_invalido_retorna_422(client, campo, valor_invalido):
    payload = {**PAYLOAD_VALIDO, campo: valor_invalido}
    response = client.post("/ml/predict", json=payload)
    assert response.status_code == 422
