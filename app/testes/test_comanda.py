import pytest
import requests

BASE_URL = 'http://127.0.0.1:5000'
comandas = []

def test_create_comandas():
    response_cliente = requests.get(f"{BASE_URL}/clientes/")
    assert response_cliente.status_code ==200

    new_comanda_dado={
        "data": "2025-05-22",
        "cliente_id": "1"
    }

    response_comanda = requests.post(f"{BASE_URL}/comanda", json=new_comanda_dado)

    assert response_comanda.status_code == 200
    response_json = response_comanda.json()
    comanda_id = response_json.get("id")
    assert "data" in response_json
    assert "cliente_id" in response_json

    comandas.append(comanda_id)