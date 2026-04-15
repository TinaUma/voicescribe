"""Sprint 1 — handlers unit tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers import (
    PROCESSING_TEXT,
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

def test_voice_replies_processing():
    msg = make_message()
    # mock voice file download chain
    mock_file = MagicMock()
    mock_file.file_path = "voice/file.oga"
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=mock_file)
    fake_bytes = MagicMock()
    fake_bytes.read.return_value = b"fake_audio_data"
    msg.bot.download_file = AsyncMock(return_value=fake_bytes)
    msg.voice = MagicMock()
    msg.voice.file_id = "test_voice_id"

    run(handle_voice(msg))

    msg.answer.assert_called_once_with(PROCESSING_TEXT)


def test_voice_does_not_save_to_disk():
    """Bytes stay in memory — no file open calls."""
    msg = make_message()
    mock_file = MagicMock()
    mock_file.file_path = "voice/file.oga"
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=mock_file)
    fake_bytes = MagicMock()
    fake_bytes.read.return_value = b"x" * 1024
    msg.bot.download_file = AsyncMock(return_value=fake_bytes)
    msg.voice = MagicMock()
    msg.voice.file_id = "vid"

    with patch("builtins.open") as mock_open:
        run(handle_voice(msg))
        mock_open.assert_not_called()


# --- audio handler ---

def test_audio_replies_processing():
    msg = make_message()
    mock_file = MagicMock()
    mock_file.file_path = "audio/file.mp3"
    msg.bot = AsyncMock()
    msg.bot.get_file = AsyncMock(return_value=mock_file)
    fake_bytes = MagicMock()
    fake_bytes.read.return_value = b"fake_mp3_data"
    msg.bot.download_file = AsyncMock(return_value=fake_bytes)
    msg.audio = MagicMock()
    msg.audio.file_id = "test_audio_id"

    run(handle_audio(msg))

    msg.answer.assert_called_once_with(PROCESSING_TEXT)


# --- constants sanity ---

def test_constants_not_empty():
    assert len(WELCOME_TEXT) > 10
    assert len(PROCESSING_TEXT) > 5
    assert len(UNSUPPORTED_TEXT) > 10
