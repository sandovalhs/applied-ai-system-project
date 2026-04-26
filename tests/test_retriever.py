"""
tests/test_retriever.py — Tests for the retrieval stage

All tests run against the real songs.csv — no mocking needed because
retrieve_candidates and format_candidates_for_prompt are pure functions
with no external dependencies.
"""

import pytest

from src.recommender import load_songs
from src.retriever import format_candidates_for_prompt, retrieve_candidates

SONGS = load_songs("data/songs.csv")

_BASE_PREFS = {
    "genre": "kpop",
    "mood": "hype",
    "energy": 0.85,
    "tempo_bpm": 130.0,
    "valence": 0.65,
    "danceability": 0.88,
    "acousticness": 0.03,
    "speechiness_range": (0.03, 0.82),
    "loudness_db": -4.5,
    "instrumentalness": 0.0,
}


# ---------------------------------------------------------------------------
# retrieve_candidates
# ---------------------------------------------------------------------------

def test_retrieve_returns_correct_count():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=5)
    assert len(candidates) == 5


def test_retrieve_returns_tuples_of_correct_shape():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=3)
    for item in candidates:
        song, score, reason = item
        assert isinstance(song, dict)
        assert isinstance(score, float)
        assert isinstance(reason, str)


def test_retrieve_results_are_sorted_descending():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=10)
    scores = [score for _, score, _ in candidates]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_genre_match_ranks_higher_than_no_match():
    """A kpop prefs dict should put kpop songs at the top."""
    candidates = retrieve_candidates({**_BASE_PREFS, "genre": "kpop"}, SONGS, top_n=3)
    assert candidates[0][0]["genre"] == "kpop"


def test_retrieve_unknown_genre_still_returns_top_n():
    """When no catalog song matches the genre, results come from mood/energy alone."""
    candidates = retrieve_candidates({**_BASE_PREFS, "genre": "country"}, SONGS, top_n=5)
    assert len(candidates) == 5


def test_retrieve_top_n_larger_than_catalog_returns_all_songs():
    """Requesting more results than the catalog size should silently cap at catalog size."""
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=999)
    assert len(candidates) == len(SONGS)


def test_retrieve_top_n_of_one_returns_single_best():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=1)
    assert len(candidates) == 1


def test_retrieve_each_result_has_required_song_keys():
    required = {"id", "title", "artist", "genre", "mood", "energy", "tempo_bpm"}
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=5)
    for song, _, _ in candidates:
        assert required.issubset(song.keys())


# ---------------------------------------------------------------------------
# format_candidates_for_prompt
# ---------------------------------------------------------------------------

def test_format_candidates_returns_string():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=3)
    assert isinstance(format_candidates_for_prompt(candidates), str)


def test_format_candidates_contains_all_titles():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=5)
    formatted = format_candidates_for_prompt(candidates)
    for song, _, _ in candidates:
        assert song["title"] in formatted


def test_format_candidates_contains_all_artists():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=5)
    formatted = format_candidates_for_prompt(candidates)
    for song, _, _ in candidates:
        assert song["artist"] in formatted


def test_format_candidates_includes_score():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=3)
    formatted = format_candidates_for_prompt(candidates)
    assert "/4.0" in formatted


def test_format_candidates_numbers_entries_from_one():
    candidates = retrieve_candidates(_BASE_PREFS, SONGS, top_n=3)
    formatted = format_candidates_for_prompt(candidates)
    assert "#1" in formatted
    assert "#2" in formatted
    assert "#3" in formatted
