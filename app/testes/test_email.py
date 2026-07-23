from unittest.mock import MagicMock, patch


def test_enviar_email_sem_segredo_bloqueado(client):
    r = client.post("/relatorios/comandas/enviar-email")
    assert r.status_code == 401


def test_enviar_email_com_segredo_errado_bloqueado(client):
    r = client.post(
        "/relatorios/comandas/enviar-email", headers={"X-Cron-Secret": "segredo-invalido"}
    )
    assert r.status_code == 401


def test_enviar_email_com_segredo_correto_envia_planilha(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 2},
        headers=auth_headers,
    )

    with patch("app.services.email_service.requests.post") as post_mock:
        post_mock.return_value = MagicMock(status_code=200)

        r = client.post(
            "/relatorios/comandas/enviar-email", headers={"X-Cron-Secret": "segredo-teste"}
        )

    assert r.status_code == 200

    post_mock.assert_called_once()
    url, kwargs = post_mock.call_args[0][0], post_mock.call_args[1]
    assert url == "https://api.resend.com/emails"
    assert kwargs["headers"]["Authorization"] == "Bearer re_teste_123"

    corpo = kwargs["json"]
    assert corpo["from"] == "onboarding@resend.dev"
    assert corpo["to"] == ["destino-teste@exemplo.com"]
    assert len(corpo["attachments"]) == 1
    assert corpo["attachments"][0]["filename"].endswith(".xlsx")
