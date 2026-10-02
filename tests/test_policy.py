import pytest
from app.detector import InjectionDetector
from app.policy import evaluate_payload
from app.audit import init_db
from config import settings

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = tmp_path / "test_audit.db"
    original_db_path = settings.db_path
    settings.db_path = str(test_db)
    init_db()
    yield
    settings.db_path = original_db_path

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


def test_policy_allow_benign():
    detector = MockDetector()
    settings.threshold = 0.85
    settings.policy_mode = "block"
    result = evaluate_payload(detector, "hello world this is safe", "test")
    assert result["action"] == "allowed"
    assert result["max_score"] == 0.1

def test_policy_block_malicious():
    detector = MockDetector()
    settings.threshold = 0.85
    settings.policy_mode = "block"
    result = evaluate_payload(detector, "this is bad payload", "test")
    assert result["action"] == "blocked"
    assert result["max_score"] == 0.9
    assert result["offending_chunk_index"] == 0

def test_policy_flag_mode():
    detector = MockDetector()
    settings.threshold = 0.95
    settings.policy_mode = "flag"
    result = evaluate_payload(detector, "this is bad payload", "test")
    assert result["action"] == "flagged"
    assert result["max_score"] == 0.9
    assert result["offending_chunk_index"] == 0
