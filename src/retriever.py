"""
retriever.py — Stage 2: Retrieve Candidate Songs (RAG Retrieval Step)

Responsibility: Given a structured prefs dict, score every song in the
catalog and return the top N candidates. This is the "retrieval" half
of Retrieval-Augmented Generation.

The existing score_song() and recommend_songs() functions in
recommender.py do the heavy lifting here. This module wraps them and
formats the results for the RAG context builder.
"""

from typing import List, Dict, Tuple


def retrieve_candidates(
    prefs: dict,
    songs: List[Dict],
    top_n: int = 10,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song in the catalog against the user's prefs and return
    the top_n highest-scoring candidates.

    Internally calls recommend_songs() from recommender.py so the same
    scoring logic is reused — no duplication. The only difference is
    that top_n is intentionally larger than the final k (default 10 vs
    final 5) so Claude has a meaningful pool to reason over in the
    generation stage.

    Parameters
    ----------
    prefs : dict
        Validated prefs dict from validate_prefs().
    songs : list[dict]
        Full song catalog loaded from songs.csv.
    top_n : int
        Number of candidates to retrieve. Should be at least 2× the
        final k so Claude has real choices to make.

    Returns
    -------
    list of (song_dict, score, reason_string) tuples
        Sorted highest-score first. Each tuple matches the format
        returned by recommend_songs().
    """
    ...


def format_candidates_for_prompt(
    candidates: List[Tuple[Dict, float, str]],
) -> str:
    """
    Convert the list of scored candidate tuples into a plain-text block
    that can be embedded directly inside a Claude prompt.

    Each candidate is rendered as a numbered entry showing title,
    artist, score, key audio features, and the scoring reason. The
    format is intentionally structured (not prose) so Claude can
    reference specific songs by number without ambiguity.

    Example output line:
        #3  ANTIFRAGILE by LE SSERAFIM  (score 3.86/4.0)
            genre: kpop | mood: intense | energy: 0.86 | tempo: 130 BPM
            why scored: genre match (kpop, +2.0), mood match (intense, +1.0), energy similarity 0.86/1.0

    Parameters
    ----------
    candidates : list of (song_dict, score, reason_string) tuples

    Returns
    -------
    str
        Multi-line formatted string ready to paste into a prompt.
    """
    ...
