import pytest
import requests

BASE_URL = 'http://127.0.0.1:5000'
clientes = []

def  test_create_clientes():
    new_cliente_dado ={
        "nome": "Usuario",
        "telefone": "123456789"
    }
    response = requests.post(f"{BASE_URL}/clientes/", json=new_cliente_dado)

    assert response.status_code ==200
    response_json = response.json()  
    cliente_id = response_json.get("id")
    assert "message" in response_json
    assert "cliente" in response_json
    assert "id" in response_json 
    
    clientes.append(cliente_id)

def test_get_clientes():
    response = requests.get(f"{BASE_URL}/clientes/")

    assert response.status_code ==200
    response_json = response.json()
    assert "clientes" in response_json

def test_get_cliente():
    if clientes:
        cliente_id = clientes[0]
        response = requests.get(f"{BASE_URL}/clientes/{cliente_id}")
        
        assert response.status_code == 200
        response_json = response.json()  
        assert cliente_id == response_json["id"]

def test_update_cliente():
    if clientes:
        cliente_id = clientes[0]
        payload ={
                    "nome": "Giovanna",
                    "telefone": "987654321"
                }
        response = requests.put(f"{BASE_URL}/clientes/{cliente_id}", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "message" in response_json
        assert "cliente" in response_json

        response = requests.get(f"{BASE_URL}/clientes/{cliente_id}")
        assert response.status_code == 200
        response_json = response.json()  
        assert response_json["nome"] == payload["nome"]
        assert response_json["telefone"] == payload["telefone"]

def test_delete_cliente():
    if clientes:
        cliente_id = clientes[0]
        response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}")
        assert response.status_code == 200

        response = requests.get(f"{BASE_URL}/clientes/{cliente_id}")
        assert response.status_code == 404