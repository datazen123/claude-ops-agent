"""Offline unit tests for mock_crm.py - no API key or network needed."""
import mock_crm


def test_upsert_and_triage_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(mock_crm, "DB_PATH", tmp_path / "test_crm.db")

    mock_crm.upsert_ticket("T-1", "Test subject")
    result = mock_crm.triage_ticket("T-1", "billing", "high", "We'll look into this.")

    assert "T-1" in result
    assert "high" in result

    rows = mock_crm.list_tickets()
    assert len(rows) == 1
    assert rows[0]["ticket_id"] == "T-1"
    assert rows[0]["category"] == "billing"
    assert rows[0]["priority"] == "high"
    assert rows[0]["status"] == "triaged"


def test_upsert_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(mock_crm, "DB_PATH", tmp_path / "test_crm.db")

    mock_crm.upsert_ticket("T-1", "Original subject")
    mock_crm.upsert_ticket("T-1", "Should not overwrite")

    rows = mock_crm.list_tickets()
    assert len(rows) == 1
    assert rows[0]["subject"] == "Original subject"


def test_reset_db_clears_tickets(tmp_path, monkeypatch):
    monkeypatch.setattr(mock_crm, "DB_PATH", tmp_path / "test_crm.db")

    mock_crm.upsert_ticket("T-1", "Subject")
    mock_crm.reset_db()

    assert mock_crm.list_tickets() == []


def test_triage_tool_schema_has_required_fields():
    schema = mock_crm.TRIAGE_TOOL_SCHEMA
    assert schema["name"] == "triage_ticket"
    required = schema["input_schema"]["required"]
    assert set(required) == {"ticket_id", "category", "priority", "draft_response"}
