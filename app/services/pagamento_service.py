from datetime import datetime, timedelta

from flask import current_app

from app.banco.database import db
from app.errors import ApiError
from app.models.comanda import Comanda
from app.models.pagamento import Pagamento
from app.pagamentos.pix import Pix
from app.services.comanda_service import calcular_saldo
from app.utils.db_helpers import get_or_404


def criar_pagamento(dado: dict) -> dict:
    comanda_id = dado["comanda_id"]
    valor = dado["valor"]

    get_or_404(Comanda, comanda_id, "Comanda não encontrada")

    expiration_date = datetime.now() + timedelta(minutes=30)
    novo_pagamento = Pagamento(
        value=valor, expiration_date=expiration_date, comanda_id=comanda_id
    )

    pix_obj = Pix(
        chave_pix=current_app.config["PIX_KEY"],
        nome_recebedor=current_app.config["PIX_RECEIVER_NAME"],
        cidade_recebedor=current_app.config["PIX_RECEIVER_CITY"],
    )
    dado_pagamento_pix = pix_obj.create_pagamento(valor)

    novo_pagamento.bank_payment_id = dado_pagamento_pix["bank_payment_id"]
    novo_pagamento.qr_code = dado_pagamento_pix["qr_code_path"]

    db.session.add(novo_pagamento)
    db.session.commit()
    return {"message": "Pagamento criado com sucesso", "pagamento": novo_pagamento.to_dict()}


def confirmar_pagamento(dado: dict) -> dict:
    comanda_id = dado["comanda_id"]
    valor = dado["valor"]

    pagamento = Pagamento.query.filter_by(
        comanda_id=comanda_id, value=valor, paid=False
    ).first()
    if not pagamento:
        raise ApiError("Não existe nenhum pagamento para essa comanda", status_code=404)

    pagamento.paid = True
    comanda = pagamento.comanda

    saldo_info = calcular_saldo(comanda)
    if saldo_info["saldo_restante"] > 0:
        # Pagamento parcial: a partir de agora a comanda exibe uma unica
        # linha de "saldo restante" em vez dos produtos individuais
        # (os produtos continuam guardados no banco, nao sao apagados).
        comanda.colapsada = True

    db.session.commit()
    return {"message": "Pagamento confirmado com sucesso", **saldo_info}
