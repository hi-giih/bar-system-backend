from marshmallow import Schema, fields, validate


class ComandaSchema(Schema):
    data = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^\d{4}-\d{2}-\d{2}$", error="Data deve estar no formato AAAA-MM-DD."
        ),
    )
    cliente_id = fields.Integer(required=True, validate=validate.Range(min=1))


class AdicionaProdutoSchema(Schema):
    produto_id = fields.Integer(required=True, validate=validate.Range(min=1))
    quantidade = fields.Integer(required=True, validate=validate.Range(min=1))


class QuantidadeSchema(Schema):
    quantidade = fields.Integer(required=True, validate=validate.Range(min=1))
