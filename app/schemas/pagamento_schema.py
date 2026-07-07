from marshmallow import Schema, fields, validate


class PagamentoSchema(Schema):
    comanda_id = fields.Integer(required=True, validate=validate.Range(min=1))
    valor = fields.Float(required=True, validate=validate.Range(min=0.01))
