from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_listar_pratos_retorna_200_e_lista():
    response = client.get("/pratos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_filtrar_por_categoria_pizza():
    response = client.get("/pratos/?categoria=pizza")
    assert response.status_code == 200
    pratos = response.json()
    assert len(pratos) > 0
    assert all(p["categoria"] == "pizza" for p in pratos)

def test_buscar_prato_por_id_retorna_campos_esperados():
    response = client.get("/pratos/1")
    assert response.status_code == 200
    prato = response.json()
    assert "id" in prato
    assert "nome" in prato
    assert "preco" in prato

def test_buscar_prato_inexistente_retorna_404():
    response = client.get("/pratos/9999")
    assert response.status_code == 404

def test_criar_prato_valido_retorna_campos_esperados():
    novo_prato = {"nome": "Funghi Trifolati", "categoria": "massa", "preco": 54.0, "disponivel": True}
    response = client.post("/pratos/", json=novo_prato)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["nome"] == "Funghi Trifolati"
    assert "id" in data
    assert "preco" in data
    assert "categoria" in data

def test_criar_prato_com_preco_negativo_retorna_422():
    prato_invalido = {"nome": "Prato Inválido", "categoria": "pizza", "preco": -10.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

def test_criar_prato_com_nome_curto_retorna_422():
    prato_invalido = {"nome": "AB", "categoria": "pizza", "preco": 30.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

def test_criar_prato_com_categoria_invalida_retorna_422():
    prato_invalido = {"nome": "Prato Teste", "categoria": "lanche", "preco": 30.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

def test_prato_criado_aparece_na_listagem():
    novo_prato = {"nome": "Panna al Salmone", "categoria": "massa", "preco": 62.0, "disponivel": True}
    client.post("/pratos/", json=novo_prato)
    response = client.get("/pratos/")
    nomes = [p["nome"] for p in response.json()]
    assert "Panna al Salmone" in nomes
