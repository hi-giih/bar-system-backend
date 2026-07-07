import os
import re
import uuid

from pybrcode.pix import generate_simple_pix


def _format_phone_key(raw_phone: str) -> str:
    """Converte um telefone tipo "+5511999999999" para o formato
    de mascara "(11) 99999-9999" exigido pela lib pybrcode."""
    digits = re.sub(r"\D", "", raw_phone)
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]
    if len(digits) not in (10, 11):
        raise ValueError(
            "PIX_KEY de telefone deve conter DDD + numero (10 ou 11 digitos)."
        )
    ddd, numero = digits[:2], digits[2:]
    if len(numero) == 9:
        return f"({ddd}) {numero[:5]}-{numero[5:]}"
    return f"({ddd}) {numero[:4]}-{numero[4:]}"


class Pix:
    def __init__(self, chave_pix: str, nome_recebedor: str, cidade_recebedor: str):
        self.chave_pix = chave_pix
        self.nome_recebedor = nome_recebedor
        self.cidade_recebedor = cidade_recebedor

    def create_pagamento(self, valor: float) -> dict:
        bank_payment_id = str(uuid.uuid4())

        chave_formatada = self.chave_pix
        if chave_formatada.strip().startswith("+"):
            chave_formatada = _format_phone_key(chave_formatada)

        pix = generate_simple_pix(
            fullname=self.nome_recebedor,
            key=chave_formatada,
            city=self.cidade_recebedor,
            value=valor,
        )

        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(base_dir, "..", "static", "img")
        os.makedirs(img_dir, exist_ok=True)

        file_name = f"qr_code_pagamento_{bank_payment_id}"
        pix.imageToPath(img_dir, file_name, svg=False)

        return {
            "bank_payment_id": bank_payment_id,
            "qr_code_path": file_name,
            "pix_brcode": str(pix),
        }
