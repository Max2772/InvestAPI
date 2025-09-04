from fastapi.testclient import TestClient

from main import app

client = TestClient(app, base_url="http://127.0.0.1:8000")

def test_get():
    response = client.get('/')
    data = response.json()
    assert response.status_code == 200
    assert data == ["Nothing here, look docs"]

if __name__ == '__main__':
    test_get()