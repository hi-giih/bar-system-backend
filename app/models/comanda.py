from app.banco.database import db
from app.models.produto import Produto

comanda_produto = db.Table('comanda_produto',
    db.Column('comanda_id', db.Integer, db.ForeignKey('comanda.id'), primary_key=True),
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), primary_key=True)
)



class Comanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    cliente = db.relationship("Cliente", back_populates="comandas")

    produtos = db.relationship("Produto", secondary='comanda_produto', backref='comandas')

    def to_dict(self):
        return{
            "id": self.id,
            "data": self.data,
            "produtos": [produto.to_dict() for produto in self.produtos]
        }
    
    def adicionar_produtos(self, produto: Produto):
        self.produtos.append(produto)


    def calcula_total(self):
        total = 0
        for produto in self.produtos:
            total = total + produto.preco
        return total