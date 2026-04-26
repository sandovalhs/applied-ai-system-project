"""
nl_parser.py — Stage 1: Natural Language → Structured Preferences

Responsibility: Take a raw user query (plain English) and ask Claude to
extract a structured preferences dictionary from it.

This is the entry point of the RAG pipeline. Nothing downstream runs
until this stage produces a valid prefs dict.
"""

from typing import Optional


def parse_query(user_query: str) -> dict:
    """
    Send the user's natural language query to the Claude API and extract
    a structured preferences dictionary from the response.

    Claude is given a system prompt that tells it the exact keys it must
    return (genre, mood, energy, tempo_bpm, valence, danceability,
    acousticness, speechiness_range, loudness_db, instrumentalness) and
    their expected types/ranges. The response is parsed from Claude's
    JSON output into a Python dict.

    Parameters
    ----------
    user_query : str
        Raw free-text input from the user, e.g.
        "something hype for a late-night drive, kind of trap-ish"

    Returns
    -------
    dict
        Structured prefs dict ready to be passed to retrieve_candidates().
        Example:
        {
            "genre": "trap",
            "mood":  "hype",
            "energy": 0.85,
            "tempo_bpm": 140,
            ...
        }

    Raises
    ------
    ValueError
        If Claude's response cannot be parsed into a valid prefs dict.
    """
    ...


def validate_prefs(prefs: dict) -> dict:
    """
    Guardrail that checks and normalizes the prefs dict returned by
    parse_query() before it is used downstream.

    Checks performed:
    - All required keys are present; missing keys get safe defaults.
    - String values (genre, mood) are lowercased and stripped.
    - Float values (energy, valence, etc.) are clamped to [0.0, 1.0].
    - tempo_bpm is clamped to a realistic range (40–250 BPM).
    - speechiness_range is a tuple of two floats in the correct order.

    This function never raises — it always returns a usable dict, even
    if the input was malformed. Corrections are logged so the developer
    can see when Claude returned unexpected values.

    Parameters
    ----------
    prefs : dict
        Raw prefs dict from parse_query(), possibly incomplete or
        containing out-of-range values.

    Returns
    -------
    dict
        A cleaned, normalized prefs dict safe to pass to the retriever.
    """
    ...


def build_system_prompt() -> str:
    """
    Return the static system prompt sent to Claude on every call to
    parse_query().

    The prompt instructs Claude to:
    - Act as a music taste extractor, not a general chatbot.
    - Output only a JSON object with the required keys.
    - Use null for any preference the user did not mention (so
      validate_prefs() can fill in defaults instead of guessing).
    - Never add commentary outside the JSON block.

    Returns
    -------
    str
        The system prompt string.
    """
    ...
