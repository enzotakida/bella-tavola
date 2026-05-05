from fastapi.testclient import TestClient
from main import app  # Certifique-se de que 'app' é o nome da sua instância FastAPI

client = TestClient(app)

def test_listar_pratos_retorna_200():
    response = client.get("/pratos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)