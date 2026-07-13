from marshmallow import Schema, fields, validate

FORMAS_PAGAMENTO = ("pix", "cartao", "dinheiro")


class PagamentoSchema(Schema):
    comanda_id = fields.Integer(required=True, validate=validate.Range(min=1))
    valor = fields.Float(required=True, validate=validate.Range(min=0.01))
    forma_pagamento = fields.String(required=True, validate=validate.OneOf(FORMAS_PAGAMENTO))


class PagamentoConfirmacaoSchema(Schema):
    comanda_id = fields.Integer(required=True, validate=validate.Range(min=1))
    valor = fields.Float(required=True, validate=validate.Range(min=0.01))
