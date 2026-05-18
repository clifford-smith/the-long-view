import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from stream.scheduler import _validate_startup


_SLOTS = {
    "morning_drift", "the_stack", "midday",
    "deep_cuts", "drive", "night_school", "archive",
}


@pytest.fixture
def valid_root(tmp_path):
    """A minimal valid project root that passes all startup checks."""
    prompts = tmp_path / "content" / "prompts"
    prompts.mkdir(parents=True)
    for slot in _SLOTS:
        (prompts / f"{slot}.txt").write_text(f"Slot: {slot}")

    music_dir = tmp_path / "audio" / "assets"
    music_dir.mkdir(parents=True)
    (music_dir / "music_index.json").write_text(
        json.dumps({"tracks": [{"path": "audio/assets/music/track1.mp3"}], "recently_played": []})
    )

    jingles = tmp_path / "audio" / "assets" / "jingles"
    jingles.mkdir(parents=True)
    (jingles / "station_id.mp3").write_bytes(b"fake-audio")

    return tmp_path


@pytest.fixture
def minimal_config():
    return {
        "llm": {"base_url": "http://localhost:11434"},
        "paths": {
            "prompts": "content/prompts",
            "music_index": "audio/assets/music_index.json",
            "jingles": "audio/assets/jingles",
        },
    }


def test_validate_startup_passes_when_all_deps_present(valid_root, minimal_config):
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        _validate_startup(minimal_config, valid_root)


def test_validate_startup_raises_if_ollama_unreachable(valid_root, minimal_config):
    with patch("requests.get", side_effect=ConnectionError("refused")):
        with pytest.raises(RuntimeError, match="Ollama is not running"):
            _validate_startup(minimal_config, valid_root)


def test_validate_startup_raises_if_prompt_file_missing(valid_root, minimal_config):
    (valid_root / "content" / "prompts" / "morning_drift.txt").unlink()
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        with pytest.raises(RuntimeError, match="morning_drift"):
            _validate_startup(minimal_config, valid_root)


def test_validate_startup_warns_if_music_library_empty(valid_root, minimal_config, caplog):
    import logging
    (valid_root / "audio" / "assets" / "music_index.json").write_text(
        json.dumps({"tracks": [], "recently_played": []})
    )
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        with caplog.at_level(logging.WARNING, logger="stream.scheduler"):
            _validate_startup(minimal_config, valid_root)
    assert any("Music library is empty" in r.message for r in caplog.records)


def test_validate_startup_does_not_raise_if_music_library_empty(valid_root, minimal_config):
    (valid_root / "audio" / "assets" / "music_index.json").write_text(
        json.dumps({"tracks": [], "recently_played": []})
    )
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        _validate_startup(minimal_config, valid_root)


def test_validate_startup_warns_if_jingle_missing(valid_root, minimal_config, caplog):
    import logging
    (valid_root / "audio" / "assets" / "jingles" / "station_id.mp3").unlink()
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        with caplog.at_level(logging.WARNING, logger="stream.scheduler"):
            _validate_startup(minimal_config, valid_root)
    assert any("Station ID jingle missing" in r.message for r in caplog.records)


def test_validate_startup_does_not_raise_if_jingle_missing(valid_root, minimal_config):
    (valid_root / "audio" / "assets" / "jingles" / "station_id.mp3").unlink()
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        _validate_startup(minimal_config, valid_root)
