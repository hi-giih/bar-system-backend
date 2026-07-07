from flask import Blueprint, jsonify
from app.schemas.cliente_schema import ClienteSchema
from app.services import cliente_service
from app.utils.validation import load_json

cliente_rt = Blueprint('cliente',__name__,url_prefix='/clientes')
cliente_schema = ClienteSchema()

#Criando cliente
@cliente_rt.route('/', methods=['POST'])
def create_cliente():
    dado = load_json(cliente_schema)
    return jsonify(cliente_service.criar_cliente(dado))

#Listando todos clientes
@cliente_rt.route('/', methods=['GET'])
def get_clientes():
    return jsonify(cliente_service.listar_clientes())

#Listando um cliente especifico
@cliente_rt.route('/<int:id>', methods=['GET'])
def get_cliente(id):
    return jsonify(cliente_service.buscar_cliente(id))

#Editando informações do cliente
@cliente_rt.route('/<int:id>', methods=['PUT'])
def update_cliente(id):
    dado = load_json(cliente_schema, partial=True)
    return jsonify(cliente_service.atualizar_cliente(id, dado))

#Deletar clientes
@cliente_rt.route('/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    return jsonify(cliente_service.deletar_cliente(id))
