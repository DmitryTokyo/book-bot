
def test_check(client):
    response = client.get('/')
    assert response.status_code == 200
