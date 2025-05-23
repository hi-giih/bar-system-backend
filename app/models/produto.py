from app.banco.database import db

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return{
            "id": self.id,
            "nome":self.nome,
            "preco":self.preco
        }