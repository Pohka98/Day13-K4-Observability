from __future__ import annotations

import ast
import inspect
import json
import re
import textwrap
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app
from app.middleware import CorrelationIdMiddleware


def _chat_payload(user_id: str = "student-01", session_id: str = "session-01") -> dict[str, str]:
    return {
        "user_id": user_id,
        "session_id": session_id,
        "feature": "qa",
        "message": "Explain monitoring observability",
    }


def _read_events(log_path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _chat_events(log_path: Path) -> list[dict]:
    return [
        event
        for event in _read_events(log_path)
        if event.get("event") in {"request_received", "response_sent"}
    ]


def _dispatch_call_order() -> list[str]:
    source = textwrap.dedent(inspect.getsource(CorrelationIdMiddleware.dispatch))
    tree = ast.parse(source)
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node.func.id)
    return calls


def test_generates_request_id_when_client_omits_header(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post("/chat", json=_chat_payload())

    assert response.status_code == 200
    correlation_id = response.headers["x-request-id"]
    assert re.fullmatch(r"req-[0-9a-f]{8}", correlation_id)
    assert response.json()["correlation_id"] == correlation_id
    assert float(response.headers["x-response-time-ms"]) >= 0


def test_respects_client_request_id_and_writes_it_to_logs(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "req-testcase"},
            json=_chat_payload(),
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-testcase"
    assert response.json()["correlation_id"] == "req-testcase"

    events = _chat_events(log_path)
    assert {event["event"] for event in events} == {"request_received", "response_sent"}
    assert {event["correlation_id"] for event in events} == {"req-testcase"}


def test_generates_unique_request_ids_for_sequential_requests(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        first = client.post("/chat", json=_chat_payload(user_id="student-01", session_id="s1"))
        second = client.post("/chat", json=_chat_payload(user_id="student-02", session_id="s2"))

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.headers["x-request-id"] != second.headers["x-request-id"]
    assert first.json()["correlation_id"] != second.json()["correlation_id"]


def test_clears_previous_contextvars_before_handling_next_request(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        chat_response = client.post(
            "/chat",
            headers={"x-request-id": "req-chat"},
            json=_chat_payload(user_id="student-leak-check", session_id="session-leak-check"),
        )
        incident_response = client.post(
            "/incidents/rag_slow/disable",
            headers={"x-request-id": "req-control"},
        )

    assert chat_response.status_code == 200
    assert incident_response.status_code == 200

    incident_event = next(
        event for event in _read_events(log_path) if event["event"] == "incident_disabled"
    )
    assert incident_event["correlation_id"] == "req-control"
    assert "user_id_hash" not in incident_event
    assert "session_id" not in incident_event
    assert "feature" not in incident_event


def test_middleware_clears_contextvars_before_binding_request_context() -> None:
    calls = _dispatch_call_order()

    assert "clear_contextvars" in calls
    assert "bind_contextvars" in calls
    assert calls.index("clear_contextvars") < calls.index("bind_contextvars")
