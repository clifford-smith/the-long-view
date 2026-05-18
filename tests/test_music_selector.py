import pytest
import json
from pathlib import Path
from content.music_selector import (
    load_index, save_index, pick_track, mark_played, get_slot_mood
)


@pytest.fixture
def index_file(tmp_path):
    idx = {
        "tracks": [
            {"path": "music/calm1.mp3", "mood": "calm", "tempo": "slow", "genre": "ambient", "duration": 180, "title": "Calm One"},
            {"path": "music/calm2.mp3", "mood": "calm", "tempo": "slow", "genre": "ambient", "duration": 200, "title": "Calm Two"},
            {"path": "music/upbeat1.mp3", "mood": "upbeat", "tempo": "fast", "genre": "jazz", "duration": 210, "title": "Upbeat One"},
        ],
        "recently_played": []
    }
    path = tmp_path / "music_index.json"
    path.write_text(json.dumps(idx))
    return path


def test_load_index_returns_dict(index_file):
    idx = load_index(index_file)
    assert "tracks" in idx
    assert "recently_played" in idx


def test_pick_track_returns_matching_mood(index_file):
    idx = load_index(index_file)
    track = pick_track(idx, mood="calm")
    assert track["mood"] == "calm"


def test_pick_track_avoids_recently_played(index_file):
    idx = load_index(index_file)
    idx["recently_played"] = ["music/calm1.mp3"]
    track = pick_track(idx, mood="calm")
    assert track["path"] == "music/calm2.mp3"


def test_pick_track_falls_back_when_all_played(index_file):
    idx = load_index(index_file)
    idx["recently_played"] = ["music/calm1.mp3", "music/calm2.mp3"]
    track = pick_track(idx, mood="calm")
    assert track is not None


def test_mark_played_adds_to_recent(index_file):
    idx = load_index(index_file)
    mark_played(idx, "music/calm1.mp3")
    assert "music/calm1.mp3" in idx["recently_played"]


def test_mark_played_caps_at_window(index_file):
    idx = load_index(index_file)
    for i in range(30):
        mark_played(idx, f"music/track_{i}.mp3")
    assert len(idx["recently_played"]) <= 20


def test_get_slot_mood_returns_string():
    mood = get_slot_mood("morning_drift")
    assert isinstance(mood, str)
    assert len(mood) > 0
