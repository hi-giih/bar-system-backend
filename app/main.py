from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.comanda import Comanda, comanda_produto
from app.banco.database import db
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)