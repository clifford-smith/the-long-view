import pytest
from datetime import datetime
from distribution.show_notes import generate_post


def test_generate_post_contains_title():
    post = generate_post(
        title="Morning Drift — May 17",
        script="Hello, this is Aria.[PAUSE]Welcome to The Long View.",
        slot="morning_drift",
        published=datetime(2026, 5, 17, 6, 0, 0),
        affiliates={},
    )
    assert "Morning Drift" in post


def test_generate_post_strips_pause_markers():
    post = generate_post(
        title="Test",
        script="Hello.[PAUSE]World.",
        slot="morning_drift",
        published=datetime(2026, 5, 17, 6, 0, 0),
        affiliates={},
    )
    assert "[PAUSE]" not in post


def test_generate_post_includes_transcript():
    post = generate_post(
        title="Test",
        script="Hello there.[PAUSE]This is the transcript.",
        slot="morning_drift",
        published=datetime(2026, 5, 17, 6, 0, 0),
        affiliates={},
    )
    assert "Hello there" in post
    assert "transcript" in post.lower()


def test_generate_post_injects_affiliates():
    post = generate_post(
        title="Test",
        script="We discussed a book today.",
        slot="the_stack",
        published=datetime(2026, 5, 17, 9, 0, 0),
        affiliates={"bookshop": "https://bookshop.org/affiliate/longview"},
    )
    assert "bookshop.org" in post
