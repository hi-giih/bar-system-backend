from app.banco.database import db

class Pagamento(db.Model):
    __tablename__ = 'pagamento'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    comanda_id = db.Column(db.Integer, db.ForeignKey('comanda.id'))
    paid = db.Column(db.Boolean, default=False)
    forma_pagamento = db.Column(db.String(20), nullable=False, default='pix')
    bank_payment_id = db.Column(db.String(200), nullable=True)
    # Guarda a imagem do QR code como data URI base64 (nao um caminho de
    # arquivo): o Pix e gerado em memoria e nunca gravado em disco.
    qr_code = db.Column(db.Text, nullable=True)
    expiration_date = db.Column(db.DateTime)

    #Relacionamentos
    comanda = db.relationship(
        'Comanda',
        backref=db.backref('pagamentos', cascade='all, delete-orphan'),
    )


    def to_dict(self):
        return{
            "id": self.id,
            "comanda": self.comanda_id,
            "value": self.value,
            "paid": self.paid,
            "forma_pagamento": self.forma_pagamento,
            "bank_payment_id": self.bank_payment_id,
            "qr_code": self.qr_code,
            "expiration_date":self.expiration_date
        }