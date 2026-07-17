from unittest.mock import MagicMock, patch


def test_enviar_email_sem_autenticacao_bloqueado(client):
    r = client.post("/relatorios/comandas/enviar-email")
    assert r.status_code == 401


def test_enviar_email_envia_planilha_por_smtp(client, auth_headers, comanda_id, produto_id):
    client.post(
        f"/comanda/{comanda_id}/produtos",
        json={"produto_id": produto_id, "quantidade": 2},
        headers=auth_headers,
    )

    with patch("app.services.email_service.smtplib.SMTP") as smtp_cls:
        servidor = MagicMock()
        smtp_cls.return_value.__enter__.return_value = servidor

        r = client.post("/relatorios/comandas/enviar-email", headers=auth_headers)

    assert r.status_code == 200
    smtp_cls.assert_called_once_with("smtp-relay.brevo.com", 587)
    servidor.starttls.assert_called_once()
    servidor.login.assert_called_once_with("login-teste@smtp-brevo.com", "senha-teste")

    servidor.send_message.assert_called_once()
    mensagem = servidor.send_message.call_args[0][0]
    assert mensagem["From"] == "login-teste@smtp-brevo.com"
    assert mensagem["To"] == "destino-teste@exemplo.com"
    assert mensagem.get_content_type() == "multipart/mixed"
