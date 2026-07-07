from app.testes.conftest import ADMIN_EMAIL, ADMIN_SENHA


def test_login_sucesso(client):
    r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA})
    assert r.status_code == 200
    assert "access_token" in r.get_json()


def test_login_senha_errada(client):
    r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "senha": "senha-errada"})
    assert r.status_code == 401


def test_login_email_errado(client):
    r = client.post("/auth/login", json={"email": "outro@teste.com", "senha": ADMIN_SENHA})
    assert r.status_code == 401


def test_login_sem_senha(client):
    r = client.post("/auth/login", json={"email": ADMIN_EMAIL})
    assert r.status_code == 400


def test_rota_protegida_sem_token(client):
    r = client.get("/clientes/")
    assert r.status_code == 401


def test_rota_protegida_token_invalido(client):
    r = client.get("/clientes/", headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401


def test_rota_protegida_com_token(client, auth_headers):
    r = client.get("/clientes/", headers=auth_headers)
    assert r.status_code == 200
