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
    forma_pagamento = dado["forma_pagamento"]

    comanda = get_or_404(Comanda, comanda_id, "Comanda não encontrada")

    if forma_pagamento != "pix":
        # Cartao/dinheiro sao pagos fora da aplicacao: nao ha QR code nem
        # confirmacao separada, o pagamento ja nasce confirmado.
        novo_pagamento = Pagamento(
            value=valor, comanda_id=comanda_id, forma_pagamento=forma_pagamento, paid=True
        )
        db.session.add(novo_pagamento)
        comanda.colapsada = True
        saldo_info = calcular_saldo(comanda)
        db.session.commit()
        return {
            "message": "Pagamento registrado com sucesso",
            "pagamento": novo_pagamento.to_dict(),
            **saldo_info,
        }

    expiration_date = datetime.now() + timedelta(minutes=30)
    novo_pagamento = Pagamento(
        value=valor,
        expiration_date=expiration_date,
        comanda_id=comanda_id,
        forma_pagamento=forma_pagamento,
    )

    pix_obj = Pix(
        chave_pix=current_app.config["PIX_KEY"],
        nome_recebedor=current_app.config["PIX_RECEIVER_NAME"],
        cidade_recebedor=current_app.config["PIX_RECEIVER_CITY"],
    )
    dado_pagamento_pix = pix_obj.create_pagamento(valor)

    novo_pagamento.bank_payment_id = dado_pagamento_pix["bank_payment_id"]
    novo_pagamento.qr_code = dado_pagamento_pix["qr_code_base64"]

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

    # A partir de qualquer pagamento confirmado (parcial ou total), a comanda
    # exibe uma unica linha de "saldo restante" em vez dos produtos individuais
    # (os produtos continuam guardados no banco, nao sao apagados). Sem isso,
    # um pagamento que quita o valor total em uma unica vez nao ficava
    # refletido no "total" devolvido por GET /comanda/:id.
    comanda.colapsada = True

    saldo_info = calcular_saldo(comanda)
    db.session.commit()
    return {"message": "Pagamento confirmado com sucesso", **saldo_info}
