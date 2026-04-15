import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

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
    # TODO Sprint 2: передать data в transcriber


@router.message(F.audio)
async def handle_audio(message: Message) -> None:
    await message.answer(PROCESSING_TEXT)
    file = await message.bot.get_file(message.audio.file_id)
    audio_bytes = await message.bot.download_file(file.file_path)
    data: bytes = audio_bytes.read()
    logger.info("Audio received: %d bytes, file_id=%s", len(data), message.audio.file_id)
    # TODO Sprint 2: передать data в transcriber


@router.message()
async def handle_unsupported(message: Message) -> None:
    await message.answer(UNSUPPORTED_TEXT)
