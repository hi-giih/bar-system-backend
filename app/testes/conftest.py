import pytest
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app
from app.banco.database import db

ADMIN_EMAIL = "admin@teste.com"
ADMIN_SENHA = "senha-teste-123"


@pytest.fixture()
def app():
    """Cria uma app Flask isolada por teste, com banco SQLite em memoria
    (unica conexao via StaticPool) e configuracoes de teste proprias,
    independentes do .env real.
    As overrides precisam ser aplicadas dentro do create_app() (via
    config_overrides), ANTES do db.init_app(): o Flask-SQLAlchemy vincula
    a engine nesse momento, entao sobrescrever app.config depois de criar
    a app nao troca mais o banco de verdade usado."""
    flask_app = create_app(config_overrides={
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "TESTING": True,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        },
        "ADMIN_EMAIL": ADMIN_EMAIL,
        "ADMIN_PASSWORD_HASH": generate_password_hash(ADMIN_SENHA),
        "PIX_KEY": "+5511999999999",
        "PIX_RECEIVER_NAME": "Bar Teste",
        "PIX_RECEIVER_CITY": "Sao Paulo",
        "SMTP_HOST": "smtp-relay.brevo.com",
        "SMTP_PORT": 587,
        "SMTP_LOGIN": "login-teste@smtp-brevo.com",
        "SMTP_SENHA": "senha-teste",
        "SMTP_REMETENTE": "login-teste@smtp-brevo.com",
        "RELATORIO_EMAIL_DESTINATARIO": "destino-teste@exemplo.com",
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    resp = client.post("/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def cliente_id(client, auth_headers):
    resp = client.post("/clientes/", json={"nome": "Cliente Teste"}, headers=auth_headers)
    return resp.get_json()["id"]


@pytest.fixture()
def produto_id(client, auth_headers):
    resp = client.post(
        "/produtos/", json={"nome": "Produto Teste", "preco": 10.0}, headers=auth_headers
    )
    return resp.get_json()["id"]


@pytest.fixture()
def comanda_id(client, auth_headers, cliente_id):
    resp = client.post(
        "/comanda/", json={"data": "2026-07-06", "cliente_id": cliente_id}, headers=auth_headers
    )
    return resp.get_json()["id"]
