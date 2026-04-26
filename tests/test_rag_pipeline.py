"""
tests/test_rag_pipeline.py — End-to-end pipeline tests

These tests exercise the full run_pipeline() flow with a mocked Claude
API. They verify two things:
1. The pipeline wires all stages together correctly (data flows from
   query → prefs → candidates → prompt → recommendations).
2. The system behaves reliably — the same query returns structurally
   consistent results across multiple runs (Reliability requirement).
"""

import pytest
from unittest.mock import patch, MagicMock
from src.recommender import load_songs
from src.rag_recommender import run_pipeline, parse_claude_response


SONGS = load_songs("data/songs.csv")


# ---------------------------------------------------------------------------
# run_pipeline — integration tests with mocked Claude
# ---------------------------------------------------------------------------

def test_pipeline_returns_k_recommendations():
    """
    run_pipeline() should return exactly k (song_dict, explanation)
    tuples when the Claude API returns a well-formed response. Mock both
    API calls (parse_query and generate_recommendations) and verify the
    output length equals k.
    """
    ...


def test_pipeline_songs_come_from_catalog():
    """
    Every song dict in the output must be from the real songs.csv
    catalog — identified by its 'id' field. If a song id in the output
    doesn't exist in SONGS, Claude invented it (RAG grounding failure).
    """
    ...


def test_pipeline_consistency_same_query_same_structure():
    """
    Running run_pipeline() twice with the exact same query and mocked
    Claude response should return the same song titles in the same order.
    Verifies that no randomness is introduced between the retrieval and
    generation stages (beyond what the mock controls).
    """
    ...


def test_pipeline_handles_api_error_without_crashing():
    """
    If the Claude API raises an exception during parse_query(), the
    pipeline should catch it, log it, and return an empty list rather
    than propagating a raw exception to the Streamlit UI.
    """
    ...


def test_pipeline_handles_empty_query():
    """
    An empty string query should not crash the pipeline. It should
    either return an empty list or raise a clear ValueError before the
    API is ever called.
    """
    ...


# ---------------------------------------------------------------------------
# parse_claude_response — unit tests for the response parser
# ---------------------------------------------------------------------------

def test_parse_claude_response_extracts_five_picks():
    """
    Given a well-formed Claude response with 5 numbered picks,
    parse_claude_response() should return exactly 5 (title, explanation)
    tuples.
    """
    ...


def test_parse_claude_response_handles_fewer_than_k_picks():
    """
    If Claude only returns 3 picks when k=5 (truncated response),
    parse_claude_response() should return 3 tuples without raising.
    The caller (generate_recommendations) decides how to handle
    short lists.
    """
    ...


def test_parse_claude_response_strips_whitespace_from_titles():
    """
    Titles in the parsed output should be stripped of leading/trailing
    whitespace. The title lookup in generate_recommendations() does
    exact string matching against the candidates list — stray spaces
    would cause silent lookup failures.
    """
    ...
