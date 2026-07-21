from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.exceptions import HTTPException
from app.banco.database import db
from app.config import Config
from app.errors import ApiError

from app.rotas.auth_rota import auth_rt
from app.rotas.clientes_rota import cliente_rt
from app.rotas.produtos_rota import produto_rt
from app.rotas.comandas_rota import comanda_rt
from app.rotas.pagamentos_rota import pagamento_rt
from app.rotas.relatorios_rota import relatorio_rt

migrate = Migrate()
jwt = JWTManager()

# Endpoints que nao exigem token JWT (login, health check, rotas nao
# encontradas, e o disparo automatico do relatorio semanal, que e chamado
# por um workflow agendado do GitHub Actions em vez de um usuario logado
# e valida um segredo proprio dentro da propria rota).
ENDPOINTS_PUBLICOS = {"auth.login", "health", "relatorio.enviar_planilha_por_email", None}

def create_app(config_overrides: dict | None = None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        # Precisa ser aplicado antes do db.init_app: a engine do
        # Flask-SQLAlchemy e vinculada nesse momento, entao sobrescrever
        # app.config depois nao troca mais o banco de fato usado.
        app.config.update(config_overrides)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])

    app.register_blueprint(auth_rt)
    app.register_blueprint(cliente_rt)
    app.register_blueprint(produto_rt)
    app.register_blueprint(comanda_rt)
    app.register_blueprint(pagamento_rt)
    app.register_blueprint(relatorio_rt)

    @app.route('/health', methods=['GET'])
    def health():
        # Consulta o banco de propósito: além de checar a saúde de verdade,
        # isso mantém o Supabase ativo quando chamado periodicamente por um
        # serviço externo de ping, evitando a pausa por inatividade do plano free.
        try:
            db.session.execute(text('SELECT 1'))
            return jsonify({"status": "ok", "database": "ok"})
        except Exception:
            db.session.rollback()
            app.logger.exception("Health check: banco indisponível")
            return jsonify({"status": "ok", "database": "erro"}), 503

    @app.before_request
    def _exigir_login():
        # Preflight do CORS nunca envia credenciais; o Flask-CORS
        # cuida de responder e adicionar os headers necessarios.
        if request.method == "OPTIONS":
            return
        if request.endpoint in ENDPOINTS_PUBLICOS:
            return
        verify_jwt_in_request()

    @jwt.unauthorized_loader
    def _token_ausente(motivo):
        return jsonify({"message": "Token de autenticação ausente."}), 401

    @jwt.invalid_token_loader
    def _token_invalido(motivo):
        return jsonify({"message": "Token de autenticação inválido."}), 401

    @jwt.expired_token_loader
    def _token_expirado(jwt_header, jwt_payload):
        return jsonify({"message": "Token de autenticação expirado."}), 401

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        payload = {"message": err.message}
        if err.errors:
            payload["errors"] = err.errors
        return jsonify(payload), err.status_code

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"message": "Recurso não encontrado."}), 404

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({"message": err.description or err.name}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        db.session.rollback()
        app.logger.exception("Erro inesperado")
        return jsonify({"message": "Erro interno do servidor."}), 500

    return app
