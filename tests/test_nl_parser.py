"""
tests/test_nl_parser.py — Tests for the NL parsing stage

These tests verify that parse_query() and validate_prefs() behave
correctly without making real API calls. The Claude API is mocked so
the tests run fast, offline, and deterministically.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.nl_parser import parse_query, validate_prefs, build_system_prompt


# ---------------------------------------------------------------------------
# validate_prefs — pure function, no mocking needed
# ---------------------------------------------------------------------------

def test_validate_prefs_lowercases_genre():
    """
    Genre and mood strings should be lowercased and stripped.
    The retriever does exact string matching against songs.csv values
    (all lowercase), so a capital 'KPop' would never match 'kpop'.
    """
    ...


def test_validate_prefs_clamps_energy_above_one():
    """
    Energy values above 1.0 (e.g., Claude returns 1.2) should be
    clamped to 1.0, not passed through as invalid floats.
    """
    ...


def test_validate_prefs_fills_missing_keys_with_defaults():
    """
    If Claude omits a key entirely, validate_prefs() should supply a
    safe default rather than letting the retriever crash on a KeyError.
    """
    ...


def test_validate_prefs_fixes_inverted_speechiness_range():
    """
    If Claude returns speechiness_range with min > max (e.g., (0.8, 0.1)),
    validate_prefs() should swap them rather than passing an invalid range.
    """
    ...


# ---------------------------------------------------------------------------
# parse_query — mocked Claude API
# ---------------------------------------------------------------------------

def test_parse_query_returns_dict_with_required_keys():
    """
    parse_query() should always return a dict that contains at minimum:
    genre, mood, and energy. Mock the Claude API to return a valid JSON
    response and confirm the dict has the right shape.
    """
    ...


def test_parse_query_raises_on_unparseable_response():
    """
    If the Claude API returns a response that cannot be parsed as JSON
    (e.g., a plain English sentence instead of a JSON block), parse_query()
    should raise a ValueError with a descriptive message.
    """
    ...


def test_parse_query_sends_system_prompt():
    """
    Confirm that the Claude API is called with the system prompt from
    build_system_prompt(), not an empty string. This ensures the parser
    prompt is wired up correctly.
    """
    ...


# ---------------------------------------------------------------------------
# build_system_prompt — content checks
# ---------------------------------------------------------------------------

def test_build_system_prompt_mentions_json():
    """
    The system prompt should instruct Claude to return JSON. If "JSON"
    is not in the prompt, Claude might return prose instead of a
    parseable response.
    """
    ...


def test_build_system_prompt_mentions_all_required_keys():
    """
    The system prompt should name all expected output keys so Claude
    knows exactly what fields to produce. Check that genre, mood,
    energy, and tempo_bpm are at least mentioned.
    """
    ...
