def _adiciona_produto(client, auth_headers, comanda_id, produto_id, quantidade):
    return client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": quantidade},
        headers=auth_headers,
    )


def _criar_pagamento_pix(client, auth_headers, comanda_id, valor):
    return client.post(
        "/pagamento/",
        json={"comanda_id": comanda_id, "valor": valor, "forma_pagamento": "pix"},
        headers=auth_headers,
    )


def test_criar_pagamento_sucesso(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30

    r = _criar_pagamento_pix(client, auth_headers, comanda_id, 30)
    assert r.status_code == 200
    dado = r.get_json()["pagamento"]
    assert dado["paid"] is False
    # QR code e gerado em memoria (data URI base64), nao gravado em disco.
    assert dado["qr_code"].startswith("data:image/png;base64,")
    assert dado["bank_payment_id"] is not None


def test_criar_pagamento_comanda_inexistente(client, auth_headers):
    r = _criar_pagamento_pix(client, auth_headers, 999, 10)
    assert r.status_code == 404


def test_criar_pagamento_valor_negativo(client, auth_headers, comanda_id):
    r = _criar_pagamento_pix(client, auth_headers, comanda_id, -10)
    assert r.status_code == 400


def test_criar_pagamento_forma_pagamento_invalida(client, auth_headers, comanda_id):
    r = client.post(
        "/pagamento/",
        json={"comanda_id": comanda_id, "valor": 10, "forma_pagamento": "boleto"},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_criar_pagamento_cartao_ja_nasce_pago_sem_qrcode(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30

    r = client.post(
        "/pagamento/",
        json={"comanda_id": comanda_id, "valor": 30, "forma_pagamento": "cartao"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    dado = r.get_json()
    assert dado["pagamento"]["paid"] is True
    assert dado["pagamento"]["qr_code"] is None
    assert dado["pagamento"]["bank_payment_id"] is None
    assert dado["saldo_restante"] == 0.0

    # ja fica refletido na comanda sem precisar de confirmacao separada
    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado_comanda = r.get_json()
    assert dado_comanda["total"] == 0.0
    assert dado_comanda["forma_pagamento"] == "cartao"

    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200


def test_forma_pagamento_reflete_ultimo_pagamento_confirmado(
    client, auth_headers, comanda_id, produto_id
):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.get_json()["forma_pagamento"] is None  # nada pago ainda

    _criar_pagamento_pix(client, auth_headers, comanda_id, 40)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )
    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.get_json()["forma_pagamento"] == "pix"

    client.post(
        "/pagamento/",
        json={"comanda_id": comanda_id, "valor": 60, "forma_pagamento": "dinheiro"},
        headers=auth_headers,
    )
    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.get_json()["forma_pagamento"] == "dinheiro"


def test_criar_pagamento_dinheiro_parcial(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100

    r = client.post(
        "/pagamento/",
        json={"comanda_id": comanda_id, "valor": 40, "forma_pagamento": "dinheiro"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.get_json()["saldo_restante"] == 60.0

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    assert r.get_json()["total"] == 60.0


def test_confirmar_pagamento_inexistente(client, auth_headers, comanda_id):
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 999}, headers=auth_headers
    )
    assert r.status_code == 404


def test_confirmar_pagamento_total(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30
    _criar_pagamento_pix(client, auth_headers, comanda_id, 30)

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


def test_confirmar_pagamento_total_colapsa_comanda(client, auth_headers, comanda_id, produto_id):
    """Pagar o valor cheio de uma unica vez (o caso mais comum) tambem deve
    colapsar a comanda, senao o total devolvido por GET fica desatualizado."""
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 3)  # total = 30
    _criar_pagamento_pix(client, auth_headers, comanda_id, 30)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 30}, headers=auth_headers
    )

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado = r.get_json()
    assert dado["colapsada"] is True
    assert dado["total"] == 0.0
    assert dado["valor_original"] == 30.0


def test_comanda_fechada_mostra_produtos_reais_nao_colapsados(
    client, auth_headers, comanda_id, produto_id
):
    """Enquanto aberta, a comanda paga colapsa para 'Saldo restante'. Uma vez
    fechada, nao ha mais saldo a esconder: a tela mostra os itens reais
    (somente leitura, edicao ja e bloqueada por comanda.fechada)."""
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 5)  # total = 50
    _criar_pagamento_pix(client, auth_headers, comanda_id, 50)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 50}, headers=auth_headers
    )
    client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado = r.get_json()
    assert dado["fechada"] is True
    assert dado["total"] == 50.0
    assert dado["valor_original"] == 50.0
    assert dado["produtos"] == [
        {"produto_id": produto_id, "nome": "Produto Teste", "preco": 10.0, "quantidade": 5, "subtotal": 50.0}
    ]


def test_pagamento_parcial_colapsa_comanda(client, auth_headers, comanda_id, produto_id):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100

    _criar_pagamento_pix(client, auth_headers, comanda_id, 40)
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )
    assert r.status_code == 200
    assert r.get_json()["saldo_restante"] == 60.0

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado = r.get_json()
    assert dado["colapsada"] is True
    assert dado["total"] == 60.0
    assert dado["valor_original"] == 100.0
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
    _criar_pagamento_pix(client, auth_headers, comanda_id, 40)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )

    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 2)  # +20

    r = client.get(f"/comanda/{comanda_id}", headers=auth_headers)
    dado = r.get_json()
    assert dado["total"] == 80.0  # 60 (saldo) + 20 (novo produto)
    assert dado["valor_original"] == 120.0  # 100 (original) + 20 (novo produto)


def test_pagamento_parcial_ate_saldo_zero_permite_fechar(
    client, auth_headers, comanda_id, produto_id
):
    _adiciona_produto(client, auth_headers, comanda_id, produto_id, 10)  # total = 100
    _criar_pagamento_pix(client, auth_headers, comanda_id, 40)
    client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 40}, headers=auth_headers
    )

    _criar_pagamento_pix(client, auth_headers, comanda_id, 60)
    r = client.post(
        "/pagamento/confirmacao", json={"comanda_id": comanda_id, "valor": 60}, headers=auth_headers
    )
    assert r.get_json()["saldo_restante"] == 0.0

    r = client.post(f"/comanda/{comanda_id}/fechar", headers=auth_headers)
    assert r.status_code == 200
