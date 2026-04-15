"""Sprint 2 — transcriber unit tests (Groq API mocked)."""
import os
from unittest.mock import MagicMock, patch

import pytest

import transcriber


def make_groq_result(text):
    result = MagicMock()
    result.text = text
    return result


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key-fake")


@patch("transcriber.Groq")
def test_transcribe_returns_text(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("Привет мир")

    result = transcriber.transcribe(b"fake_ogg_bytes")

    assert result == "Привет мир"


@patch("transcriber.Groq")
def test_transcribe_strips_whitespace(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("  текст с пробелами  ")

    result = transcriber.transcribe(b"fake_ogg_bytes")

    assert result == "текст с пробелами"


@patch("transcriber.Groq")
def test_transcribe_raises_on_api_error(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.side_effect = Exception("Connection error")

    with pytest.raises(Exception, match="Connection error"):
        transcriber.transcribe(b"fake_ogg_bytes")


@patch("transcriber.Groq")
def test_transcribe_raises_on_empty_response(mock_groq_cls):
    """Groq вернул 200, но текст пустой — тишина или очень тихое сообщение."""
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("")

    with pytest.raises(ValueError, match="тихая"):
        transcriber.transcribe(b"silence_bytes")


@patch("transcriber.Groq")
def test_transcribe_raises_on_whitespace_only_response(mock_groq_cls):
    """Groq вернул только пробелы — считаем пустым."""
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("   \n  ")

    with pytest.raises(ValueError):
        transcriber.transcribe(b"near_silence_bytes")


@patch("transcriber.Groq")
def test_transcribe_uses_auto_language(mock_groq_cls):
    """language=None передаётся в Groq — без хардкода языка."""
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("hello")

    transcriber.transcribe(b"audio")

    call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
    assert call_kwargs.get("language") is None


@patch("transcriber.Groq")
def test_transcribe_reads_api_key_from_env(mock_groq_cls, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "my-secret-key")
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = make_groq_result("ok")

    transcriber.transcribe(b"audio")

    mock_groq_cls.assert_called_once_with(api_key="my-secret-key")
