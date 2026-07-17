import io

from openpyxl import Workbook
from openpyxl.styles import Font

from app.models.comanda import Comanda
from app.services.comanda_service import calcular_saldo, forma_pagamento_final

CABECALHO_ABERTAS = [
    "Cliente", "Data", "Produto", "Quantidade", "Preço Unitário", "Subtotal", "Saldo Devedor",
]
CABECALHO_HISTORICO = [
    "Cliente", "Data", "Forma de Pagamento", "Produto", "Quantidade", "Preço Unitário",
    "Subtotal", "Valor Total da Comanda",
]


def _nome_cliente(comanda: Comanda) -> str:
    return comanda.cliente.nome if comanda.cliente else "Cliente removido"


def _escrever_cabecalho(planilha, colunas: list[str]) -> None:
    planilha.append(colunas)
    for celula in planilha[1]:
        celula.font = Font(bold=True)


def _preencher_aba_abertas(planilha, comandas: list[Comanda]) -> None:
    _escrever_cabecalho(planilha, CABECALHO_ABERTAS)

    for comanda in comandas:
        saldo = calcular_saldo(comanda)["saldo_restante"]
        if not comanda.comanda_produtos:
            planilha.append([_nome_cliente(comanda), comanda.data, "-", "-", "-", "-", saldo])
            continue
        for cp in comanda.comanda_produtos:
            planilha.append([
                _nome_cliente(comanda), comanda.data, cp.produto.nome, cp.quantidade,
                cp.produto.preco, cp.produto.preco * cp.quantidade, saldo,
            ])


def _preencher_aba_historico(planilha, comandas: list[Comanda]) -> None:
    _escrever_cabecalho(planilha, CABECALHO_HISTORICO)

    for comanda in comandas:
        forma = forma_pagamento_final(comanda) or "-"
        total = comanda.calcula_total()
        if not comanda.comanda_produtos:
            planilha.append([_nome_cliente(comanda), comanda.data, forma, "-", "-", "-", "-", total])
            continue
        for cp in comanda.comanda_produtos:
            planilha.append([
                _nome_cliente(comanda), comanda.data, forma, cp.produto.nome, cp.quantidade,
                cp.produto.preco, cp.produto.preco * cp.quantidade, total,
            ])


def gerar_planilha_comandas() -> io.BytesIO:
    """Gera uma planilha .xlsx em memoria (nunca gravada em disco) com duas
    abas: comandas ainda abertas e o historico de comandas ja fechadas."""
    todas = Comanda.query.all()
    abertas = [c for c in todas if not c.fechada]
    fechadas = [c for c in todas if c.fechada]

    workbook = Workbook()
    _preencher_aba_abertas(workbook.active, abertas)
    workbook.active.title = "Comandas Abertas"

    aba_historico = workbook.create_sheet("Histórico")
    _preencher_aba_historico(aba_historico, fechadas)

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
