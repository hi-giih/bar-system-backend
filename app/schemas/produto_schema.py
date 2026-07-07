from marshmallow import Schema, fields, validate


class ProdutoSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=1, max=80))
    preco = fields.Float(required=True, validate=validate.Range(min=0.01))
