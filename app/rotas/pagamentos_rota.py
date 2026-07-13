from flask import Blueprint, jsonify
from app.schemas.pagamento_schema import PagamentoConfirmacaoSchema, PagamentoSchema
from app.services import pagamento_service
from app.utils.validation import load_json


pagamento_rt = Blueprint('pagamento',__name__,url_prefix='/pagamento')
pagamento_schema = PagamentoSchema()
pagamento_confirmacao_schema = PagamentoConfirmacaoSchema()

#criando pagamentos
@pagamento_rt.route('/', methods=['POST'])
def create_pagamento_pix():
    dado = load_json(pagamento_schema)
    return jsonify(pagamento_service.criar_pagamento(dado))


#confirmação de pagamento
@pagamento_rt.route('/confirmacao', methods=['POST'])
def pix_confirmacao():
    dado = load_json(pagamento_confirmacao_schema)
    return jsonify(pagamento_service.confirmar_pagamento(dado))
