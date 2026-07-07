def test_criar_cliente_sucesso(client, auth_headers):
    payload = {"nome": "Usuario", "telefone": "11987654321"}
    r = client.post("/clientes/", json=payload, headers=auth_headers)

    assert r.status_code == 200
    dado = r.get_json()
    assert dado["cliente"]["nome"] == payload["nome"]
    assert dado["cliente"]["telefone"] == payload["telefone"]
    assert "id" in dado


def test_criar_cliente_sem_nome(client, auth_headers):
    r = client.post("/clientes/", json={"telefone": "11987654321"}, headers=auth_headers)
    assert r.status_code == 400
    assert "nome" in r.get_json()["errors"]


def test_criar_cliente_telefone_invalido(client, auth_headers):
    r = client.post("/clientes/", json={"nome": "Usuario", "telefone": "123"}, headers=auth_headers)
    assert r.status_code == 400
    assert "telefone" in r.get_json()["errors"]


def test_criar_cliente_sem_telefone_e_permitido(client, auth_headers):
    r = client.post("/clientes/", json={"nome": "Usuario"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["cliente"]["telefone"] is None


def test_listar_clientes(client, auth_headers, cliente_id):
    r = client.get("/clientes/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.get_json()["clientes"]) == 1


def test_buscar_cliente_existente(client, auth_headers, cliente_id):
    r = client.get(f"/clientes/{cliente_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["id"] == cliente_id


def test_buscar_cliente_inexistente(client, auth_headers):
    r = client.get("/clientes/999", headers=auth_headers)
    assert r.status_code == 404


def test_atualizar_cliente_completo(client, auth_headers, cliente_id):
    payload = {"nome": "Giovanna", "telefone": "11912345678"}
    r = client.put(f"/clientes/{cliente_id}", json=payload, headers=auth_headers)

    assert r.status_code == 200
    assert r.get_json()["cliente"]["nome"] == payload["nome"]
    assert r.get_json()["cliente"]["telefone"] == payload["telefone"]


def test_atualizar_cliente_somente_nome(client, auth_headers, cliente_id):
    """Regressao: antes quebrava com KeyError se so 'nome' fosse enviado."""
    r = client.put(f"/clientes/{cliente_id}", json={"nome": "Novo Nome"}, headers=auth_headers)

    assert r.status_code == 200
    assert r.get_json()["cliente"]["nome"] == "Novo Nome"


def test_atualizar_cliente_inexistente(client, auth_headers):
    r = client.put("/clientes/999", json={"nome": "X"}, headers=auth_headers)
    assert r.status_code == 404


def test_deletar_cliente(client, auth_headers, cliente_id):
    r = client.delete(f"/clientes/{cliente_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.get(f"/clientes/{cliente_id}", headers=auth_headers)
    assert r.status_code == 404


def test_deletar_cliente_inexistente(client, auth_headers):
    r = client.delete("/clientes/999", headers=auth_headers)
    assert r.status_code == 404
