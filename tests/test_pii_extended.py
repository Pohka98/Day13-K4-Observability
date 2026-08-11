from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app
from app.pii import scrub_text


def test_scrub_passport_vn() -> None:
    out = scrub_text("ho chieu cua toi la C1234567")
    assert "C1234567" not in out
    assert "REDACTED_PASSPORT_VN" in out


def test_chat_endpoint_never_writes_raw_pii_to_the_log_file(
    monkeypatch, tmp_path: Path
) -> None:
    """`/chat` message_preview is pre-scrubbed by summarize_text() at the call
    site, so this only proves the field is clean end-to-end — it does NOT by
    itself prove scrub_event's position in the processor chain matters. See
    test_processor_position_actually_gates_the_log_file below for that.
    """
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    email = "student@vinuni.edu.vn"
    phone = "0901234567"
    card = "4111 1111 1111 1111"

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                # kept short: summarize_text truncates message_preview to 80 chars
                "message": f"{email} {phone} {card}",
            },
        )

    assert response.status_code == 200
    raw = log_path.read_text(encoding="utf-8")
    assert email not in raw
    assert phone not in raw
    assert card not in raw
    assert "[REDACTED_EMAIL]" in raw
    assert "[REDACTED_PHONE_VN]" in raw
    assert "[REDACTED_CREDIT_CARD]" in raw


def test_processor_position_actually_gates_the_log_file(
    monkeypatch, tmp_path: Path
) -> None:
    """Every /chat payload field happens to be pre-scrubbed by summarize_text()
    before it reaches structlog, so a test built only on /chat would still
    pass even if scrub_event were removed from the processor chain entirely.
    This test logs a raw, unscrubbed value straight through the *actual*
    configured pipeline (app.main already called configure_logging() at
    import time) to prove scrub_event's registered position — before
    JsonlFileProcessor() — is what keeps PII out of the file.
    """
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    email = "leak@example.com"
    logging_config.get_logger().info(
        "raw_probe", service="test", payload={"raw": f"contact me at {email}"}
    )

    raw = log_path.read_text(encoding="utf-8")
    assert email not in raw
    assert "[REDACTED_EMAIL]" in raw


def test_no_false_positive_redaction_on_benign_numbers() -> None:
    out = scrub_text("version 4111 of the doc, released in room 2024")
    assert "4111" in out
    assert "2024" in out
    assert "REDACTED" not in out


def test_no_false_positive_end_to_end(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "version 4111 of the doc",
            },
        )

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    request_event = next(event for event in events if event["event"] == "request_received")
    assert "REDACTED" not in request_event["payload"]["message_preview"]
    assert "4111" in request_event["payload"]["message_preview"]
