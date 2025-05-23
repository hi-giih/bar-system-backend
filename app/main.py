from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "your-secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from models.cliente import Cliente
from models.produto import Produto
from models.comanda import Comanda, comanda_produto
from app import app,db

with app.app_context():
    db.create_all()

    # Criar cliente 
    cliente = Cliente(nome="Giih", telefone="0")

    # Criar produtos
    produto1 = Produto(nome="Agua", preco=9.0)
    produto2 = Produto(nome="Suco", preco=15.0)

    # Criar comanda
    comanda = Comanda(data="20/05/2025")

    # Adicionar produtos à comanda
    comanda.adicionar_produtos(produto1)
    comanda.adicionar_produtos(produto2)

    # Adicionar comanda ao cliente
    cliente.adicionar_comanda(comanda)

    # Salvar no banco
    db.session.add(cliente)
    db.session.commit()

    # Exibir os dados
    print(cliente.to_dict())
    print(comanda.to_dict())
    print("Total:", comanda.calcula_total())