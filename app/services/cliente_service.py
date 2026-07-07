from app.banco.database import db
from app.models.cliente import Cliente
from app.utils.db_helpers import get_or_404

CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"


def _serialize(cliente: Cliente) -> dict:
    return {"id": cliente.id, "nome": cliente.nome, "telefone": cliente.telefone}


def criar_cliente(dado: dict) -> dict:
    novo_cliente = Cliente(nome=dado["nome"], telefone=dado.get("telefone"))
    db.session.add(novo_cliente)
    db.session.commit()
    return {
        "message": "Cliente cadastrado com sucesso",
        "cliente": _serialize(novo_cliente),
        "id": novo_cliente.id,
    }


def listar_clientes() -> dict:
    clientes = Cliente.query.all()
    return {"clientes": [_serialize(c) for c in clientes]}


def buscar_cliente(cliente_id: int) -> dict:
    cliente = get_or_404(Cliente, cliente_id, CLIENTE_NAO_ENCONTRADO)
    return _serialize(cliente)


def atualizar_cliente(cliente_id: int, dado: dict) -> dict:
    cliente = get_or_404(Cliente, cliente_id, CLIENTE_NAO_ENCONTRADO)
    if "nome" in dado:
        cliente.nome = dado["nome"]
    if "telefone" in dado:
        cliente.telefone = dado["telefone"]
    db.session.commit()
    return {"message": "Cliente atualizado com sucesso", "cliente": _serialize(cliente)}


def deletar_cliente(cliente_id: int) -> dict:
    cliente = get_or_404(Cliente, cliente_id, CLIENTE_NAO_ENCONTRADO)
    db.session.delete(cliente)
    db.session.commit()
    return {"message": "Cliente deletado com sucesso"}
