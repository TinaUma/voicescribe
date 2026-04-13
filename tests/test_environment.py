"""Sprint 0 — environment smoke tests."""
import importlib
import subprocess
import sys


def test_bot_help_exits_zero():
    """python bot.py --help must exit 0."""
    result = subprocess.run(
        [sys.executable, "bot.py", "--help"],
        capture_output=True,
    )
    assert result.returncode == 0


def test_bot_unknown_arg_exits_two():
    """python bot.py --unknown-arg must exit 2."""
    result = subprocess.run(
        [sys.executable, "bot.py", "--unknown-arg"],
        capture_output=True,
    )
    assert result.returncode == 2


def test_dotenv_importable():
    """python-dotenv must be installed."""
    assert importlib.util.find_spec("dotenv") is not None
