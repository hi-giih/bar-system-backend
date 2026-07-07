import os

from flask import Blueprint, current_app, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app.schemas.pagamento_schema import PagamentoSchema
from app.services import pagamento_service
from app.utils.validation import load_json


pagamento_rt = Blueprint('pagamento',__name__,url_prefix='/pagamento')
pagamento_schema = PagamentoSchema()

#criando pagamentos
@pagamento_rt.route('/', methods=['POST'])
def create_pagamento_pix():
    dado = load_json(pagamento_schema)
    return jsonify(pagamento_service.criar_pagamento(dado))


#retornando imagem
@pagamento_rt.route('/pix/qrcode/<file_name>', methods=['GET'])
def get_img(file_name):
    safe_name = secure_filename(file_name)
    if not safe_name:
        return jsonify({"message": "Nome de arquivo inválido"}), 400

    img_dir = os.path.join(current_app.root_path, 'static', 'img')
    return send_from_directory(img_dir, f"{safe_name}.png", mimetype='image/png')


#confirmação de pagamento
@pagamento_rt.route('/confirmacao', methods=['POST'])
def pix_confirmacao():
    dado = load_json(pagamento_schema)
    return jsonify(pagamento_service.confirmar_pagamento(dado))
