"""Sprint 1 — handlers unit tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers import (
    PROCESSING_TEXT,
    TRANSCRIPTION_ERROR_TEXT,
    UNSUPPORTED_TEXT,
    WELCOME_TEXT,
    cmd_start,
    handle_audio,
    handle_unsupported,
    handle_voice,
)


def make_message():
    """Return a mock aiogram Message with async answer()."""
    msg = MagicMock()
    msg.answer = AsyncMock()
    return msg


def run(coro):
    return asyncio.run(coro)


# --- /start ---

def test_start_replies_welcome():
    msg = make_message()
    run(cmd_start(msg))
    msg.answer.assert_called_once_with(WELCOME_TEXT)


# --- unsupported fallback ---

def test_unsupported_replies_hint():
    msg = make_message()
    run(handle_unsupported(msg))
    msg.answer.assert_called_once_with(UNSUPPORTED_TEXT)


# --- voice handler ---

def _make_voice_msg(audio_data=b"fake_audio_data"):
    msg = make_message()
    mock_file = MagicMock()
    mock_file.file_path = "voice/file.oga"
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=mock_file)
    fake_bytes = MagicMock()
    fake_bytes.read.return_value = audio_data
    msg.bot.download_file = AsyncMock(return_value=fake_bytes)
    msg.voice = MagicMock()
    msg.voice.file_id = "test_voice_id"
    return msg


def _make_audio_msg(audio_data=b"fake_mp3_data"):
    msg = make_message()
    mock_file = MagicMock()
    mock_file.file_path = "audio/file.mp3"
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=mock_file)
    fake_bytes = MagicMock()
    fake_bytes.read.return_value = audio_data
    msg.bot.download_file = AsyncMock(return_value=fake_bytes)
    msg.audio = MagicMock()
    msg.audio.file_id = "test_audio_id"
    return msg


def test_voice_replies_processing_then_text():
    msg = _make_voice_msg()
    with patch("handlers.transcriber.transcribe", return_value="Привет мир"):
        run(handle_voice(msg))
    calls = [c.args[0] for c in msg.answer.call_args_list]
    assert calls[0] == PROCESSING_TEXT
    assert calls[1] == "Привет мир"


def test_voice_error_sends_error_text():
    msg = _make_voice_msg()
    with patch("handlers.transcriber.transcribe", side_effect=Exception("API down")):
        run(handle_voice(msg))
    calls = [c.args[0] for c in msg.answer.call_args_list]
    assert calls[0] == PROCESSING_TEXT
    assert calls[1] == TRANSCRIPTION_ERROR_TEXT


def test_voice_silent_sends_value_error_text():
    msg = _make_voice_msg()
    err = ValueError("Не удалось распознать речь — запись слишком тихая или пустая.")
    with patch("handlers.transcriber.transcribe", side_effect=err):
        run(handle_voice(msg))
    calls = [c.args[0] for c in msg.answer.call_args_list]
    assert calls[1] == str(err)


def test_voice_does_not_save_to_disk():
    """Bytes stay in memory — no file open calls."""
    msg = _make_voice_msg(b"x" * 1024)
    with patch("handlers.transcriber.transcribe", return_value="ok"), \
         patch("builtins.open") as mock_open:
        run(handle_voice(msg))
        mock_open.assert_not_called()


# --- audio handler ---

def test_audio_replies_processing_then_text():
    msg = _make_audio_msg()
    with patch("handlers.transcriber.transcribe", return_value="Текст из MP3"):
        run(handle_audio(msg))
    calls = [c.args[0] for c in msg.answer.call_args_list]
    assert calls[0] == PROCESSING_TEXT
    assert calls[1] == "Текст из MP3"


def test_audio_error_sends_error_text():
    msg = _make_audio_msg()
    with patch("handlers.transcriber.transcribe", side_effect=Exception("timeout")):
        run(handle_audio(msg))
    calls = [c.args[0] for c in msg.answer.call_args_list]
    assert calls[1] == TRANSCRIPTION_ERROR_TEXT


# --- constants sanity ---

def test_constants_not_empty():
    assert len(WELCOME_TEXT) > 10
    assert len(PROCESSING_TEXT) > 5
    assert len(UNSUPPORTED_TEXT) > 10
