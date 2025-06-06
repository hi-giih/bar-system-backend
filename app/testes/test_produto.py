import pytest
import requests

BASE_URL = 'http://127.0.0.1:5000'
produtos = []

def test_create_produtos():
    new_produto_dado ={
        "nome": "Agua",
        "preco": "1.10"
    }
    response = requests.post(f"{BASE_URL}/produtos", json=new_produto_dado)

    assert response.status_code == 200
    response_json = response.json()
    produto_id = response_json.get("id")
    assert "message" in response_json
    assert "produto" in response_json
    assert "id" in response_json

    produtos.append(produto_id)

def test_get_produtos():
    response = requests.get(f"{BASE_URL}/produtos")

    assert response.status_code ==200
    response_json = response.json()
    assert "produtos" in response_json

def test_get_produto():
    if produtos:
        produto_id = produtos[0]
        response = requests.get(f"{BASE_URL}/produtos/{produto_id}")

        assert response.status_code == 200
        response_json = response.json()
        assert produto_id == response_json["id"]

def test_update_produto():
    if produtos:
        produto_id = produtos[0]
        payload ={
                    "nome": "Cerveja",
                    "preco": "10.00"
                }
        response = requests.put(f"{BASE_URL}/produtos/{produto_id}", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert "message" in response_json
        assert "produto" in response_json

        response = requests.get(f"{BASE_URL}/produtos/{produto_id}")
        assert response.status_code == 200
        response_json =  response.json()
        assert response_json["nome"] == payload["nome"]
        assert float(response_json["preco"]) == float(payload["preco"])

def test_delete_produto():
    if produtos:
        produto_id = produtos[0]
        response = requests.delete(f"{BASE_URL}/produtos/{produto_id}")
        assert response.status_code == 200

        response = requests.get(f"{BASE_URL}/produtos/{produto_id}")
        assert response.status_code == 404