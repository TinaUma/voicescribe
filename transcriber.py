import io
import os

from groq import Groq


def transcribe(audio_bytes: bytes) -> str:
    """Transcribe OGG/Opus audio bytes via Groq Whisper API.

    Args:
        audio_bytes: Raw audio data (OGG/Opus or other Groq-supported format).

    Returns:
        Transcribed text as a non-empty string.

    Raises:
        ValueError: If Groq returned 200 but text is empty (silent or too quiet audio).
        groq.APIError and others: Propagated as-is on API failure.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    result = client.audio.transcriptions.create(
        file=("audio.ogg", io.BytesIO(audio_bytes), "audio/ogg"),
        model="whisper-large-v3-turbo",
        language=None,
        response_format="json",
    )

    text = result.text.strip()
    if not text:
        raise ValueError("Не удалось распознать речь — запись слишком тихая или пустая.")

    return text
