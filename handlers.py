import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import exporter
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
NO_TRANSCRIPTION_TEXT = "Нет сохранённой транскрипции. Сначала пришли голосовое или аудио."

# Last transcription per user: {user_id: (text, datetime)}
user_texts: dict[int, tuple[str, datetime]] = {}


def _export_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📄 TXT", callback_data="export_txt"),
        InlineKeyboardButton(text="📑 PDF", callback_data="export_pdf"),
    ]])


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
        dt = datetime.now(timezone.utc)
        user_texts[message.from_user.id] = (text, dt)
        await message.answer(text, reply_markup=_export_keyboard())
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
        dt = datetime.now(timezone.utc)
        user_texts[message.from_user.id] = (text, dt)
        await message.answer(text, reply_markup=_export_keyboard())
    except ValueError as e:
        await message.answer(str(e))
    except Exception:
        logger.exception("Transcription failed for audio file_id=%s", message.audio.file_id)
        await message.answer(TRANSCRIPTION_ERROR_TEXT)


@router.callback_query(F.data == "export_txt")
async def callback_export_txt(query: CallbackQuery) -> None:
    await query.answer()
    entry = user_texts.get(query.from_user.id)
    if not entry:
        await query.message.answer(NO_TRANSCRIPTION_TEXT)
        return
    text, dt = entry
    data, filename = exporter.to_txt(text, dt)
    await query.message.answer_document(
        BufferedInputFile(data, filename=filename),
    )


@router.callback_query(F.data == "export_pdf")
async def callback_export_pdf(query: CallbackQuery) -> None:
    await query.answer()
    entry = user_texts.get(query.from_user.id)
    if not entry:
        await query.message.answer(NO_TRANSCRIPTION_TEXT)
        return
    text, dt = entry
    data, filename = exporter.to_pdf(text, dt)
    await query.message.answer_document(
        BufferedInputFile(data, filename=filename),
    )


@router.message()
async def handle_unsupported(message: Message) -> None:
    await message.answer(UNSUPPORTED_TEXT)
