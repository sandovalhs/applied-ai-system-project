"""
tests/test_retriever.py — Tests for the retrieval stage

These tests verify that retrieve_candidates() and
format_candidates_for_prompt() work correctly against the real songs.csv
catalog. No mocking needed — these are pure functions with no external
dependencies.
"""

import pytest
from src.recommender import load_songs
from src.retriever import retrieve_candidates, format_candidates_for_prompt


SONGS = load_songs("data/songs.csv")


# ---------------------------------------------------------------------------
# retrieve_candidates
# ---------------------------------------------------------------------------

def test_retrieve_returns_correct_count():
    """
    retrieve_candidates() should return exactly top_n results when the
    catalog is larger than top_n (which it always is with 20 songs).
    """
    ...


def test_retrieve_results_are_sorted_by_score_descending():
    """
    The first result should always have a score >= the second result,
    and so on down the list. Unsorted results would give Claude a
    misleading sense of which songs scored highest.
    """
    ...


def test_retrieve_genre_match_scores_higher_than_no_match():
    """
    A prefs dict with genre='kpop' should rank the two kpop songs
    (Hype Boy, ANTIFRAGILE) above a non-kpop song with identical energy,
    because genre match adds +2.0 to the score.
    """
    ...


def test_retrieve_handles_unknown_genre_gracefully():
    """
    If the prefs dict contains a genre not in the catalog (e.g.,
    'country'), retrieve_candidates() should still return top_n results
    — ranked by mood and energy only — without raising an exception.
    """
    ...


def test_retrieve_top_n_larger_than_catalog_returns_all_songs():
    """
    If top_n exceeds the catalog size (e.g., top_n=100 with 20 songs),
    retrieve_candidates() should return all available songs without
    crashing. This mirrors the k > catalog size edge case from the
    existing test suite.
    """
    ...


# ---------------------------------------------------------------------------
# format_candidates_for_prompt
# ---------------------------------------------------------------------------

def test_format_candidates_contains_all_titles():
    """
    Every song title in the candidates list should appear in the
    formatted string. If a title is missing, Claude cannot reference it
    in its response.
    """
    ...


def test_format_candidates_is_a_string():
    """
    format_candidates_for_prompt() must return a str, not a list or
    dict. The rag_context builder concatenates this directly into the
    prompt string.
    """
    ...


def test_format_candidates_includes_score():
    """
    Each candidate block in the formatted output should include the
    numeric score so Claude has explicit ranking context, not just a
    flat list.
    """
    ...
