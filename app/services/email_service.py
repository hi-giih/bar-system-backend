import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

from app.services.relatorio_service import gerar_planilha_comandas


def enviar_relatorio_por_email() -> None:
    planilha = gerar_planilha_comandas()
    nome_arquivo = f"comandas_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    mensagem = MIMEMultipart()
    mensagem["From"] = current_app.config["SMTP_REMETENTE"]
    mensagem["To"] = current_app.config["RELATORIO_EMAIL_DESTINATARIO"]
    mensagem["Subject"] = f"Relatório de comandas - {datetime.now().strftime('%d/%m/%Y')}"
    mensagem.attach(MIMEText(
        "Segue em anexo a planilha com as comandas abertas e o histórico de comandas fechadas.",
        "plain",
    ))

    anexo = MIMEBase("application", "octet-stream")
    anexo.set_payload(planilha.read())
    encoders.encode_base64(anexo)
    anexo.add_header("Content-Disposition", f"attachment; filename={nome_arquivo}")
    mensagem.attach(anexo)

    with smtplib.SMTP(current_app.config["SMTP_HOST"], current_app.config["SMTP_PORT"]) as servidor:
        servidor.starttls()
        servidor.login(current_app.config["SMTP_LOGIN"], current_app.config["SMTP_SENHA"])
        servidor.send_message(mensagem)
