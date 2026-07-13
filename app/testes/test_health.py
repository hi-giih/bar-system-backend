def test_health_nao_exige_login(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_health_consulta_o_banco(client):
    """O health check roda uma query real, tanto para checagem de saude
    quanto para servir de "ping" que mantem o banco (Supabase free tier)
    ativo quando chamado periodicamente por um servico externo."""
    r = client.get("/health")
    assert r.get_json()["database"] == "ok"
