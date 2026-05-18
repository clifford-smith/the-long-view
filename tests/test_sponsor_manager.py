import pytest
import yaml
from pathlib import Path
from monetization.sponsor_manager import (
    load_sponsors,
    get_spot_for_slot,
    render_sponsor_script,
    is_acceptable,
    BLOCKED_CATEGORIES,
)


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


# --- Vetting tests ---

def test_is_acceptable_clean_sponsor():
    sponsor = {"name": "Brilliant", "categories": ["education", "science"]}
    assert is_acceptable(sponsor) is True


def test_is_acceptable_no_categories():
    # Missing categories field defaults to [] — treated as acceptable so existing
    # entries without the field don't silently disappear; operators must add bad
    # categories explicitly to block.
    assert is_acceptable({"name": "Unknown"}) is True


def test_is_acceptable_rejects_anti_science():
    sponsor = {"name": "Snake Oil Co", "categories": ["health", "anti_science"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_climate_denial():
    sponsor = {"name": "Big Oil Media", "categories": ["energy", "climate_denial"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_anti_vaccine():
    sponsor = {"name": "Freedom Health", "categories": ["health", "anti_vaccine"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_misinformation():
    sponsor = {"name": "TruthBlast", "categories": ["news", "misinformation"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_partisan():
    sponsor = {"name": "PAC Media", "categories": ["partisan", "news"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_crypto():
    sponsor = {"name": "MoonCoin", "categories": ["crypto", "finance"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_fossil_fuel():
    sponsor = {"name": "Oil Corp Radio", "categories": ["fossil_fuel"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_rejects_firearms():
    sponsor = {"name": "Guns Daily", "categories": ["firearms", "retail"]}
    assert is_acceptable(sponsor) is False


def test_is_acceptable_category_check_is_case_insensitive():
    sponsor = {"name": "Bad Actor", "categories": ["Anti_Science", "Health"]}
    assert is_acceptable(sponsor) is False


def test_get_spot_skips_blocked_category_even_when_active(tmp_path):
    data = {
        "sponsors": [
            {
                "name": "Coal Co",
                "copy": "Coal powers your world.",
                "active": True,
                "slots": ["morning_drift"],
                "categories": ["fossil_fuel"],
            },
            {
                "name": "Bookshop",
                "copy": "Support indie bookstores.",
                "active": True,
                "slots": ["morning_drift"],
                "categories": ["books", "retail"],
            },
        ]
    }
    p = tmp_path / "sponsors.yml"
    p.write_text(yaml.dump(data))
    sponsors = load_sponsors(p)
    spot = get_spot_for_slot(sponsors, "morning_drift")
    assert spot is not None
    assert spot["name"] == "Bookshop"


def test_blocked_categories_set_is_not_empty():
    assert len(BLOCKED_CATEGORIES) > 0


def test_blocked_categories_contains_expected_entries():
    expected = {"anti_science", "climate_denial", "anti_vaccine", "fossil_fuel",
                "misinformation", "partisan", "crypto", "firearms", "tobacco"}
    assert expected.issubset(BLOCKED_CATEGORIES)
