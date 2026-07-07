from marshmallow import Schema, fields, validate


class ClienteSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=1, max=80))
    telefone = fields.String(
        allow_none=True,
        validate=validate.Regexp(
            r"^\d{10,11}$",
            error="Telefone deve conter 10 ou 11 dígitos numéricos (DDD + número, sem espaços ou símbolos).",
        ),
    )
