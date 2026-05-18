import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from audio.show_assembler import build_segment_order, assemble_segment, SegmentParts


def test_build_segment_order_includes_all_parts():
    parts = SegmentParts(
        intro_jingle=Path("jingles/intro.mp3"),
        speech=Path("speech.mp3"),
        music=Path("music/track.mp3"),
        outro_jingle=Path("jingles/outro.mp3"),
        sponsor=None,
    )
    order = build_segment_order(parts)
    paths = [str(p) for p in order]
    assert "intro.mp3" in " ".join(paths)
    assert "speech.mp3" in " ".join(paths)
    assert "track.mp3" in " ".join(paths)
    assert "outro.mp3" in " ".join(paths)


def test_build_segment_order_includes_sponsor_when_present():
    parts = SegmentParts(
        intro_jingle=Path("jingles/intro.mp3"),
        speech=Path("speech.mp3"),
        music=Path("music/track.mp3"),
        outro_jingle=Path("jingles/outro.mp3"),
        sponsor=Path("sponsor/spot.mp3"),
    )
    order = build_segment_order(parts)
    paths = [str(p) for p in order]
    assert "spot.mp3" in " ".join(paths)


def test_build_segment_order_no_sponsor():
    parts = SegmentParts(
        intro_jingle=Path("jingles/intro.mp3"),
        speech=Path("speech.mp3"),
        music=None,
        outro_jingle=Path("jingles/outro.mp3"),
        sponsor=None,
    )
    order = build_segment_order(parts)
    assert len(order) >= 2


def test_assemble_segment_calls_ffmpeg(tmp_path):
    parts = SegmentParts(
        intro_jingle=Path("jingles/intro.mp3"),
        speech=Path("speech.mp3"),
        music=Path("music/track.mp3"),
        outro_jingle=Path("jingles/outro.mp3"),
        sponsor=None,
    )
    output = tmp_path / "segment.mp3"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assemble_segment(parts, output)
    assert mock_run.called
