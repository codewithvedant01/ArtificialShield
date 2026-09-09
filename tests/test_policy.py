from app.gateway import _decision
from config import settings


def test_decision_blocked(monkeypatch):
    monkeypatch.setattr(settings, "threshold", 0.85)
    assert _decision(0.91) == "blocked"


def test_decision_allowed(monkeypatch):
    monkeypatch.setattr(settings, "threshold", 0.85)
    monkeypatch.setattr(settings, "policy_mode", "block")
    assert _decision(0.12) == "allowed"
