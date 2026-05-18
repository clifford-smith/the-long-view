import pytest
from datetime import datetime
from xml.etree import ElementTree as ET
from distribution.rss_generator import SegmentMeta, generate_rss, add_episode


def test_generate_rss_produces_valid_xml():
    meta_list = [
        SegmentMeta(
            title="Morning Drift — May 17",
            description="Today's brief and opening thoughts.",
            audio_url="https://example.com/stream/morning_drift_20260517.mp3",
            duration_seconds=720,
            published=datetime(2026, 5, 17, 6, 0, 0),
            guid="20260517-morning-drift",
        )
    ]
    xml = generate_rss(
        meta_list,
        station_title="The Long View",
        station_url="https://example.com",
        description="Thinking out loud, all day long.",
    )
    assert "<?xml" in xml
    assert "Morning Drift" in xml
    assert "<rss" in xml
    assert "<item>" in xml


def test_generate_rss_includes_enclosure():
    meta_list = [
        SegmentMeta(
            title="Test Episode",
            description="Description.",
            audio_url="https://example.com/ep.mp3",
            duration_seconds=300,
            published=datetime(2026, 5, 17, 9, 0, 0),
            guid="test-guid-001",
        )
    ]
    xml = generate_rss(meta_list, "Title", "https://example.com", "Desc")
    assert "enclosure" in xml
    assert "ep.mp3" in xml


def test_enclosure_length_uses_file_size_bytes_when_provided():
    meta_list = [
        SegmentMeta(
            title="Episode",
            description="Desc.",
            audio_url="https://example.com/ep.mp3",
            duration_seconds=300,
            published=datetime(2026, 5, 17, 9, 0, 0),
            guid="guid-001",
            file_size_bytes=4_800_000,
        )
    ]
    xml = generate_rss(meta_list, "Title", "https://example.com", "Desc")
    root = ET.fromstring(xml.split("\n", 1)[1])
    enc = root.find(".//enclosure")
    assert enc is not None
    assert enc.get("length") == "4800000"


def test_enclosure_length_falls_back_to_duration_estimate_when_no_file_size():
    meta_list = [
        SegmentMeta(
            title="Episode",
            description="Desc.",
            audio_url="https://example.com/ep.mp3",
            duration_seconds=300,
            published=datetime(2026, 5, 17, 9, 0, 0),
            guid="guid-002",
            file_size_bytes=0,
        )
    ]
    xml = generate_rss(meta_list, "Title", "https://example.com", "Desc")
    root = ET.fromstring(xml.split("\n", 1)[1])
    enc = root.find(".//enclosure")
    assert enc is not None
    assert enc.get("length") == str(300 * 16000)
