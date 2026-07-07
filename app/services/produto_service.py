from app.banco.database import db
from app.models.produto import Produto
from app.utils.db_helpers import get_or_404

PRODUTO_NAO_ENCONTRADO = "Produto não encontrado"


def _serialize(produto: Produto) -> dict:
    return {"id": produto.id, "nome": produto.nome, "preco": produto.preco}


def criar_produto(dado: dict) -> dict:
    novo_produto = Produto(nome=dado["nome"], preco=dado["preco"])
    db.session.add(novo_produto)
    db.session.commit()
    return {
        "message": "Produto cadastrado com sucesso",
        "produto": _serialize(novo_produto),
        "id": novo_produto.id,
    }


def listar_produtos() -> dict:
    produtos = Produto.query.all()
    return {"produtos": [_serialize(p) for p in produtos]}


def buscar_produto(produto_id: int) -> dict:
    produto = get_or_404(Produto, produto_id, PRODUTO_NAO_ENCONTRADO)
    return _serialize(produto)


def atualizar_produto(produto_id: int, dado: dict) -> dict:
    produto = get_or_404(Produto, produto_id, PRODUTO_NAO_ENCONTRADO)
    if "nome" in dado:
        produto.nome = dado["nome"]
    if "preco" in dado:
        produto.preco = dado["preco"]
    db.session.commit()
    return {"message": "Produto atualizado com sucesso", "produto": _serialize(produto)}


def deletar_produto(produto_id: int) -> dict:
    produto = get_or_404(Produto, produto_id, PRODUTO_NAO_ENCONTRADO)
    db.session.delete(produto)
    db.session.commit()
    return {"message": "Produto deletado com sucesso"}
