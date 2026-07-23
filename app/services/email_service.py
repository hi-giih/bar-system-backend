import base64
from datetime import datetime

import requests
from flask import current_app

from app.services.relatorio_service import gerar_planilha_comandas

RESEND_API_URL = "https://api.resend.com/emails"


def enviar_relatorio_por_email() -> None:
    planilha = gerar_planilha_comandas()
    nome_arquivo = f"comandas_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    conteudo_base64 = base64.b64encode(planilha.read()).decode("ascii")

    resposta = requests.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {current_app.config['RESEND_API_KEY']}"},
        json={
            "from": current_app.config["RESEND_REMETENTE"],
            "to": [current_app.config["RELATORIO_EMAIL_DESTINATARIO"]],
            "subject": f"Relatório de comandas - {datetime.now().strftime('%d/%m/%Y')}",
            "html": (
                "<p>Segue em anexo a planilha com as comandas abertas "
                "e o histórico de comandas fechadas.</p>"
            ),
            "attachments": [{"filename": nome_arquivo, "content": conteudo_base64}],
        },
        timeout=30,
    )
    resposta.raise_for_status()
