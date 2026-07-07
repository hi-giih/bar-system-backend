from flask import Blueprint, jsonify
from app.schemas.produto_schema import ProdutoSchema
from app.services import produto_service
from app.utils.validation import load_json

produto_rt = Blueprint('produto',__name__,url_prefix='/produtos')
produto_schema = ProdutoSchema()

#Criando Produtos
@produto_rt.route('/', methods=['POST'])
def create_produto():
    dado = load_json(produto_schema)
    return jsonify(produto_service.criar_produto(dado))

#Listando todos produtos
@produto_rt.route('/', methods=['GET'])
def get_produtos():
    return jsonify(produto_service.listar_produtos())

#Listando um produto especifico
@produto_rt.route('/<int:id>', methods=['GET'])
def get_produto(id):
    return jsonify(produto_service.buscar_produto(id))

#Editando informações de produtos
@produto_rt.route('/<int:id>', methods=['PUT'])
def update_produtos(id):
    dado = load_json(produto_schema, partial=True)
    return jsonify(produto_service.atualizar_produto(id, dado))

#Deletar produtos
@produto_rt.route('/<int:id>', methods=['DELETE'])
def delete_produto(id):
    return jsonify(produto_service.deletar_produto(id))
