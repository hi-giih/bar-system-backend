from app.banco.database import db
from app.errors import ApiError
from app.models.cliente import Cliente
from app.models.comanda import Comanda
from app.models.produto import Produto
from app.utils.db_helpers import get_or_404

COMANDA_NAO_ENCONTRADA = "Comanda não encontrada"
CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"
PRODUTO_NAO_ENCONTRADO = "Produto não encontrado"
PRODUTO_NAO_ENCONTRADO_NA_COMANDA = "Produto não encontrado na comanda"
COMANDA_FECHADA = "Comanda fechada não pode ser alterada."
COMANDA_JA_FECHADA = "Comanda já está fechada."


def calcular_saldo(comanda: Comanda) -> dict:
    total_comanda = comanda.calcula_total()
    total_pago = sum(p.value for p in comanda.pagamentos if p.paid)
    return {
        "total_comanda": total_comanda,
        "total_pago": total_pago,
        "saldo_restante": total_comanda - total_pago,
    }


def forma_pagamento_final(comanda: Comanda) -> str | None:
    """Forma de pagamento do ultimo pagamento confirmado da comanda (usado
    para exibir na aba de comandas fechadas). None se nada foi pago ainda."""
    pagos = [p for p in comanda.pagamentos if p.paid]
    if not pagos:
        return None
    return max(pagos, key=lambda p: p.id).forma_pagamento


def _serializar_comanda(comanda: Comanda) -> dict:
    """Serializa a comanda para resposta da API. Enquanto a comanda ainda
    esta aberta e ja houve pagamento parcial (comanda.colapsada), os produtos
    individuais ficam ocultos e a comanda exibe uma unica linha com o saldo
    restante. Uma vez fechada, mostra os produtos reais (so leitura, a tela
    ja bloqueia edicao de comanda fechada) - nao ha mais saldo a esconder.
    Os produtos originais NUNCA sao apagados do banco (historico)."""
    comanda_dict = comanda.to_dict()
    comanda_dict["forma_pagamento"] = forma_pagamento_final(comanda)

    if comanda.colapsada and not comanda.fechada:
        saldo_restante = calcular_saldo(comanda)["saldo_restante"]
        comanda_dict["produtos"] = [{
            "produto_id": None,
            "nome": "Saldo restante",
            "preco": saldo_restante,
            "quantidade": 1,
            "subtotal": saldo_restante,
        }]
        comanda_dict["total"] = saldo_restante

    return comanda_dict


def criar_comanda(dado: dict) -> dict:
    cliente = get_or_404(Cliente, dado["cliente_id"], CLIENTE_NAO_ENCONTRADO)
    nova_comanda = Comanda(data=dado["data"], cliente_id=cliente.id)
    db.session.add(nova_comanda)
    db.session.commit()
    return _serializar_comanda(nova_comanda)


def listar_comandas() -> dict:
    comandas = Comanda.query.all()
    return {"comandas": [_serializar_comanda(c) for c in comandas]}


def buscar_comanda(comanda_id: int) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)
    return _serializar_comanda(comanda)


def atualizar_comanda(comanda_id: int, dado: dict) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)
    if comanda.fechada:
        raise ApiError(COMANDA_FECHADA, status_code=400)

    if "cliente_id" in dado:
        get_or_404(Cliente, dado["cliente_id"], CLIENTE_NAO_ENCONTRADO)
        comanda.cliente_id = dado["cliente_id"]

    if "data" in dado:
        comanda.data = dado["data"]

    db.session.commit()
    return {"message": "Informações atualizadas", "comanda": _serializar_comanda(comanda)}


def adicionar_produto(comanda_id: int, dado: dict) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)
    if comanda.fechada:
        raise ApiError(COMANDA_FECHADA, status_code=400)

    produto = get_or_404(Produto, dado["produto_id"], PRODUTO_NAO_ENCONTRADO)

    comanda.adicionar_produtos(produto, dado["quantidade"])
    db.session.commit()
    return {"message": "Produto adicionado com sucesso", "comanda": _serializar_comanda(comanda)}


def incrementar_quantidade_produto(comanda_id: int, produto_id: int, quantidade: int) -> dict:
    """Soma 'quantidade' unidades ao produto ja existente na comanda
    (pedido adicional do mesmo produto, nao substituicao do total)."""
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)
    if comanda.fechada:
        raise ApiError(COMANDA_FECHADA, status_code=400)

    for cp in comanda.comanda_produtos:
        if cp.produto_id == produto_id:
            cp.quantidade += quantidade
            db.session.commit()
            return {"message": "Quantidade atualizada com sucesso", "comanda": _serializar_comanda(comanda)}

    raise ApiError(PRODUTO_NAO_ENCONTRADO_NA_COMANDA, status_code=404)


def remover_produto(comanda_id: int, produto_id: int, quantidade: int) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)
    if comanda.fechada:
        raise ApiError(COMANDA_FECHADA, status_code=400)

    for cp in comanda.comanda_produtos:
        if cp.produto_id == produto_id:
            if cp.quantidade > quantidade:
                cp.quantidade -= quantidade
            else:
                comanda.comanda_produtos.remove(cp)
                db.session.delete(cp)
            db.session.commit()
            return {"message": "Produto removido da comanda com sucesso", "comanda": _serializar_comanda(comanda)}

    raise ApiError(PRODUTO_NAO_ENCONTRADO_NA_COMANDA, status_code=404)


def fechar_comanda(comanda_id: int) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)

    if comanda.fechada:
        raise ApiError(COMANDA_JA_FECHADA, status_code=400)

    saldo_restante = calcular_saldo(comanda)["saldo_restante"]
    if saldo_restante > 0:
        raise ApiError(
            f"Comanda possui saldo pendente de {saldo_restante:.2f} e não pode ser fechada.",
            status_code=400,
        )

    comanda.fechada = True
    db.session.commit()
    return {"message": "Comanda fechada com sucesso.", "comanda": _serializar_comanda(comanda)}


def deletar_comanda(comanda_id: int) -> dict:
    comanda = get_or_404(Comanda, comanda_id, COMANDA_NAO_ENCONTRADA)

    # comanda_produtos e pagamentos sao removidos automaticamente pelo
    # cascade="all, delete-orphan" configurado nos relacionamentos.
    db.session.delete(comanda)
    db.session.commit()
    return {"message": "Comanda deletada com sucesso"}
