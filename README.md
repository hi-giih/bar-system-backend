# 📑 Sistema de comandas

## 📄 Descrição
O Sistema de Comandas é uma API backend desenvolvida em Python, com foco em facilitar o controle de consumo em estabelecimentos como bares, restaurantes, salões de beleza e eventos. O sistema permite o cadastro de clientes e produtos, a criação de comandas individuais, o registro de produtos consumidos, e o gerenciamento de pagamentos via Pix, fornecendo uma visão clara e atualizada do valor total (e do saldo restante) de cada comanda.

O código segue uma estrutura em camadas usando Blueprints (rotas), uma camada de serviços (regras de negócio) e schemas de validação, visando manutenibilidade e testabilidade.

## ⚙️ Funcionalidades

- ✅ **Autenticação:** login único (admin) via JWT — todas as rotas exigem token, exceto `/auth/login` e `/health`.
- 👤 **Cadastro de Clientes:** CRUD de clientes (nome e telefone).
- 🛒 **Cadastro de Produtos:** CRUD de produtos (nome e preço).
- 🧾 **Comandas por cliente:** criação de comandas, adição/remoção de produtos, cálculo automático do total.
- 🔒 **Fechamento de comanda:** uma comanda só pode ser fechada com saldo zerado; depois de fechada, não aceita mais alterações (produtos ou dados), mas pode ser deletada.
- 💰 **Pagamento parcial:** ao confirmar um pagamento que não cobre o total, a comanda passa a exibir uma única linha de "Saldo restante" (os produtos originais continuam guardados no banco para auditoria, só ficam ocultos da resposta da API).
- 📟 **Pagamentos via Pix com QR Code:** gera um código Pix real (padrão Bacen/EMV), com QR code para o cliente escanear.
- 🧪 **Testes automatizados:** cobertura de CRUD, validação, autenticação e dos fluxos de pagamento/fechamento de comanda.

## 💻 Tecnologias Utilizadas

- **Python 3.12**
- **Flask 2.3.0** + **Flask-SQLAlchemy** (ORM) + **Flask-Migrate** (migrations/Alembic)
- **Flask-JWT-Extended** (autenticação)
- **marshmallow** (validação de entrada)
- **PostgreSQL** (hospedado no [Supabase](https://supabase.com), plano free) — SQLite localmente por padrão, se `DATABASE_URL` não for definida
- **qrcode** + **pillow** + **pybrcode** (geração do QR code Pix)
- **gunicorn** (servidor WSGI de produção)
- **pytest** (testes automatizados)

## 🏗️ Estrutura do projeto

```
app/
├── models/     # Entidades (SQLAlchemy)
├── rotas/      # Blueprints (HTTP: validam entrada, chamam o service)
├── services/   # Regras de negócio
├── schemas/    # Validação de entrada (marshmallow)
├── banco/      # Configuração do SQLAlchemy
├── pagamentos/ # Geração do código/QR Pix
├── utils/      # Helpers (get_or_404, validação de JSON)
└── testes/     # Testes automatizados (pytest)
migrations/     # Histórico de migrations (Alembic)
```

## 🚀 Rodando o projeto localmente

1. Clone este repositório e acesse a pasta:
```
git clone git@github.com:hi-giih/bar-system.git
cd bar-system
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
```
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Copie o `.env.example` para `.env` e preencha as variáveis (veja a seção abaixo).

5. Aplique as migrations no banco:
```
export FLASK_APP=app.main   # Windows (PowerShell): $env:FLASK_APP = "app.main"
flask db upgrade
```

6. Execute a aplicação (a partir da raiz do projeto):
```
python -m app.main
```

O servidor estará disponível em: `http://127.0.0.1:5000`

## 🔑 Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta do Flask. Gere uma aleatória (`python -c "import secrets; print(secrets.token_hex(32))"`). |
| `JWT_SECRET_KEY` | Chave usada para assinar os tokens JWT. Se não definida, reusa a `SECRET_KEY`. |
| `DATABASE_URL` | Connection string do Postgres (Supabase). Em branco usa SQLite local. |
| `FLASK_DEBUG` | `true` para ligar o modo debug (só em desenvolvimento local). |
| `PIX_KEY` / `PIX_RECEIVER_NAME` / `PIX_RECEIVER_CITY` | Dados do recebedor usados para gerar o código Pix. |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH` | Credenciais do único usuário admin. O hash é gerado localmente, nunca a senha em texto puro (`generate_password_hash` do `werkzeug.security`). |

## ⚙️ Testes

Para rodar a suíte de testes (usa banco SQLite em memória, isolado — não precisa de servidor rodando nem de configuração extra):
```
pytest
```

## ☁️ Deploy

- **Banco de dados:** [Supabase](https://supabase.com) (Postgres, plano free) — use a connection string do **connection pooler** (não a conexão direta), para evitar problemas de rede/IPv6 em hosts que só suportam IPv4.
- **Aplicação:** [Render](https://render.com) (Web Service, plano free), usando `gunicorn app.main:app` como comando de start (ver `Procfile`) e rodando `flask db upgrade` a cada deploy para manter o schema atualizado.

## 🆗 Roadmap
- [x] Criar estrutura de arquivos e modelar entidades
- [x] Implementar CRUD de clientes, produtos e comandas
- [x] Integração com banco de dados (Postgres/Supabase) e migrations
- [x] Geração de QR Code Pix real
- [x] Validação de entrada e tratamento de erros centralizado
- [x] Camada de serviços
- [x] Autenticação JWT
- [x] Fechamento de comanda e pagamento parcial
- [x] Testes automatizados
- [x] Deploy em produção

## 📜 Contribuições
Projeto criado por Giovanna Santos (@hi-giih).
