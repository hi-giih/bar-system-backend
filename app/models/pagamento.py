from app.banco.database import db

class Pagamento(db.Model):
    __tablename__ = 'pagamento'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    comanda_id = db.Column(db.Integer, db.ForeignKey('comanda.id'))
    paid = db.Column(db.Boolean, default=False)  
    bank_payment_id = db.Column(db.String(200), nullable=True)
    qr_code = db.Column(db.String(100), nullable=True)
    expiration_date = db.Column(db.DateTime)

    #Relacionamentos
    comanda = db.relationship('Comanda', backref='pagamentos')


    def to_dict(self):
        return{
            "id": self.id,
            "comanda": self.comanda_id,
            "value": self.value,
            "paid": self.paid,
            "bank_payment_id": self.bank_payment_id,
            "qr_code": self.qr_code,
            "expiration_date":self.expiration_date
        }