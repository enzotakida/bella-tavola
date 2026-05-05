import pytest


@pytest.mark.parametrize("categoria_invalida", [
    "esoterico",
    "fastfood",
    "japonesa",
    "PIZZA",
    "massa extra",
])
@pytest.mark.validacao
def test_categoria_invalida_retorna_422(client, categoria_invalida):
    prato = {"nome": "Prato Teste", "categoria": categoria_invalida, "preco": 40.0}
    response = client.post("/pratos/", json=prato)
    assert response.status_code == 422


@pytest.mark.parametrize("id_inexistente", [9999, 123456, 99999])
def test_prato_inexistente_retorna_404(client, id_inexistente):
    response = client.get(f"/pratos/{id_inexistente}")
    assert response.status_code == 404


@pytest.mark.parametrize("categoria_valida", [
    "pizza",
    "massa",
    "sobremesa",
    "entrada",
    "salada",
])
def test_filtro_por_categoria_valida(client, categoria_valida):
    response = client.get(f"/pratos/?categoria={categoria_valida}")
    assert response.status_code == 200
    for prato in response.json():
        assert prato["categoria"] == categoria_valida


@pytest.mark.smoke
def test_listar_pratos_retorna_200_e_lista(client):
    response = client.get("/pratos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_filtrar_por_categoria_pizza(client):
    response = client.get("/pratos/?categoria=pizza")
    assert response.status_code == 200
    pratos = response.json()
    assert len(pratos) > 0
    assert all(p["categoria"] == "pizza" for p in pratos)

@pytest.mark.smoke
def test_buscar_prato_por_id_retorna_campos_esperados(client):
    response = client.get("/pratos/1")
    assert response.status_code == 200
    prato = response.json()
    assert "id" in prato
    assert "nome" in prato
    assert "preco" in prato

def test_buscar_prato_inexistente_retorna_404(client):
    response = client.get("/pratos/9999")
    assert response.status_code == 404

@pytest.mark.smoke
def test_criar_prato_valido_retorna_campos_esperados(client):
    novo_prato = {"nome": "Funghi Trifolati", "categoria": "massa", "preco": 54.0, "disponivel": True}
    response = client.post("/pratos/", json=novo_prato)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["nome"] == "Funghi Trifolati"
    assert "id" in data
    assert "preco" in data
    assert "categoria" in data

@pytest.mark.validacao
def test_criar_prato_com_preco_negativo_retorna_422(client):
    prato_invalido = {"nome": "Prato Inválido", "categoria": "pizza", "preco": -10.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

@pytest.mark.validacao
def test_criar_prato_com_nome_curto_retorna_422(client):
    prato_invalido = {"nome": "AB", "categoria": "pizza", "preco": 30.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

@pytest.mark.validacao
def test_criar_prato_com_categoria_invalida_retorna_422(client):
    prato_invalido = {"nome": "Prato Teste", "categoria": "lanche", "preco": 30.0}
    response = client.post("/pratos/", json=prato_invalido)
    assert response.status_code == 422

def test_prato_criado_aparece_na_listagem(client):
    novo_prato = {"nome": "Panna al Salmone", "categoria": "massa", "preco": 62.0, "disponivel": True}
    client.post("/pratos/", json=novo_prato)
    response = client.get("/pratos/")
    nomes = [p["nome"] for p in response.json()]
    assert "Panna al Salmone" in nomes

def test_criar_prato_com_fixture(client, prato_valido):
    response = client.post("/pratos/", json=prato_valido)
    assert response.status_code in [200, 201]
    assert response.json()["nome"] == prato_valido["nome"]

def test_quantidade_aumenta_ao_criar_prato(client, prato_valido):
    quantidade_antes = len(client.get("/pratos/").json())
    client.post("/pratos/", json=prato_valido)
    quantidade_depois = len(client.get("/pratos/").json())
    assert quantidade_depois == quantidade_antes + 1
