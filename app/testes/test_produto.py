def test_criar_produto_sucesso(client, auth_headers):
    payload = {"nome": "Agua", "preco": 1.10}
    r = client.post("/produtos/", json=payload, headers=auth_headers)

    assert r.status_code == 200
    dado = r.get_json()
    assert dado["produto"]["nome"] == payload["nome"]
    assert dado["produto"]["preco"] == payload["preco"]
    assert "id" in dado


def test_criar_produto_preco_como_string_numerica(client, auth_headers):
    """Marshmallow converte string numerica para float automaticamente."""
    r = client.post("/produtos/", json={"nome": "Agua", "preco": "1.10"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["produto"]["preco"] == 1.10


def test_criar_produto_preco_negativo(client, auth_headers):
    r = client.post("/produtos/", json={"nome": "Agua", "preco": -5}, headers=auth_headers)
    assert r.status_code == 400
    assert "preco" in r.get_json()["errors"]


def test_criar_produto_preco_nao_numerico(client, auth_headers):
    r = client.post("/produtos/", json={"nome": "Agua", "preco": "abc"}, headers=auth_headers)
    assert r.status_code == 400
    assert "preco" in r.get_json()["errors"]


def test_criar_produto_sem_nome(client, auth_headers):
    r = client.post("/produtos/", json={"preco": 5}, headers=auth_headers)
    assert r.status_code == 400
    assert "nome" in r.get_json()["errors"]


def test_listar_produtos(client, auth_headers, produto_id):
    r = client.get("/produtos/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.get_json()["produtos"]) == 1


def test_buscar_produto_existente(client, auth_headers, produto_id):
    r = client.get(f"/produtos/{produto_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == produto_id


def test_buscar_produto_inexistente(client, auth_headers):
    r = client.get("/produtos/999", headers=auth_headers)
    assert r.status_code == 404


def test_atualizar_produto_completo(client, auth_headers, produto_id):
    payload = {"nome": "Cerveja", "preco": 10.0}
    r = client.put(f"/produtos/{produto_id}", json=payload, headers=auth_headers)

    assert r.status_code == 200
    assert r.get_json()["produto"]["nome"] == payload["nome"]
    assert r.get_json()["produto"]["preco"] == payload["preco"]


def test_atualizar_produto_somente_preco(client, auth_headers, produto_id):
    r = client.put(f"/produtos/{produto_id}", json={"preco": 99.9}, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["produto"]["preco"] == 99.9


def test_atualizar_produto_inexistente(client, auth_headers):
    r = client.put("/produtos/999", json={"preco": 5}, headers=auth_headers)
    assert r.status_code == 404


def test_deletar_produto(client, auth_headers, produto_id):
    r = client.delete(f"/produtos/{produto_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.get(f"/produtos/{produto_id}", headers=auth_headers)
    assert r.status_code == 404


def test_deletar_produto_inexistente(client, auth_headers):
    r = client.delete("/produtos/999", headers=auth_headers)
    assert r.status_code == 404
