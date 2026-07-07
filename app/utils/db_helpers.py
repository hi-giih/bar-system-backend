from app.banco.database import db
from app.errors import ApiError


def get_or_404(model, obj_id, message: str = None):
    """Busca um registro pelo id ou levanta ApiError (404)."""
    obj = db.session.get(model, obj_id)
    if not obj:
        raise ApiError(message or f"{model.__name__} não encontrado", status_code=404)
    return obj
