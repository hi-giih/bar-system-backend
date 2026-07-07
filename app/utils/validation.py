from flask import request
from marshmallow import ValidationError

from app.errors import ApiError


def load_json(schema, partial: bool = False) -> dict:
    """Le o corpo da requisicao como JSON e valida com o schema informado.
    Levanta ApiError (400) se o corpo nao for um JSON valido ou se os
    dados nao passarem na validacao do schema."""
    dado = request.get_json(silent=True, force=True)
    if not isinstance(dado, dict):
        raise ApiError("O corpo da requisição deve ser um JSON válido.")

    try:
        return schema.load(dado, partial=partial)
    except ValidationError as err:
        raise ApiError("Dados inválidos.", errors=err.messages)
