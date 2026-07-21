import secrets
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_file

from app.services.email_service import enviar_relatorio_por_email
from app.services.relatorio_service import gerar_planilha_comandas

relatorio_rt = Blueprint('relatorio', __name__, url_prefix='/relatorios')


@relatorio_rt.route('/comandas', methods=['GET'])
def baixar_planilha_comandas():
    planilha = gerar_planilha_comandas()
    nome_arquivo = f"comandas_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    return send_file(
        planilha,
        as_attachment=True,
        download_name=nome_arquivo,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@relatorio_rt.route('/comandas/enviar-email', methods=['POST'])
def enviar_planilha_por_email():
    # Chamada pelo workflow agendado do GitHub Actions (nao por um usuario
    # logado), entao a autenticacao aqui e um segredo proprio, comparado de
    # forma segura contra timing attack, em vez do JWT usado no resto da API.
    segredo_esperado = current_app.config["RELATORIO_CRON_SECRET"]
    segredo_recebido = request.headers.get("X-Cron-Secret", "")
    if not segredo_esperado or not secrets.compare_digest(segredo_recebido, segredo_esperado):
        return jsonify({"message": "Não autorizado."}), 401

    enviar_relatorio_por_email()
    return jsonify({"message": "Relatório enviado por e-mail."})
