from app import create_app
from app.banco.database import db

app = create_app()

with app.app_context():
    db.drop_all()
    print("Tabelas apagadas")
    db.create_all()
    print("Tabelas criadas novamente")
