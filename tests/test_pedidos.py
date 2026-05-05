def test_criar_pedido_valido_retorna_campos_esperados(client):
    pedido = {"prato_id": 1, "quantidade": 2}
    response = client.post("/pedidos/", json=pedido)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["prato_id"] == 1
    assert data["quantidade"] == 2
    assert "valor_total" in data
    assert "nome_prato" in data

def test_criar_pedido_calcula_valor_total_corretamente(client):
    pedido = {"prato_id": 1, "quantidade": 3}
    response = client.post("/pedidos/", json=pedido)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["valor_total"] == 45.0 * 3

def test_criar_pedido_com_quantidade_zero_retorna_422(client):
    pedido_invalido = {"prato_id": 1, "quantidade": 0}
    response = client.post("/pedidos/", json=pedido_invalido)
    assert response.status_code == 422

def test_criar_pedido_com_quantidade_negativa_retorna_422(client):
    pedido_invalido = {"prato_id": 1, "quantidade": -1}
    response = client.post("/pedidos/", json=pedido_invalido)
    assert response.status_code == 422

def test_criar_pedido_com_prato_inexistente_retorna_404(client):
    pedido_invalido = {"prato_id": 9999, "quantidade": 1}
    response = client.post("/pedidos/", json=pedido_invalido)
    assert response.status_code == 404

def test_criar_pedido_com_prato_indisponivel_retorna_400(client):
    pedido = {"prato_id": 3, "quantidade": 1}
    response = client.post("/pedidos/", json=pedido)
    assert response.status_code == 400

def test_pedido_criado_preserva_observacao(client):
    pedido = {"prato_id": 2, "quantidade": 1, "observacao": "sem cebola"}
    response = client.post("/pedidos/", json=pedido)
    assert response.status_code in [200, 201]
    assert response.json()["observacao"] == "sem cebola"
