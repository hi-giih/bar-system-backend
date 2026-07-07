from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.String(required=True, validate=validate.Length(min=1))
    senha = fields.String(required=True, validate=validate.Length(min=1))
