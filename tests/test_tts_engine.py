import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from audio.tts_engine import split_on_pauses, render_script


def test_split_on_pauses_returns_parts():
    script = "Hello there.[PAUSE]Welcome to The Long View.[PAUSE]I'm Aria."
    parts = split_on_pauses(script)
    assert len(parts) == 3
    assert parts[0] == "Hello there."
    assert parts[2] == "I'm Aria."


def test_split_on_pauses_strips_whitespace():
    script = "  Hello.  [PAUSE]  Goodbye.  "
    parts = split_on_pauses(script)
    assert parts[0] == "Hello."
    assert parts[1] == "Goodbye."


def test_split_on_pauses_filters_empty():
    script = "[PAUSE]Content here.[PAUSE][PAUSE]More content."
    parts = split_on_pauses(script)
    assert "" not in parts
    assert len(parts) == 2


def test_render_script_creates_output(tmp_path):
    script = "Hello.[PAUSE]Goodbye."
    output = tmp_path / "segment.mp3"

    with patch("audio.tts_engine._tts_part") as mock_tts, \
         patch("audio.tts_engine._concat_with_silence") as mock_concat:
        mock_tts.side_effect = lambda text, voice, path: path.write_bytes(b"mp3data")
        mock_concat.return_value = output
        result = render_script(script, output, voice="en-US-AriaNeural")

    assert mock_tts.call_count == 2
    assert mock_concat.called


def test_render_script_returns_output_path(tmp_path):
    script = "Hello.[PAUSE]Goodbye."
    output = tmp_path / "out.mp3"

    with patch("audio.tts_engine._tts_part") as mock_tts, \
         patch("audio.tts_engine._concat_with_silence") as mock_concat:
        mock_tts.side_effect = lambda text, voice, path: path.write_bytes(b"mp3")
        mock_concat.return_value = output
        result = render_script(script, output, voice="en-US-AriaNeural")

    assert result == output
