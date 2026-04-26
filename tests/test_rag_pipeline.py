"""
tests/test_rag_pipeline.py — End-to-end pipeline and response-parser tests

run_pipeline tests mock both Gemini API calls so they run offline.
parse_claude_response tests are pure — no mocking needed.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.recommender import load_songs
from src.rag_recommender import parse_claude_response, run_pipeline

SONGS = load_songs("data/songs.csv")
CATALOG_IDS = {song["id"] for song in SONGS}

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

_FAKE_PREFS_JSON = (
    '{"genre": "kpop", "mood": "hype", "energy": 0.85, "tempo_bpm": 130, '
    '"valence": 0.65, "danceability": 0.88, "acousticness": 0.03, '
    '"speechiness_range": [0.03, 0.82], "loudness_db": -4.5, "instrumentalness": 0.0}'
)

# Titles must exactly match songs.csv so the catalog lookup in generate_recommendations succeeds
_FAKE_GENERATION = """\
1. Hype Boy by New Jeans — pure kpop energy that locks into your late-night drive vibe.
2. ANTIFRAGILE by LE SSERAFIM — intense kpop momentum matching your hype request perfectly.
3. Blinding Lights by The Weeknd — high-energy synth-pop that channels the same nocturnal intensity.
4. Gym Hero by Max Pulse — driven tempo and max energy for your upbeat mood.
5. Magnolia by Playboi Carti — trap hype anchoring the rhythm of your late-night theme.\
"""


def _patch_both_apis(fake_prefs_json: str = _FAKE_PREFS_JSON, fake_gen: str = _FAKE_GENERATION):
    """
    Return a pair of patch context managers that mock the Gemini client
    in nl_parser (parse stage) and rag_recommender (generation stage) independently.
    """
    parse_mock = patch(
        "src.nl_parser.genai",
        **{"Client.return_value.models.generate_content.return_value": MagicMock(text=fake_prefs_json)},
    )
    gen_mock = patch(
        "src.rag_recommender.genai",
        **{"Client.return_value.models.generate_content.return_value": MagicMock(text=fake_gen)},
    )
    return parse_mock, gen_mock


# ---------------------------------------------------------------------------
# run_pipeline — integration tests
# ---------------------------------------------------------------------------

def test_pipeline_returns_k_recommendations():
    parse_mock, gen_mock = _patch_both_apis()
    with parse_mock, gen_mock:
        results = run_pipeline("hype kpop late night", SONGS, k=5)
    assert len(results) == 5


def test_pipeline_returns_list_of_tuples():
    parse_mock, gen_mock = _patch_both_apis()
    with parse_mock, gen_mock:
        results = run_pipeline("hype kpop late night", SONGS, k=5)
    for item in results:
        song, explanation = item
        assert isinstance(song, dict)
        assert isinstance(explanation, str)


def test_pipeline_songs_come_from_catalog():
    """Every returned song id must exist in songs.csv — Gemini cannot invent picks."""
    parse_mock, gen_mock = _patch_both_apis()
    with parse_mock, gen_mock:
        results = run_pipeline("hype kpop late night", SONGS, k=5)
    for song, _ in results:
        assert song["id"] in CATALOG_IDS


def test_pipeline_consistency_same_query_same_titles():
    """Two runs with identical mocked responses must yield the same title order."""
    parse_mock, gen_mock = _patch_both_apis()
    with parse_mock, gen_mock:
        run1 = run_pipeline("hype kpop late night", SONGS, k=5)
    parse_mock, gen_mock = _patch_both_apis()
    with parse_mock, gen_mock:
        run2 = run_pipeline("hype kpop late night", SONGS, k=5)

    assert [s["title"] for s, _ in run1] == [s["title"] for s, _ in run2]


def test_pipeline_handles_api_error_without_crashing():
    """A Gemini API exception should be caught and return an empty list."""
    with patch("src.nl_parser.genai") as mock_genai:
        mock_genai.Client.return_value.models.generate_content.side_effect = Exception("API timeout")
        results = run_pipeline("hype kpop late night", SONGS, k=5)
    assert results == []


def test_pipeline_returns_empty_list_for_empty_query():
    """An empty query must short-circuit before any API call and return []."""
    with patch("src.nl_parser.genai") as mock_genai:
        results = run_pipeline("", SONGS, k=5)
        mock_genai.Client.assert_not_called()
    assert results == []


def test_pipeline_returns_empty_list_for_whitespace_query():
    with patch("src.nl_parser.genai") as mock_genai:
        results = run_pipeline("   ", SONGS, k=5)
        mock_genai.Client.assert_not_called()
    assert results == []


# ---------------------------------------------------------------------------
# parse_claude_response — unit tests (pure function, no mocking)
# ---------------------------------------------------------------------------

def test_parse_extracts_correct_number_of_picks():
    picks = parse_claude_response(_FAKE_GENERATION, k=5)
    assert len(picks) == 5


def test_parse_returns_list_of_title_explanation_tuples():
    picks = parse_claude_response(_FAKE_GENERATION, k=5)
    for title, explanation in picks:
        assert isinstance(title, str) and title
        assert isinstance(explanation, str) and explanation


def test_parse_first_title_is_correct():
    picks = parse_claude_response(_FAKE_GENERATION, k=5)
    assert picks[0][0] == "Hype Boy"


def test_parse_handles_fewer_than_k_picks_without_raising():
    short = (
        "1. Hype Boy by New Jeans — great energy.\n"
        "2. ANTIFRAGILE by LE SSERAFIM — intense momentum.\n"
    )
    picks = parse_claude_response(short, k=5)
    assert len(picks) == 2


def test_parse_strips_whitespace_from_titles():
    response = "1.   Hype Boy   by New Jeans — great pick.\n"
    picks = parse_claude_response(response, k=1)
    title, _ = picks[0]
    assert title == title.strip()
    assert title == "Hype Boy"


def test_parse_handles_title_containing_the_word_by():
    """rfind(' by ') must extract the correct title when 'by' appears inside it."""
    response = "1. Boy's a liar by PinkPantheress — playful energy matching your vibe.\n"
    picks = parse_claude_response(response, k=1)
    assert picks[0][0] == "Boy's a liar"


def test_parse_skips_non_numbered_lines():
    response = (
        "Here are my picks:\n"
        "1. Hype Boy by New Jeans — great energy.\n"
        "Hope you enjoy!\n"
    )
    picks = parse_claude_response(response, k=5)
    assert len(picks) == 1


def test_parse_returns_empty_list_for_blank_response():
    picks = parse_claude_response("", k=5)
    assert picks == []
