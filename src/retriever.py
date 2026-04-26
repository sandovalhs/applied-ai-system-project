"""
retriever.py — Stage 2: Retrieve Candidate Songs (RAG Retrieval Step)

Given a validated prefs dict, scores every song in the catalog and
returns the top N candidates. This is the "retrieval" half of RAG.

Reuses the existing score_song / recommend_songs logic from recommender.py
so no scoring rules are duplicated.
"""

from typing import Dict, List, Tuple

from .recommender import recommend_songs


def retrieve_candidates(
    prefs: dict,
    songs: List[Dict],
    top_n: int = 10,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song against prefs and return the top_n highest-scoring
    candidates, capped at the catalog size.

    top_n is intentionally larger than the final k (default 10 vs final 5)
    so Claude has a meaningful pool to reason over in the generation stage.
    """
    return recommend_songs(prefs, songs, k=min(top_n, len(songs)))


def format_candidates_for_prompt(
    candidates: List[Tuple[Dict, float, str]],
) -> str:
    """
    Render the candidate list as a structured, numbered text block ready
    to embed inside a Claude prompt.

    Each entry shows the title, artist, score, key audio features, and
    the scoring reason so Claude can reference specific songs unambiguously.

    Example entry:
        #1  Hype Boy by New Jeans  (score 2.99/4.0)
            genre: kpop | mood: happy | energy: 0.77 | tempo: 120 BPM
            why scored: genre match (kpop, +2.0), energy similarity 0.92/1.0
    """
    entries = [
        f"#{i}  {song['title']} by {song['artist']}  (score {score:.2f}/4.0)\n"
        f"    genre: {song['genre']} | mood: {song['mood']} | "
        f"energy: {song['energy']} | tempo: {song['tempo_bpm']:.0f} BPM\n"
        f"    why scored: {reason}"
        for i, (song, score, reason) in enumerate(candidates, start=1)
    ]
    return "\n\n".join(entries)
