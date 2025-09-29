from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_health_check_success(test_client: TestClient, db_session: Session):
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "postgres_connection": "ok"}