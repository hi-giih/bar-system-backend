from flask import Blueprint, request, jsonify
from app.banco.database import db
from app.models.comanda import Comanda
from app.models.produto import Produto
from app.models.cliente import Cliente

comanda_rt = Blueprint('comanda',__name__,url_prefix='/comanda')

#Criando comandas
@comanda_rt.route('/', methods=['POST'])
def create_comanda():
    global id_comanda
    dado = request.get_json()

    data = dado.get('data')
    cliente_id = dado.get('cliente_id')

    if not data or not cliente_id:
        return jsonify({"message":"Cliente e Data são obrigatorios"}), 400


    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"message": "Cliente não encontrado"}), 404

    nova_comanda = Comanda( 
        data=data,
        cliente_id= cliente.id
    )
    db.session.add(nova_comanda)
    db.session.commit()
    return jsonify(nova_comanda.to_dict())

#Listando todas as comandas
@comanda_rt.route('/', methods=['GET'])
def get_comandas():

    comandas = Comanda.query.all()

    output={"comandas":[]}

    for comanda in comandas:
        comanda_dict = comanda.to_dict()
        output["comandas"].append(comanda_dict)
    
    return jsonify(output)

#Listando uma única comanda
@comanda_rt.route('/<int:id>', methods=['GET'])
def get_comanda(id):
    comanda = Comanda.query.get(id)

    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    comanda_dict = comanda.to_dict()
    return jsonify(comanda_dict)

#Editando informações da comanda
@comanda_rt.route('/<int:id>', methods=['PUT'])
def update_comanda(id):
    comanda = Comanda.query.get(id)

    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    dado = request.get_json()
    # Atualiza data se fornecida
    if 'data' in dado:
        comanda.data = dado['data']

    # Atualiza cliente se fornecido
    if 'cliente_id' in dado:
        comanda.cliente_id = dado['cliente_id']
    
    db.session.commit()
    return jsonify({"message":"Informações atualizadas",
                    "comanda": comanda.to_dict()})

#Adicionar produtos a comanda
@comanda_rt.route('<int:id>/produtos', methods=['POST'])
def adiciona_produto_comanda(id):
    comanda = Comanda.query.get(id)
    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    dado = request.get_json()
    produto_id=dado.get('produto_id')
    quantidade=dado.get('quantidade')

    if not produto_id or not quantidade or quantidade <=0:
        return jsonify({"message": "Dados inválidos"}), 400
    
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"message": "Produto não encontrado"}), 404
    
    comanda.adicionar_produtos(produto, quantidade)
    db.session.commit()
    return jsonify({"message": "Produto adicionado com sucesso", "comanda": comanda.to_dict()})

#Edita quantidades dos produtos da comanda
@comanda_rt.route('<int:id>/produtos/<int:produto_id>', methods=['PATCH'])
def update_produtos_comanda(id, produto_id):
    comanda = Comanda.query.get(id)
    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    dado = request.get_json()
    quantidade=dado.get('quantidade')

    if quantidade is None or quantidade <= 0:
        return jsonify({"message":"A quantidade tem que ser maior que zero"}), 400

    for cp in comanda.comanda_produtos:
        if cp.produto_id == produto_id:
            cp.quantidade += quantidade
            db.session.commit()
            return jsonify({"message": "Quantidade atualizada com sucesso",
                            "comanda": comanda.to_dict()})
    return jsonify({"message": "Produto não encontrado na comanda"}), 404


#Deleta produtos a comanda
@comanda_rt.route('/<int:id>/produtos/<int:produto_id>', methods=['DELETE'])
def delete_produto_comanda(id,produto_id):
    comanda = Comanda.query.get(id)
    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    dado = request.get_json()
    quantidade=dado.get('quantidade', 0)

    if quantidade <= 0:
        return jsonify({"message":"Informe uma quantidade válida para remover"}), 400
    
    for cp in comanda.comanda_produtos:
        if cp.produto_id == produto_id:
            if cp.quantidade > quantidade:
                cp.quantidade -= quantidade
            else:
                comanda.comanda_produtos.remove(cp)
                db.session.delete(cp)

            db.session.commit()
            return jsonify({"message": "Produto removido da comanda com sucesso",
                            "comanda": comanda.to_dict()})
    return jsonify({"message": "Produto não encontrado na comanda"}), 404


#Deleta comanda
@comanda_rt.route('/<int:id>', methods=['DELETE'])
def deleta_comanda(id):
    comanda = Comanda.query.get(id)
    if not comanda:
        return jsonify({"message":"Comanda não encontrada"}), 404
    
    for cp in comanda.comanda_produtos:
        db.session.delete(cp)
    
    db.session.delete(comanda)
    db.session.commit()

    return jsonify({"message": "Comanda deletada com sucesso"})