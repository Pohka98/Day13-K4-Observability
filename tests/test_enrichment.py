from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app, agent
from app.pii import hash_user_id

def test_enrichment_fields_exist(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "hello",
            },
        )

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_events = [e for e in events if e.get("service") == "api"]
    
    request_received = next(e for e in api_events if e["event"] == "request_received")
    response_sent = next(e for e in api_events if e["event"] == "response_sent")
    
    expected_fields = ["user_id_hash", "session_id", "feature", "model", "env"]
    for field in expected_fields:
        assert field in request_received
        assert field in response_sent


def test_user_id_is_hashed_not_raw(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "hello",
            },
        )

    raw_logs = log_path.read_text(encoding="utf-8")
    assert "student-01" not in raw_logs
    assert hash_user_id("student-01") in raw_logs


def test_enrichment_values_match_source(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "hello",
            },
        )

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    api_events = [e for e in events if e.get("service") == "api"]
    
    for event in api_events:
        if event["event"] in ("request_received", "response_sent"):
            assert event["feature"] == "qa"
            assert event["model"] == agent.model
