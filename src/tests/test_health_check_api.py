def test_health_check(api_client):  # pytest에 의해 conftest의 api_client가 주입됨.
    """
    health check API 성공 테스트.
    """

    response = api_client.get("")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
