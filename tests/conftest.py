import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def prato_valido():
    """Payload de prato válido para reutilizar nos testes."""
    return {
        "nome": "Prato de Fixture",
        "categoria": "massa",
        "preco": 45.0,
        "disponivel": True,
    }
