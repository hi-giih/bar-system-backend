from app import db

class Cliente (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    telefone = db.Column(db.String(11))
    
    comandas = db.relationship("Comanda", back_populates="cliente", cascade="all, delete-orphan")


    def to_dict(self):
        return{
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "comandas": [comanda.to_dict() for comanda in self.comandas]
        }

    def adicionar_comanda(self, comanda):
        self.comandas.append(comanda)

        