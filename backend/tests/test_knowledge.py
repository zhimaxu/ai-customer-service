"""Tests for Phase 3 knowledge management"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["version"] == "0.2.0"


def test_list_knowledge_empty():
    resp = client.get("/api/knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert "total" in data
    assert data["total"] == 0


def test_search_knowledge_empty():
    resp = client.get("/api/knowledge/search?q=test")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert "total" in data


def test_get_nonexistent_knowledge():
    resp = client.get("/api/knowledge/nonexistent-id")
    assert resp.status_code == 404


def test_detect_supported_file_types():
    from app.services.file_converter import FileConverter
    for ext in [".md", ".txt", ".csv", ".pdf", ".docx", ".xlsx", ".png", ".jpg"]:
        assert FileConverter.detect_type(f"file{ext}") is not None
    assert FileConverter.detect_type("file.xyz") is None


def test_convert_plain_text():
    from app.services.file_converter import FileConverter
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(b"Hello world", "test.txt")
    )
    assert result == "Hello world"


def test_convert_markdown():
    from app.services.file_converter import FileConverter
    import asyncio
    content = "# Title\n\nParagraph 1\n\nParagraph 2"
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(content.encode(), "test.md")
    )
    assert result == content


def test_convert_csv_to_table():
    from app.services.file_converter import FileConverter
    import asyncio
    csv_content = "Name,Age,City\nAlice,30,Beijing\nBob,25,Shanghai"
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(csv_content.encode(), "test.csv")
    )
    assert "Name" in result
    assert "Alice" in result
    assert "|" in result  # Markdown table format
