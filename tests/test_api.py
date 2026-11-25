from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.endpoints import documents
from app.infrastructure import registry
from app.main import app

SAMPLE = Path("tests/test_docs/sample.pdf")


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Write uploads and indexes to a temporary folder, not into the project
    monkeypatch.setattr(documents, "UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setattr(registry, "DATA_DIR", str(tmp_path / "data"))
    (tmp_path / "uploads").mkdir()
    return TestClient(app)


def upload(client):
    with SAMPLE.open("rb") as f:
        return client.post("/upload", files={"file": ("sample.pdf", f, "application/pdf")})


def test_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/chat").status_code == 200


def test_upload_returns_doc_info(client):
    res = upload(client)
    assert res.status_code == 200
    data = res.json()
    assert data["intro_page_count"] == 2   # pages i and ii
    assert data["page_count"] == 5


def test_upload_rejects_non_pdf(client):
    res = client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")})
    assert res.status_code == 400


def test_ask_finds_relevant_page(client):
    doc_id = upload(client).json()["doc_id"]
    res = client.post("/ask", json={"doc_id": doc_id, "query": "How was chlorophyll measured?"})
    assert res.status_code == 200
    sources = res.json()["sources"]
    assert sources, "expected at least one matching page"
    assert sources[0]["label"] == "2"  # Chapter 2 Method


def test_ask_unknown_document(client):
    res = client.post("/ask", json={"doc_id": "0" * 32, "query": "anything"})
    assert res.status_code == 404
