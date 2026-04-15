"""Sprint 3 — exporter unit tests."""
from datetime import datetime

import pytest

import exporter

DT = datetime(2026, 4, 15, 14, 30)
CYRILLIC_TEXT = "Привет мир — тест кириллицы"
LATIN_TEXT = "Hello world — test"


# --- to_txt ---

def test_txt_returns_bytes():
    data, _ = exporter.to_txt(LATIN_TEXT, DT)
    assert isinstance(data, bytes)


def test_txt_filename_contains_date_and_time():
    _, fn = exporter.to_txt(LATIN_TEXT, DT)
    assert fn == "voicescribe_2026-04-15_14-30.txt"


def test_txt_contains_text():
    data, _ = exporter.to_txt(LATIN_TEXT, DT)
    assert LATIN_TEXT.encode("utf-8") in data


def test_txt_contains_cyrillic():
    data, _ = exporter.to_txt(CYRILLIC_TEXT, DT)
    assert "Привет".encode("utf-8") in data


def test_txt_contains_header():
    data, _ = exporter.to_txt(LATIN_TEXT, DT)
    assert b"VoiceScribe" in data
    assert b"2026-04-15" in data


# --- to_pdf ---

def test_pdf_returns_bytes():
    data, _ = exporter.to_pdf(LATIN_TEXT, DT)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pdf_filename_contains_date_and_time():
    _, fn = exporter.to_pdf(LATIN_TEXT, DT)
    assert fn == "voicescribe_2026-04-15_14-30.pdf"


def test_pdf_starts_with_pdf_magic():
    """Valid PDF files start with %PDF."""
    data, _ = exporter.to_pdf(LATIN_TEXT, DT)
    assert data[:4] == b"%PDF"


def test_pdf_cyrillic_does_not_raise():
    """PDF generation with Cyrillic text must not raise an exception."""
    data, _ = exporter.to_pdf(CYRILLIC_TEXT, DT)
    assert isinstance(data, bytes)
    assert len(data) > 1000


def test_pdf_and_txt_same_datetime_same_stem():
    """Both formats share the same filename stem for the same datetime."""
    _, txt_fn = exporter.to_txt(LATIN_TEXT, DT)
    _, pdf_fn = exporter.to_pdf(LATIN_TEXT, DT)
    assert txt_fn.replace(".txt", "") == pdf_fn.replace(".pdf", "")


def test_different_datetimes_produce_different_filenames():
    dt2 = datetime(2026, 4, 15, 15, 45)
    _, fn1 = exporter.to_txt(LATIN_TEXT, DT)
    _, fn2 = exporter.to_txt(LATIN_TEXT, dt2)
    assert fn1 != fn2
