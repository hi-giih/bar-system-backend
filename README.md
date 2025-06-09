# 📑 Sistema de comandas

## 📄 Descrição
O Sistema de Comandas é uma aplicação backend desenvolvida em Python, com foco em facilitar o controle de consumo em estabelecimentos como bares, restaurantes, salões de beleza e eventos. O sistema permite o cadastro de itens, a criação de comandas individuais, o registro de produtos consumidos, e o gerenciamento de pagamentos, fornecendo uma visão clara e atualizada do valor total de cada comanda.
Oferecer uma solução simples, rápida e eficaz para o controle de consumo individual, ideal para pequenos negócios que desejam organizar melhor seus atendimentos e evitar perdas financeiras.
Para o código utilizamos uma estrutura escavel utilizando Blueprints.


## ⚙️ Funcionalidades

- ✅ **Cadastro de Clientes:** Cadastro de clientes por nome.
- 🛒 **Cadastro de produtos:** Cadastro de produtos com o nome e o valor.
- 🧾 **Comandas por cliente:** Comanda criada por clientes constando o que foi consumido e o valor pago pelo cliente.
- ✏️ **Cálculo do total da comanda.:** Cálculo total de cada comanda.
- 📟 **Pagamentos via Pix com QR Code :** Pagamento fazendo o controle do valor da comanda, gerando o qr code de pagamento .


## 💻 Tecnologias Utilizadas

- **Python 3.11**
- **Flask 2.3.0**
- **Flask-SQLAlchemy**
- **MySQL (via pymysql connector)**
- **qrcode==7.4.2**
- **pillow==10.2.0**
- **pybrcode==1.1**

## 🆗 Roadmap
- [x] Criar README
- [x] Criar estrutura de arquivos
- [x] Modelar entidades: Cliente, Produto, Comanda
- [x] Implementar CRUD de comandas
- [x] Integração com banco de dados
- [x] Criação das rotas
- [x] Criação do Qr Code

## 🚀 Instalando e Rodando o Projeto

1. Clone este repositório:
```
git clone git@github.com:seu-usuario/bar-system.git
```

2. Acesse o diretório do projeto:
```
cd bar-system
```

3. Crie um ambiente virtual (opcional, mas recomendado):
```
python -m venv venv
```

4. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

5. Instale as dependências:
```
pip install -r requeriments.txt
```

7. Execute a aplicação:
```
python app.py
```

O servidor estará disponível em: `http://127.0.0.1:5000`

## ⚙ Teste
Para rodar os testes unitários: pytest

## 📜 Contribuições
Projeto criado por Giovanna Santos (@hi-giih).