from flask import Blueprint, request, jsonify
from app.banco.database import db
from app.models.produto import Produto

produto_rt = Blueprint('produto',__name__,url_prefix='/produtos')

#Criando Produtos
@produto_rt.route('/', methods=['POST'])
def create_produto():
    global id_produto
    dado = request.get_json()
    novo_produto = Produto( nome= dado['nome'],
                           preco = dado['preco'])
    db.session.add(novo_produto)
    db.session.commit()
    return jsonify({"message": "Produto cadastrado com sucesso",
                    "produto":{"id": novo_produto.id,
                            "nome":  novo_produto.nome,
                            "preco": novo_produto.preco},
                            "id":novo_produto.id 
                        })

#Listando todos produtos
@produto_rt.route('/', methods=['GET'])
def get_produtos():

    produtos= Produto.query.all()

    output={"produtos":[]}

    for produto in produtos:
        produto_dado ={
            "id": produto.id,
            "nome":  produto.nome,
            "preco": produto.preco
        }
        output['produtos'].append(produto_dado)

    return jsonify(output)

#Listando um produto especifico
@produto_rt.route('/<int:id>', methods=['GET'])
def get_produto(id):

    produto= Produto.query.get(id)

    if not produto:
        return jsonify({"message":"Produto não encontrado"}), 404
    
    produto_dado ={
            "id": produto.id,
            "nome":  produto.nome,
            "preco": produto.preco
        }
    return jsonify(produto_dado)

#Editando informações de produtos
@produto_rt.route('/<int:id>', methods=['PUT'])
def update_produtos(id):
    produto = Produto.query.get(id)

    if not produto:
        return jsonify({"message":"Produto não encontrado"}),404
    
    dado = request.get_json()
    produto.nome = dado['nome']
    produto.preco = dado ['preco']
    db.session.commit()

    return jsonify({
        "message": "Produto atualizado com sucesso",
        "produto":{
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco
        }
    }) 

#Deletar produtos
@produto_rt.route('/<int:id>', methods=['DELETE'])
def delete_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return jsonify ({"message":"Produto não encontrado"}), 404
    
    db.session.delete(produto)
    db.session.commit()
    return jsonify({"message": "Produto deletado com sucesso"})