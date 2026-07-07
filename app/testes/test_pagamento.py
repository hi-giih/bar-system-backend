def _adiciona_produto(client, auth_headers, comanda_id, produto_id, quantidade):
    return client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": quantidade},
        headers=auth_headers,
    )


def test_criar_pagamento_sucesso(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30

    r = client.post(
        "/pagamento/", json={"comanda_id": comanda_id, "valor": 30}, headers=auth_headers
    )
    assert r.status_code == 200
    dado = r.get_json()["pagamento"]
    assert dado["paid"] is False
    assert dado["qr_code"] is not None
    assert dado["bank_payment_id"] is not None


def test_criar_pagamento_comanda_inexistente(client, auth_headers):
    r = client.post("/pagamento/", json={"comanda_id": 999, "valor": 10}, headers=auth_headers)
    assert r.status_code == 404


def test_criar_pagamento_valor_negativo(client, auth_headers, comanda_id):
    r = client.post(
        "/pagamento/", json={"comanda_id": comanda_id, "valor": -10}, headers=auth_headers
    )
    assert r.status_code == 400


def test_qrcode_gerado_pode_ser_baixado(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 1)
    r = client.post(
        "/pagamento/", json={"comanda_id": comanda_id, "valor": 10}, headers=auth_headers
    )
    qr_code = r.get_json()["pagamento"]["qr_code"]

    r = client.get(f"/pagamento/pix/qrcode/{qr_code}", headers=auth_headers)
    assert r.status_code == 200
    assert r.content_type == "image/png"


def test_qrcode_path_traversal_bloqueado(client, auth_headers):
    r = client.get("/pagamento/pix/qrcode/..%2f..%2f..%2fetc%2fpasswd", headers=auth_headers)
    assert r.status_code == 404


def test_confirmar_pagamento_inexistente(client, auth_headers, comanda_id):
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 999}, headers=auth_headers
    )
    assert r.status_code == 404


def test_confirmar_pagamento_total(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30
    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 30}, headers=auth_headers)

    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 30}, headers=auth_headers
    )
    assert r.status_code == 200
    dado = r.get_json()
    assert dado["total_comanda"] == 30.0
    assert dado["total_pago"] == 30.0
    assert dado["saldo_restante"] == 0.0

    # com saldo zerado, a comanda pode ser fechada
    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200


def test_pagamento_parcial_colapsa_comanda(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100

    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers)
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )
    assert r.status_code == 200
    assert r.get_json()["saldo_restante"] == 60.0

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado = r.get_json()
    assert dado["colapsada"] is True
    assert dado["total"] == 60.0
    assert dado["produtos"] == [
        {"produto_id": None, "nome": "Saldo restante", "preco": 60.0, "quantidade": 1, "subtotal": 60.0}
    ]

    # comanda colapsada nao pode ser fechada com saldo pendente
    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 400


def test_pagamento_parcial_produto_adicionado_depois_soma_ao_saldo(
    client, auth_headers, comanda_id, produto_id
):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100
    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )

    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 2)  # +20

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.get_json()["total"] == 80.0  # 60 (saldo) + 20 (novo produto)


def test_pagamento_parcial_ate_saldo_zero_permite_fechar(
    client, auth_headers, comanda_id, produto_id
):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100
    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )

    client.post("/pagamento/", json={"comanda_id": comanda_id, "valor": 60}, headers=auth_headers)
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 60}, headers=auth_headers
    )
    assert r.get_json()["saldo_restante"] == 0.0

    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200
