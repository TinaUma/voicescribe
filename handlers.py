import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import transcriber

logger = logging.getLogger(__name__)

router = Router()

WELCOME_TEXT = (
    "Привет! Я VoiceScribe — расшифровываю голосовые сообщения и аудиофайлы.\n\n"
    "Просто пришли голосовое сообщение или аудиофайл (MP3, M4A, WAV) — "
    "и я верну текст."
)

PROCESSING_TEXT = "Принял, обрабатываю..."

UNSUPPORTED_TEXT = (
    "Понимаю только голосовые и аудиофайлы. "
    "Пришли голосовое — расшифрую."
)

TRANSCRIPTION_ERROR_TEXT = "Не удалось расшифровать аудио. Попробуй ещё раз."


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)


@router.message(F.voice)
async def handle_voice(message: Message) -> None:
    await message.answer(PROCESSING_TEXT)
    file = await message.bot.get_file(message.voice.file_id)
    audio_bytes = await message.bot.download_file(file.file_path)
    data: bytes = audio_bytes.read()
    logger.info("Voice received: %d bytes, file_id=%s", len(data), message.voice.file_id)
    try:
        text = transcriber.transcribe(data)
        await message.answer(text)
    except ValueError as e:
        await message.answer(str(e))
    except Exception:
        logger.exception("Transcription failed for voice file_id=%s", message.voice.file_id)
        await message.answer(TRANSCRIPTION_ERROR_TEXT)


@router.message(F.audio)
async def handle_audio(message: Message) -> None:
    await message.answer(PROCESSING_TEXT)
    file = await message.bot.get_file(message.audio.file_id)
    audio_bytes = await message.bot.download_file(file.file_path)
    data: bytes = audio_bytes.read()
    logger.info("Audio received: %d bytes, file_id=%s", len(data), message.audio.file_id)
    try:
        text = transcriber.transcribe(data)
        await message.answer(text)
    except ValueError as e:
        await message.answer(str(e))
    except Exception:
        logger.exception("Transcription failed for audio file_id=%s", message.audio.file_id)
        await message.answer(TRANSCRIPTION_ERROR_TEXT)


@router.message()
async def handle_unsupported(message: Message) -> None:
    await message.answer(UNSUPPORTED_TEXT)
