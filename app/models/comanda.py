from app.banco.database import db
from app.models.produto import Produto
from app.models.comanda_produto import ComandaProduto

class Comanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    cliente = db.relationship("Cliente", back_populates="comandas")

    comanda_produtos = db.relationship('ComandaProduto', back_populates='comanda', cascade="all, delete-orphan")


    def to_dict(self):
        print(f"comanda_produtos: {self.comanda_produtos}")
        return{
            "id": self.id,
            "data": self.data,
            "cliente_id": self.cliente_id,
            "produtos": [cp.to_dict() for cp in self.comanda_produtos],
            "total": self.calcula_total()
        }
    
    def adicionar_produtos(self, produto: Produto, quantidade: int):
        if quantidade <=0:
            raise ValueError("A quantidade deve ser maior que zero.")
        
        for cp in self.comanda_produtos:
            if cp.produto_id == produto.id:
                cp.quantidade += quantidade
                return
            
        #senão existir 
        novo_cp = ComandaProduto(produto=produto, quantidade=quantidade)
        self.comanda_produtos.append(novo_cp)


    def calcula_total(self):
        return sum(cp.produto.preco * cp.quantidade for cp in self.comanda_produtos)