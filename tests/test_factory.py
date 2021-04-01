from app import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_response(client):
    response = client.get("/login")
    assert response.status_code == 200
