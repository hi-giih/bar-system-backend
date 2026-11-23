# 📑 Sistema de Comandas — Backend

API backend em Python (Flask) para controle de consumo em bares, restaurantes, salões e eventos. Permite cadastrar clientes e produtos, abrir comandas individuais, registrar o que foi consumido e receber pagamentos (Pix com QR Code, cartão ou dinheiro), sempre mostrando o total e o saldo restante de cada comanda.

O código é organizado em camadas: rotas (Blueprints), serviços (regras de negócio) e schemas de validação.

## ⚙️ Funcionalidades

- 🔐 **Autenticação:** login único (admin) via JWT, válido por 24h. Todas as rotas exigem token, exceto `/auth/login`, `/health` e o disparo do relatório semanal (que usa um segredo próprio).
- 👤 **Clientes:** CRUD (nome e telefone).
- 🛒 **Produtos:** CRUD (nome, preço e ícone: `drink`, `bebida` ou `comida`).
- 🧾 **Comandas:** criação por cliente, adição, alteração e remoção de produtos, com cálculo automático do total.
- 🔒 **Fechamento:** só é possível fechar uma comanda com saldo zerado. Depois de fechada ela não aceita alterações, mas pode ser deletada.
- 💰 **Pagamento parcial:** ao confirmar um pagamento que não cobre o total, a comanda passa a exibir uma única linha de "Saldo restante". Os produtos originais continuam no banco para auditoria e só ficam ocultos na resposta da API.
- 📟 **Formas de pagamento:** `pix`, `cartao` e `dinheiro`. No Pix é gerado um código real (padrão Bacen/EMV) com QR Code.
- 📊 **Relatório de comandas:** download de planilha `.xlsx` e envio semanal por e-mail (via Resend), disparado por GitHub Actions.
- ❤️ **Health check:** `GET /health` consulta o banco, o que também evita a pausa do Supabase por inatividade.
- 🧪 **Testes automatizados:** autenticação, CRUDs, validação, pagamentos, fechamento de comanda, relatório e e-mail.

## 💻 Tecnologias

- **Python 3.12**
- **Flask 2.3** + **Flask-SQLAlchemy** + **Flask-Migrate** (Alembic)
- **Flask-JWT-Extended** (autenticação) e **Flask-Cors**
- **marshmallow** (validação de entrada)
- **PostgreSQL** ([Supabase](https://supabase.com), plano free) em produção; SQLite local se `DATABASE_URL` não for definida
- **qrcode**, **pillow** e **pybrcode** (QR Code Pix)
- **openpyxl** (planilha do relatório) e **requests** (API da Resend)
- **gunicorn** (servidor WSGI de produção)
- **pytest** (testes)

## 🏗️ Estrutura do projeto

```
app/
├── models/      # Entidades (SQLAlchemy)
├── rotas/       # Blueprints (HTTP: validam entrada e chamam o service)
├── services/    # Regras de negócio (comandas, pagamentos, relatório, e-mail...)
├── schemas/     # Validação de entrada (marshmallow)
├── banco/       # Configuração do SQLAlchemy
├── pagamentos/  # Geração do código/QR Pix
├── utils/       # Helpers (get_or_404, validação de JSON)
├── testes/      # Testes automatizados (pytest)
├── config.py    # Configuração via variáveis de ambiente
└── main.py      # Ponto de entrada
migrations/      # Histórico de migrations (Alembic)
.github/workflows/  # keep-alive e relatório semanal
```

## 🚀 Rodando localmente

1. Clone o repositório:
```bash
git clone https://github.com/hi-giih/bar-system-backend.git
cd bar-system-backend
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
```
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Copie `.env.example` para `.env` e preencha as variáveis.

5. Aplique as migrations:
```bash
export FLASK_APP=app.main   # PowerShell: $env:FLASK_APP = "app.main"
flask db upgrade
```

6. Inicie a aplicação (a partir da raiz do projeto):
```bash
python -m app.main
```

O servidor sobe em `http://127.0.0.1:5000`.

> `reset_db.py` apaga **todas** as tabelas e as recria. Use apenas em desenvolvimento.

## 🔌 Endpoints

Todos exigem `Authorization: Bearer <token>`, salvo indicação.

| Recurso | Rotas |
|---|---|
| **Auth** | `POST /auth/login` *(público)* |
| **Health** | `GET /health` *(público)* |
| **Clientes** | `POST /clientes/` · `GET /clientes/` · `GET/PUT/DELETE /clientes/<id>` |
| **Produtos** | `POST /produtos/` · `GET /produtos/` · `GET/PUT/DELETE /produtos/<id>` |
| **Comandas** | `POST /comanda/` · `GET /comanda/` · `GET/PUT/DELETE /comanda/<id>` |
| | `POST /comanda/<id>/produtos` · `PATCH/DELETE /comanda/<id>/produtos/<produto_id>` |
| | `POST /comanda/<id>/fechar` |
| **Pagamentos** | `POST /pagamento/` (cria; `forma_pagamento`: `pix`, `cartao` ou `dinheiro`) · `POST /pagamento/confirmacao` |
| **Relatórios** | `GET /relatorios/comandas` (baixa a planilha `.xlsx`) |
| | `POST /relatorios/comandas/enviar-email` *(autenticado pelo header `X-Cron-Secret`)* |

## 🧪 Testes

Usam SQLite em memória, sem precisar de servidor ou configuração extra:
```bash
pytest
```

## ☁️ Deploy

- **Banco:** [Supabase](https://supabase.com) (Postgres, plano free). Use a connection string do **connection pooler**, não a conexão direta, para evitar problemas de rede/IPv6 em hosts só IPv4.
- **Aplicação:** [Render](https://render.com) (Web Service, plano free), com `gunicorn app.main:app` como comando de start (ver `Procfile`) e `flask db upgrade` a cada deploy.

### Automações (GitHub Actions)

| Workflow | Frequência | O que faz |
|---|---|---|
| `keep-alive.yml` | A cada 10 min | Chama `/health` para o Render (plano free) não hibernar. |
| `relatorio-semanal.yml` | Segundas, 08:00 (Brasília) | Chama `POST /relatorios/comandas/enviar-email` e envia a planilha por e-mail. |

Para o relatório semanal funcionar, cadastre o mesmo valor de `RELATORIO_CRON_SECRET` como secret do repositório (*Settings → Secrets and variables → Actions*).

> O envio de e-mail usa a API HTTP da Resend porque o Render bloqueia conexões SMTP de saída.

## 🆗 Roadmap

- [x] Estrutura de arquivos e modelagem das entidades
- [x] CRUD de clientes, produtos e comandas
- [x] Banco Postgres (Supabase) e migrations
- [x] QR Code Pix real
- [x] Validação de entrada e tratamento centralizado de erros
- [x] Camada de serviços
- [x] Autenticação JWT
- [x] Fechamento de comanda e pagamento parcial
- [x] Formas de pagamento (Pix, cartão, dinheiro)
- [x] Relatório semanal de comandas por e-mail
- [x] Testes automatizados
- [x] Deploy em produção

## 📜 Autoria

Projeto criado por Giovanna Santos ([@hi-giih](https://github.com/hi-giih)).
