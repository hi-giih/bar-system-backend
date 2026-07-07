def test_criar_comanda_sucesso(client, auth_headers, cliente_id):
    payload = {"data": "2026-07-06", "cliente_id": cliente_id}
    r = client.post("/comanda/", json=payload, headers=auth_headers)

    assert r.status_code == 200
    dado = r.get_json()
    assert dado["cliente_id"] == cliente_id
    assert dado["produtos"] == []
    assert dado["total"] == 0
    assert dado["fechada"] is False
    assert dado["colapsada"] is False


def test_criar_comanda_cliente_inexistente(client, auth_headers):
    r = client.post("/comanda/", json={"data": "2026-07-06", "cliente_id": 999}, headers=auth_headers)
    assert r.status_code == 404


def test_criar_comanda_data_formato_invalido(client, auth_headers, cliente_id):
    r = client.post(
        "/comanda/", json={"data": "06-07-2026", "cliente_id": cliente_id}, headers=auth_headers
    )
    assert r.status_code == 400
    assert "data" in r.get_json()["errors"]


def test_listar_comandas(client, auth_headers, comanda_id):
    r = client.get("/comanda/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.get_json()["comandas"]) == 1


def test_buscar_comanda_inexistente(client, auth_headers):
    r = client.get("/comanda/999", headers=auth_headers)
    assert r.status_code == 404


def test_atualizar_comanda_data(client, auth_headers, comanda_id):
    r = client.put(f"/comanda/{comanda_id}", json={"data": "2026-08-01"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["comanda"]["data"] == "2026-08-01"


def test_atualizar_comanda_cliente_inexistente(client, auth_headers, comanda_id):
    r = client.put(f"/comanda/{comanda_id}", json={"cliente_id": 999}, headers=auth_headers)
    assert r.status_code == 404


def test_adicionar_produto_sucesso(client, auth_headers, comanda_id, produto_id):
    r = client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 3},
        headers=auth_headers,
    )
    assert r.status_code == 200
    dado = r.get_json()["comanda"]
    assert dado["produtos"][0]["quantidade"] == 3
    assert dado["total"] == 30.0  # produto_id fixture custa 10.0


def test_adicionar_produto_inexistente(client, auth_headers, comanda_id):
    r = client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": 999, "quantidade": 1},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_adicionar_produto_quantidade_invalida(client, auth_headers, comanda_id, produto_id):
    r = client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 0},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_incrementar_quantidade_soma_ao_existente(client, auth_headers, comanda_id, produto_id):
    """PATCH soma a quantidade extra ao que ja existe (pedido adicional do
    mesmo produto), nao substitui o total."""
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 4},
        headers=auth_headers,
    )
    r = client.patch(
        f"/comanda/{comanda_id}/produtos/{produto_id}",
        json={"quantidade": 1},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["comanda"]["produtos"][0]["quantidade"] == 5


def test_incrementar_produto_nao_na_comanda(client, auth_headers, comanda_id, produto_id):
    r = client.patch(
        f"/comanda/{comanda_id}/produtos/{produto_id}",
        json={"quantidade": 1},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_remover_produto_parcial(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 5},
        headers=auth_headers,
    )
    r = client.delete(
        f"/comanda/{comanda_id}/produtos/{produto_id}",
        json={"quantidade": 2},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["comanda"]["produtos"][0]["quantidade"] == 3


def test_remover_produto_total(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 2},
        headers=auth_headers,
    )
    r = client.delete(
        f"/comanda/{comanda_id}/produtos/{produto_id}",
        json={"quantidade": 5},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["comanda"]["produtos"] == []


def test_deletar_comanda(client, auth_headers, comanda_id):
    r = client.delete(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.status_code == 404


# --- Fechamento da comanda ---

def test_fechar_comanda_com_saldo_pendente(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 1},
        headers=auth_headers,
    )
    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 400


def test_fechar_comanda_saldo_zero(client, auth_headers, comanda_id):
    """Comanda sem nenhum produto ja tem saldo zero, pode ser fechada."""
    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200
    assert r.get_json()["comanda"]["fechada"] is True


def test_fechar_comanda_ja_fechada(client, auth_headers, comanda_id):
    client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 400


def test_editar_comanda_fechada_bloqueado(client, auth_headers, comanda_id):
    client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    r = client.put(f"/comanda/{comanda_id}", json={"data": "2026-09-01"}, headers=auth_headers)
    assert r.status_code == 400


def test_adicionar_produto_comanda_fechada_bloqueado(client, auth_headers, comanda_id, produto_id):
    client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    r = client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 1},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_remover_produto_comanda_fechada_bloqueado(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 1},
        headers=auth_headers,
    )
    # produto_id fixture custa 10.0, precisa pagar antes de poder fechar
    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 10.0}, headers=auth_headers)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 10.0}, headers=auth_headers
    )

    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200

    r = client.delete(
        f"/comanda/{comanda_id}/produtos/{produto_id}",
        json={"quantidade": 1},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_deletar_comanda_fechada_e_permitido(client, auth_headers, comanda_id):
    client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    r = client.delete(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.status_code == 200
