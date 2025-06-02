from flask import Blueprint, request, jsonify
from app.banco.database import db
from app.models.cliente import Cliente

cliente_rt = Blueprint('cliente',__name__,url_prefix='/clientes')

#Criando cliente
@cliente_rt.route('/', methods=['POST'])
def create_cliente():
    global id_cliente
    dado = request.get_json()
    novo_cliente = Cliente( nome=dado['nome'],
                           telefone=dado['telefone'],
                           )
    db.session.add(novo_cliente)
    db.session.commit()
    return jsonify({"message":"Cliente cadastrado com sucesso",
                    "cliente":{
                        "id": novo_cliente.id,
                        "nome": novo_cliente.nome,
                        "telefone": novo_cliente.telefone 
                    }})

#Listando todos clientes
@cliente_rt.route('/', methods=['GET'])
def get_clientes():

    clientes = Cliente.query.all()

    output={"clientes":[]}

    for cliente in clientes:
        cliente_dado ={
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone
        }
        output['clientes'].append(cliente_dado)

    return jsonify(output)


#Listando um cliente especifico
@cliente_rt.route('/<int:id>', methods=['GET'])
def get_cliente(id):

    cliente = Cliente.query.get(id)

    if not cliente:
        return jsonify({"message":"Cliente não encontrado"}), 404
    
    cliente_dado ={
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone
        }
    return jsonify(cliente_dado)


#Editando informações do cliente
@cliente_rt.route('/<int:id>', methods=['PUT'])
def update_cliente(id):
    cliente = Cliente.query.get(id)

    if not cliente:
        return jsonify({"message":"Cliente não encontrado"}), 404
    
    dado = request.get_json()
    cliente.nome = dado['nome']
    cliente.telefone = dado['telefone']
    db.session.commit()

    return jsonify({
        "message": "Cliente atualizado com sucesso",
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone
        }
    })

#Deletar clientes
@cliente_rt.route('/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    cliente = Cliente.query.get(id)

    if not cliente:
        return jsonify({"message":"Cliente não encontrado"}), 404

    db.session.delete(cliente)
    db.session.commit()
    return jsonify({"message":"Cliente deletado com sucesso"})
