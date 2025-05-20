class Cliente():
    def __init__(self, id ,nome, telefone) -> None:
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.comandas= [] 


    def to_dict(self):
        return{
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "comandas": self.comandas
        }

    def adicionar_comanda(self, comanda):
        self.comandas.append(comanda)

        