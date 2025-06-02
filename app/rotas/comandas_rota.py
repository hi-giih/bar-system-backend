from flask import Blueprint, request, jsonify
from app.banco.database import db
from app.models.comanda import Comanda

comanda_rt = Blueprint('comanda',__name__,url_prefix='/clientes')

#Criando comandas
@comanda_rt.route('/', methods=['POST'])
def create_comanda():
    global id_comanda
    dado = request.get_json()
    nova_comanda = Comanda (
        
    )