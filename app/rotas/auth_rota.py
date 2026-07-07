from flask import Blueprint, jsonify
from app.schemas.auth_schema import LoginSchema
from app.services import auth_service
from app.utils.validation import load_json

auth_rt = Blueprint('auth', __name__, url_prefix='/auth')
login_schema = LoginSchema()

#Login do admin, gera o token JWT usado nas demais rotas
@auth_rt.route('/login', methods=['POST'])
def login():
    dado = load_json(login_schema)
    return jsonify(auth_service.autenticar(dado))
