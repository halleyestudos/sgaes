from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_mvp_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "SGA-EDU" in response.text
    assert "MVP" in response.text
