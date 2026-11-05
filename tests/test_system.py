"""Meaningful integration tests: real weights, token safety, and API validation."""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.evaluation import distance


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_actual_neural_inference(client):
    response = client.post("/api/transliterate", json={"text": "namaste dost"})
    assert response.status_code == 200
    data = response.json()
    assert data["output"] == "नमस्ते दोस्त"
    assert data["model"] == "AI4Bharat IndicXlit v1.0"
    assert len(data["tokens"][0]["alternatives"]) >= 2


def test_protected_content_inside_sentence(client):
    text = (
        "namaste @mera #padhai https://example.com/a?b=1 student@example.com 10:30 नमस्ते"
    )
    data = client.post("/api/transliterate", json={"text": text}).json()
    for protected in [
        "@mera",
        "#padhai",
        "https://example.com/a?b=1",
        "student@example.com",
        "10:30",
        "नमस्ते",
    ]:
        assert protected in data["output"]
    assert data["output"].startswith("नमस्ते ")
    assert "".join(t["source"] for t in data["tokens"]) == text


def test_switching_policy(client):
    text = "project ki deadline kal hai."
    kept = client.post("/api/transliterate", json={"text": text}).json()["output"]
    converted = client.post(
        "/api/transliterate", json={"text": text, "preserve_english": False}
    ).json()["output"]
    assert kept.startswith("project की deadline")
    assert "project" not in converted and "deadline" not in converted


@pytest.mark.parametrize(
    "body",
    [
        {"text": ""},
        {"text": "   "},
        {"text": "a" * 3001},
        {"text": "hello", "language": "xx"},
    ],
)
def test_reject_bad_input(client, body):
    assert client.post("/api/transliterate", json=body).status_code == 422


def test_preserve_whitespace_and_native(client):
    text = "नमस्ते!\n\n  namaste\t123"
    assert (
        client.post("/api/transliterate", json={"text": text}).json()["output"]
        == "नमस्ते!\n\n  नमस्ते\t123"
    )


def test_metrics_known_edit_distances():
    assert distance("abc", "axc") == 1
    assert distance("", "ab") == 2
    assert distance(["one", "two"], ["one"]) == 1


def test_model_health_and_suite(client):
    health = client.get("/api/health").json()
    assert health["transliteration"]["ready"] is True
    report = client.get("/api/evaluation").json()
    assert report["test_count"] == 40
    assert len({r["id"] for r in report["results"]}) == 40


def test_generation_request_validation(client):
    assert (
        client.post("/api/generate", json={"text": "hi", "task": "unknown"}).status_code
        == 422
    )
    assert (
        client.post("/api/generate", json={"text": "", "task": "polish"}).status_code
        == 422
    )
