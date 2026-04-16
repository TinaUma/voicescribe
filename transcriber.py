import io
import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)

_PAUSE_THRESHOLD = 1.5  # seconds between segments to start a new paragraph


def _segments_to_paragraphs(segments: list) -> str:
    """Group Whisper segments into paragraphs based on pauses between them."""
    if not segments:
        return ""

    paragraphs = []
    current: list[str] = []

    def _text(seg) -> str:
        return (seg["text"] if isinstance(seg, dict) else seg.text).strip()

    def _start(seg) -> float:
        return seg["start"] if isinstance(seg, dict) else seg.start

    def _end(seg) -> float:
        return seg["end"] if isinstance(seg, dict) else seg.end

    current.append(_text(segments[0]))

    for prev, curr in zip(segments, segments[1:]):
        pause = _start(curr) - _end(prev)
        if pause >= _PAUSE_THRESHOLD:
            paragraphs.append(" ".join(current))
            current = [_text(curr)]
        else:
            current.append(_text(curr))

    paragraphs.append(" ".join(current))
    return "\n\n".join(p for p in paragraphs if p)


def transcribe(audio_bytes: bytes) -> str:
    """Transcribe audio bytes via Groq Whisper API.

    Returns text formatted into paragraphs based on natural speech pauses.

    Raises:
        ValueError: If Groq returned 200 but text is empty (silent or too quiet audio).
        groq.APIError and others: Propagated as-is on API failure.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    result = client.audio.transcriptions.create(
        file=("audio.ogg", io.BytesIO(audio_bytes), "audio/ogg"),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
    )

    text = ""
    try:
        segments = getattr(result, "segments", None)
        if segments:
            text = _segments_to_paragraphs(segments)
    except Exception:
        logger.exception("Paragraph formatting failed, falling back to plain text")

    if not text:
        text = getattr(result, "text", "").strip()

    if not text:
        raise ValueError("Не удалось распознать речь — запись слишком тихая или пустая.")

    return text
