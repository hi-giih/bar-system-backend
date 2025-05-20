from models.cliente import Cliente
from models.produto import Produto
from models.comanda import Comanda


# Criar cliente 
cliente = Cliente(1, "Giih", "0")

# Criar produtos
produto1 = Produto(5, "Agua", 9.0)
produto2 = Produto(6, "Suco", 15.0)

# Criar comanda
comanda = Comanda(101, "20/05/2025")

# Adicionar produtos
comanda.adicionar_produtos(produto1)
comanda.adicionar_produtos(produto2)

# Adicionar comanda ao cliente
cliente.adicionar_comanda(comanda.to_dict())

# Mostrar cliente com comanda
print(cliente.to_dict())


# Mostrar comanda
print(comanda.to_dict())

# Calcular total
comanda.calcula_total()

# Mostrar total 
print(comanda.calcula_total())