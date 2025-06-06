import pytest
import requests

BASE_URL = 'http://127.0.0.1:5000'
comandas = []

def test_create_comandas():
    response_cliente = requests.get(f"{BASE_URL}/clientes/")
    assert response_cliente.status_code ==200

    new_comanda_dado={
        "data": "2025-05-22",
        "cliente_id": "2"
    }

    response_comanda = requests.post(f"{BASE_URL}/comanda", json=new_comanda_dado)

    assert response_comanda.status_code == 200
    response_json = response_comanda.json()
    comanda_id = response_json.get("id")
    assert "data" in response_json
    assert "cliente_id" in response_json

    comandas.append(comanda_id)

def test_get_comandas():
    response = requests.get(f"{BASE_URL}/comanda")
    
    assert response.status_code == 200
    response_json = response.json()
    assert "comandas" in response_json

def test_get_comanda():
    if comandas:
        comanda_id = comandas[0]
        response = requests.get(f"{BASE_URL}/comanda/{comanda_id}")

        assert response.status_code == 200
        response_json = response.json()
        assert comanda_id == response_json["id"]

def test_update_comanda():
    if comandas:
        comanda_id = comandas[0]
        payload ={
            "data": "2025-06-03",
            "cliente_id": 2
        }
        response = requests.put(f"{BASE_URL}/comanda/{comanda_id}",json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "comanda" in response_json

        response = requests.get(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"] == payload["data"]
        assert response_json["cliente_id"] == payload["cliente_id"]

def test_add_produto_comanda():
    if comandas:
        comanda_id = comandas[0]
        response = requests.get(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 200
        
        payload ={
            "produto_id": 1, 
            "quantidade": 2
        }
        response = requests.post(f"{BASE_URL}/comanda/{comanda_id}/produtos", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "comanda" in response_json
        assert "message" in response_json

def test_edita_produto_comanda():
    if comandas:
        comanda_id = comandas[0]
        produto_id = 1 
        response = requests.get(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 200

        payload ={ 
            "quantidade": 1
        }

        response = requests.patch(f"{BASE_URL}/comanda/{comanda_id}/produtos/{produto_id}", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "comanda" in response_json
        assert "message" in response_json

def test_deleta_produto_comanda():
    if comandas:
        comanda_id = comandas[0]
        produto_id = 1 
        response = requests.get(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 200

        payload ={ 
            "quantidade": 3
        }

        response = requests.delete(f"{BASE_URL}/comanda/{comanda_id}/produtos/{produto_id}", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "comanda" in response_json
        assert "message" in response_json

def test_deleta_comanda():
    if comandas:
        comanda_id = comandas[0]
        response = requests.delete(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 200

        response = requests.delete(f"{BASE_URL}/comanda/{comanda_id}")
        assert response.status_code == 404