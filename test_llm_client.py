"""Offline unit tests for llm_client.py's guard clauses - no network calls."""
import pytest

from llm_client import AnthropicClient, AskSageClient, OpenAIClient, get_client


def test_anthropic_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        AnthropicClient()


def test_openai_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        OpenAIClient()


def test_asksage_client_requires_email_and_key(monkeypatch):
    monkeypatch.delenv("ASKSAGE_EMAIL", raising=False)
    monkeypatch.delenv("ASKSAGE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ASKSAGE_EMAIL"):
        AskSageClient()


def test_get_client_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_client("not-a-real-provider")
