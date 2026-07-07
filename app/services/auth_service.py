from flask import current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from app.errors import ApiError

CREDENCIAIS_INVALIDAS = "E-mail ou senha inválidos."


def autenticar(dado: dict) -> dict:
    email = dado["email"]
    senha = dado["senha"]

    admin_email = current_app.config["ADMIN_EMAIL"]
    admin_password_hash = current_app.config["ADMIN_PASSWORD_HASH"]

    if not admin_email or not admin_password_hash:
        raise ApiError("Login não configurado no servidor.", status_code=500)

    if email != admin_email or not check_password_hash(admin_password_hash, senha):
        raise ApiError(CREDENCIAIS_INVALIDAS, status_code=401)

    access_token = create_access_token(identity=email)
    return {"access_token": access_token}
