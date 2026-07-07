class ApiError(Exception):
    """Erro esperado de requisicao (dados invalidos, JSON malformado, etc).
    Convertido em resposta JSON pelo error handler central em app/__init__.py."""

    def __init__(self, message: str, status_code: int = 400, errors: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors
