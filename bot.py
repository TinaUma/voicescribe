import argparse
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voicescribe",
        description="VoiceScribe Bot — transcribes Telegram voice messages via Groq Whisper",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("BOT_TOKEN"),
        help="Telegram bot token (default: BOT_TOKEN from .env)",
    )
    parser.add_argument(
        "--groq-key",
        default=os.getenv("GROQ_API_KEY"),
        help="Groq API key (default: GROQ_API_KEY from .env)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


async def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    if not args.token:
        parser.error("BOT_TOKEN is required. Set it in .env or pass --token")
    if not args.groq_key:
        parser.error("GROQ_API_KEY is required. Set it in .env or pass --groq-key")

    bot = Bot(token=args.token)
    dp = Dispatcher()
    dp.include_router(handlers.router)

    print("Starting VoiceScribe Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
