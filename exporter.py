import io
import os
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

_FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_PATH = os.path.join(_FONTS_DIR, "Arial.ttf")
_FONT_NAME = "Arial"


def _filename(ext: str, dt: datetime) -> str:
    return f"voicescribe_{dt.strftime('%Y-%m-%d_%H-%M')}.{ext}"


def to_txt(text: str, dt: datetime) -> tuple[bytes, str]:
    """Return (file_bytes, filename) for a plain-text export."""
    content = f"VoiceScribe — {dt.strftime('%Y-%m-%d %H:%M')}\n\n{text}\n"
    return content.encode("utf-8"), _filename("txt", dt)


def to_pdf(text: str, dt: datetime) -> tuple[bytes, str]:
    """Return (file_bytes, filename) for a PDF export with Cyrillic support."""
    pdf = FPDF()
    pdf.add_font(_FONT_NAME, style="", fname=_FONT_PATH)
    pdf.add_page()

    # Title
    pdf.set_font(_FONT_NAME, size=14)
    pdf.cell(0, 10, "VoiceScribe", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Date
    pdf.set_font(_FONT_NAME, size=10)
    pdf.cell(0, 8, dt.strftime("%Y-%m-%d %H:%M"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(6)

    # Body
    pdf.set_font(_FONT_NAME, size=12)
    pdf.multi_cell(0, 8, text)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue(), _filename("pdf", dt)
