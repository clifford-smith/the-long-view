import pytest
import yaml
from pathlib import Path
from monetization.sponsor_manager import load_sponsors, get_spot_for_slot, render_sponsor_script


@pytest.fixture
def sponsor_file(tmp_path):
    data = {
        "sponsors": [
            {
                "name": "Brilliant",
                "copy": "Brought to you by Brilliant. Go to brilliant.org.",
                "url": "https://brilliant.org",
                "active": True,
                "slots": ["the_stack", "deep_cuts"],
            },
            {
                "name": "Readwise",
                "copy": "Readwise helps you remember what you read.",
                "url": "https://readwise.io",
                "active": False,
                "slots": ["morning_drift"],
            },
        ]
    }
    p = tmp_path / "sponsors.yml"
    p.write_text(yaml.dump(data))
    return p


def test_load_sponsors_returns_list(sponsor_file):
    sponsors = load_sponsors(sponsor_file)
    assert isinstance(sponsors, list)
    assert len(sponsors) == 2


def test_get_spot_for_slot_returns_active_sponsor(sponsor_file):
    sponsors = load_sponsors(sponsor_file)
    spot = get_spot_for_slot(sponsors, "the_stack")
    assert spot is not None
    assert spot["name"] == "Brilliant"


def test_get_spot_for_slot_skips_inactive(sponsor_file):
    sponsors = load_sponsors(sponsor_file)
    spot = get_spot_for_slot(sponsors, "morning_drift")
    assert spot is None


def test_get_spot_for_slot_returns_none_for_unsponsored_slot(sponsor_file):
    sponsors = load_sponsors(sponsor_file)
    spot = get_spot_for_slot(sponsors, "archive")
    assert spot is None


def test_render_sponsor_script_returns_copy(sponsor_file):
    sponsors = load_sponsors(sponsor_file)
    spot = get_spot_for_slot(sponsors, "the_stack")
    script = render_sponsor_script(spot)
    assert "Brilliant" in script
