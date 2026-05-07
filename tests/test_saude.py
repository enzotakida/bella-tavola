import pytest


def test_pytest_funcionando():
    """Confirma que o pytest encontrou e executou este arquivo."""
    assert 1 + 1 == 2


@pytest.mark.smoke
def test_health_api_ok(client):
    """Endpoint /ml/health deve responder com api: ok."""
    response = client.get("/ml/health")
    assert response.status_code in (200, 503)
    body = response.json()
    assert body["api"] == "ok"
    assert "model" in body
    assert "model_repo" in body


@pytest.mark.integracao
def test_health_model_ok(client):
    """Com acesso ao HF, o modelo deve carregar e responder com model: ok."""
    response = client.get("/ml/health")
    body = response.json()
    assert response.status_code == 200, (
        f"Modelo degradado — detalhe: {body.get('detail')}"
    )
    assert body["model"] == "ok"
    assert body["model_repo"] == "Main921/mlops-analise-credito-v1"
