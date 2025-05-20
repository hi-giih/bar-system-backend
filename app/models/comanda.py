from models.produto import Produto

class Comanda():
    def __init__(self, id, data) -> None:
        self.id = id
        self.data = data
        self.produtos = []

    def to_dict(self):
        return{
            "id": self.id,
            "data": self.data,
            "produtos": [produto.to_dict() for produto in self.produtos]
        }
    
    def adicionar_produtos(self, produto: Produto):
        self.produtos.append(produto)


    def calcula_total(self):
        total = 0
        for produto in self.produtos:
            total = total + produto.preco
        return total