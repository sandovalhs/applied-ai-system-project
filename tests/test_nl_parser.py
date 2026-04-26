"""
tests/test_nl_parser.py — Tests for the NL parsing stage

validate_prefs tests are pure — no mocking needed.
parse_query tests mock the Gemini client so they run offline and fast.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.nl_parser import build_system_prompt, parse_query, validate_prefs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_response(json_str: str) -> MagicMock:
    """Return a mock Gemini response whose .text attribute is json_str."""
    return MagicMock(text=json_str)


_VALID_JSON = (
    '{"genre": "kpop", "mood": "hype", "energy": 0.85, "tempo_bpm": 130, '
    '"valence": null, "danceability": null, "acousticness": null, '
    '"speechiness_range": null, "loudness_db": null, "instrumentalness": null}'
)


# ---------------------------------------------------------------------------
# validate_prefs — pure function, no mocking
# ---------------------------------------------------------------------------

def test_validate_prefs_lowercases_genre_and_mood():
    result = validate_prefs({"genre": "KPop", "mood": "HYPE"})
    assert result["genre"] == "kpop"
    assert result["mood"] == "hype"


def test_validate_prefs_strips_whitespace_from_strings():
    result = validate_prefs({"genre": "  trap  ", "mood": " chill "})
    assert result["genre"] == "trap"
    assert result["mood"] == "chill"


def test_validate_prefs_clamps_energy_above_one():
    result = validate_prefs({"energy": 1.5})
    assert result["energy"] == 1.0


def test_validate_prefs_clamps_energy_below_zero():
    result = validate_prefs({"energy": -0.3})
    assert result["energy"] == 0.0


def test_validate_prefs_fills_missing_keys_with_defaults():
    result = validate_prefs({})
    required = {
        "genre", "mood", "energy", "tempo_bpm", "valence",
        "danceability", "acousticness", "speechiness_range",
        "loudness_db", "instrumentalness",
    }
    assert required.issubset(result.keys())


def test_validate_prefs_fixes_inverted_speechiness_range():
    result = validate_prefs({"speechiness_range": [0.8, 0.1]})
    lo, hi = result["speechiness_range"]
    assert lo <= hi


def test_validate_prefs_coerces_speechiness_range_list_to_tuple():
    result = validate_prefs({"speechiness_range": [0.1, 0.5]})
    assert isinstance(result["speechiness_range"], tuple)


def test_validate_prefs_clamps_tempo_to_max():
    result = validate_prefs({"tempo_bpm": 999})
    assert result["tempo_bpm"] == 250.0


def test_validate_prefs_clamps_tempo_to_min():
    result = validate_prefs({"tempo_bpm": 10})
    assert result["tempo_bpm"] == 40.0


def test_validate_prefs_ignores_null_values_and_uses_defaults():
    result = validate_prefs({"genre": None, "energy": None})
    # None values should fall back to defaults, not overwrite them with None
    assert result["genre"] == ""
    assert result["energy"] == 0.5


# ---------------------------------------------------------------------------
# parse_query — mocked Gemini client
# ---------------------------------------------------------------------------

def test_parse_query_returns_dict_with_required_keys():
    with patch("src.nl_parser.genai") as mock_genai:
        mock_genai.Client.return_value.models.generate_content.return_value = _fake_response(_VALID_JSON)
        result = parse_query("hype kpop songs")

    assert isinstance(result, dict)
    for key in ("genre", "mood", "energy"):
        assert key in result


def test_parse_query_raises_on_non_json_response():
    with patch("src.nl_parser.genai") as mock_genai:
        mock_genai.Client.return_value.models.generate_content.return_value = _fake_response(
            "Sure! I'd love to help you find some music."
        )
        with pytest.raises(ValueError, match="No JSON object found"):
            parse_query("some query")


def test_parse_query_raises_on_malformed_json():
    with patch("src.nl_parser.genai") as mock_genai:
        mock_genai.Client.return_value.models.generate_content.return_value = _fake_response(
            "{genre: kpop, mood: hype}"  # invalid JSON (unquoted keys)
        )
        with pytest.raises(ValueError):
            parse_query("some query")


def test_parse_query_sends_non_empty_system_prompt():
    with patch("src.nl_parser.genai") as mock_genai:
        mock_genai.Client.return_value.models.generate_content.return_value = _fake_response(_VALID_JSON)
        parse_query("pop songs")

    call_kwargs = mock_genai.Client.return_value.models.generate_content.call_args.kwargs
    config = call_kwargs.get("config")
    assert config is not None
    assert len(config.system_instruction) > 0


def test_parse_query_passes_user_query_to_generate_content():
    with patch("src.nl_parser.genai") as mock_genai:
        mock_generate = mock_genai.Client.return_value.models.generate_content
        mock_generate.return_value = _fake_response(_VALID_JSON)
        parse_query("chill lofi vibes")

    call_kwargs = mock_generate.call_args.kwargs
    assert call_kwargs.get("contents") == "chill lofi vibes"


# ---------------------------------------------------------------------------
# build_system_prompt — content checks (no API calls)
# ---------------------------------------------------------------------------

def test_build_system_prompt_mentions_json():
    prompt = build_system_prompt()
    assert "JSON" in prompt


def test_build_system_prompt_mentions_required_keys():
    prompt = build_system_prompt()
    for key in ("genre", "mood", "energy", "tempo_bpm"):
        assert key in prompt


def test_build_system_prompt_instructs_null_for_missing():
    prompt = build_system_prompt()
    assert "null" in prompt.lower()
