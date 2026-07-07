from flask import Blueprint, jsonify
from app.schemas.comanda_schema import AdicionaProdutoSchema, ComandaSchema, QuantidadeSchema
from app.services import comanda_service
from app.utils.validation import load_json

comanda_rt = Blueprint('comanda',__name__,url_prefix='/comanda')
comanda_schema = ComandaSchema()
adiciona_produto_schema = AdicionaProdutoSchema()
quantidade_schema = QuantidadeSchema()

#Criando comandas
@comanda_rt.route('/', methods=['POST'])
def create_comanda():
    dado = load_json(comanda_schema)
    return jsonify(comanda_service.criar_comanda(dado))

#Listando todas as comandas
@comanda_rt.route('/', methods=['GET'])
def get_comandas():
    return jsonify(comanda_service.listar_comandas())

#Listando uma única comanda
@comanda_rt.route('/<int:id>', methods=['GET'])
def get_comanda(id):
    return jsonify(comanda_service.buscar_comanda(id))

#Editando informações da comanda
@comanda_rt.route('/<int:id>', methods=['PUT'])
def update_comanda(id):
    dado = load_json(comanda_schema, partial=True)
    return jsonify(comanda_service.atualizar_comanda(id, dado))

#Adicionar produtos a comanda
@comanda_rt.route('<int:id>/produtos', methods=['POST'])
def adiciona_produto_comanda(id):
    dado = load_json(adiciona_produto_schema)
    return jsonify(comanda_service.adicionar_produto(id, dado))

#Edita quantidades dos produtos da comanda (soma ao que ja existe)
@comanda_rt.route('<int:id>/produtos/<int:produto_id>', methods=['PATCH'])
def update_produtos_comanda(id, produto_id):
    dado = load_json(quantidade_schema)
    return jsonify(comanda_service.incrementar_quantidade_produto(id, produto_id, dado['quantidade']))

#Deleta produtos a comanda
@comanda_rt.route('/<int:id>/produtos/<int:produto_id>', methods=['DELETE'])
def delete_produto_comanda(id,produto_id):
    dado = load_json(quantidade_schema)
    return jsonify(comanda_service.remover_produto(id, produto_id, dado['quantidade']))

#Fecha a comanda (só permitido se o saldo estiver zerado)
@comanda_rt.route('/<int:id>/fechar', methods=['POST'])
def fechar_comanda(id):
    return jsonify(comanda_service.fechar_comanda(id))

#Deleta comanda
@comanda_rt.route('/<int:id>', methods=['DELETE'])
def deleta_comanda(id):
    return jsonify(comanda_service.deletar_comanda(id))
