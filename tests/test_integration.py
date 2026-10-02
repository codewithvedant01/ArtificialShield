import pytest
from fastapi.testclient import TestClient
from app.gateway import app, get_detector
from config import settings
from app.audit import init_db

class MockDetector:
    def score_segments(self, segments):
        class MockItem:
            def __init__(self, text, score, label):
                self.text = text
                self.score = score
                self.label = label
        items = []
        max_score = 0.0
        for seg in segments:
            score = 0.9 if "bad" in seg else 0.1
            items.append(MockItem(seg, score, "INJECTION" if score >= 0.5 else "SAFE"))
            max_score = max(max_score, score)
        return items, max_score


@pytest.fixture(autouse=True)
def setup_mock_detector(tmp_path):
    import app.gateway
    app.gateway.get_detector = lambda: MockDetector()
    original_url = settings.backend_url
    original_db = settings.db_path
    
    settings.backend_url = "" # Mock upstream
    settings.db_path = str(tmp_path / "test_integration.db")
    
    init_db()
    yield
    settings.backend_url = original_url
    settings.db_path = original_db
    app.dependency_overrides = {}

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model": settings.model_name}

def test_chat_completion_allow():
    with TestClient(app) as client:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "hello world"}
            ]
        }
        response = client.post("/v1/chat/completions", json=payload)
        assert response.status_code == 200

def test_chat_completion_block():
    with TestClient(app) as client:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "this is bad payload"}
            ]
        }
        response = client.post("/v1/chat/completions", json=payload)
        assert response.status_code == 403
        data = response.json()["detail"]
        assert data["error"] == "prompt_injection_detected"
        assert data["max_score"] == 0.9
        assert data["offending_chunk_index"] == 0
