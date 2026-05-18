import pytest
from unittest.mock import patch, MagicMock
from content.script_writer import load_prompt, inject_sponsor_spot, write_script


def test_load_prompt_includes_base():
    prompt = load_prompt("morning_drift")
    assert "Aria" in prompt
    assert len(prompt) > 100


def test_load_prompt_includes_slot():
    prompt = load_prompt("deep_cuts")
    assert "Deep Cuts" in prompt or "deep" in prompt.lower()


def test_inject_sponsor_spot_adds_spot():
    script = "First paragraph.[PAUSE]Second paragraph.[PAUSE]Third paragraph."
    sponsor = "This segment is brought to you by Brilliant. Go to brilliant.org/longview."
    result = inject_sponsor_spot(script, sponsor)
    assert "Brilliant" in result
    assert result.count("[PAUSE]") >= script.count("[PAUSE]")


def test_inject_sponsor_spot_places_midway():
    script = "[PAUSE]".join([f"Paragraph {i}." for i in range(6)])
    sponsor = "Sponsored by TestCo."
    result = inject_sponsor_spot(script, sponsor)
    parts = result.split("[PAUSE]")
    # Sponsor should not be at the very start or very end
    assert "TestCo" not in parts[0]
    assert "TestCo" not in parts[-1]


def test_write_script_calls_ollama():
    mock_response = {"message": {"content": "Hello.[PAUSE]This is Aria.[PAUSE]Welcome."}}
    with patch("ollama.chat", return_value=mock_response) as mock_chat:
        result = write_script(slot="morning_drift", brief="Story: Test headline. Summary.")
    assert mock_chat.called
    assert "Hello" in result


def test_write_script_returns_string():
    mock_response = {"message": {"content": "Script content here.[PAUSE]More content."}}
    with patch("ollama.chat", return_value=mock_response):
        result = write_script(slot="drive", brief="News brief.")
    assert isinstance(result, str)
    assert len(result) > 0
