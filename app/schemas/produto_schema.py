from marshmallow import Schema, fields, validate

ICONES_PRODUTO = ("drink", "bebida", "comida")


class ProdutoSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=1, max=80))
    preco = fields.Float(required=True, validate=validate.Range(min=0.01))
    # sem load_default: em PUT parcial, so queremos alterar o icone quando
    # o campo vier explicito no corpo (senao "sumiria" o valor atual).
    icone = fields.String(validate=validate.OneOf(ICONES_PRODUTO))
