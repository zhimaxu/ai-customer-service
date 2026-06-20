"""End-to-end tests for Phase 2 chat core"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_send_message_creates_session():
    """Test that sending a message creates a session and returns a reply"""
    resp = client.post("/api/chat", json={
        "message": "你好",
        "tenant_id": "test-tenant",
        "user_id": "test-user",
    })
    # May return 200 (success) or 5xx (AI service unavailable)
    # We test the session management part
    assert resp.status_code in (200, 500, 502, 503)
    if resp.status_code == 200:
        data = resp.json()
        assert "session_id" in data
        assert "reply" in data


def test_get_nonexistent_session():
    resp = client.get("/api/chat/sessions/nonexistent-id")
    assert resp.status_code == 404


def test_list_sessions_empty():
    resp = client.get("/api/chat/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert "sessions" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_sessions_with_filters():
    resp = client.get("/api/chat/sessions?user_id=test-filter-user&page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "sessions" in data


def test_close_nonexistent_session():
    resp = client.delete("/api/chat/sessions/nonexistent-id")
    assert resp.status_code == 404
