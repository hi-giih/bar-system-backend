from app.banco.database import db
from app.models.produto import Produto

class ComandaProduto(db.Model):
    __tablename__ = 'comanda_produto' 

    comanda_id = db.Column(db.Integer, db.ForeignKey('comanda.id'), primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), primary_key=True)
    quantidade= db.Column(db.Integer, nullable=False)

    # Relacionamentos
    comanda = db.relationship('Comanda', back_populates='comanda_produtos')
    produto = db.relationship('Produto')

    def to_dict(self):
        print(f"Produto: {self.produto}")
        return {
            "produto_id": self.produto.id,
            "nome": self.produto.nome,
            "preco": self.produto.preco,
            "quantidade": self.quantidade,
            "subtotal": self.produto.preco * self.quantidade
        }
