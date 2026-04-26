"""
rag_recommender.py — Stage 4: Generate Final Recommendations (RAG Generation Step)

Responsibility: Send the enriched prompt to Claude and parse its
response into a structured list of (song_dict, explanation) pairs that
the UI can render.

This is the "generation" half of Retrieval-Augmented Generation. Claude
receives real catalog data injected into the prompt and must only pick
from that set — the answer is grounded, not hallucinated.
"""

from typing import List, Dict, Tuple


def generate_recommendations(
    rag_prompt: str,
    candidates: List[Tuple[Dict, float, str]],
    k: int = 5,
) -> List[Tuple[Dict, str]]:
    """
    Send the RAG prompt to the Claude API and return a structured list
    of recommended songs with explanations.

    Steps inside this function:
    1. Call the Claude API with the rag_prompt and the generation
       system prompt from build_generation_system_prompt().
    2. Pass Claude's raw text response to parse_claude_response().
    3. Match each parsed title back to its full song dict from the
       candidates list so the caller gets complete song data.
    4. Return the final top-k list.

    Parameters
    ----------
    rag_prompt : str
        Fully assembled prompt from build_rag_prompt().
    candidates : list of (song_dict, score, reason_string) tuples
        The same candidate list used to build the prompt. Used here to
        look up full song dicts by title after Claude responds.
    k : int
        Expected number of recommendations. Used to validate that
        parse_claude_response() returned the right number of picks.

    Returns
    -------
    list of (song_dict, explanation_string) tuples
        Final recommendations in the order Claude ranked them.

    Raises
    ------
    ValueError
        If Claude's response contains titles not found in the candidates
        list (i.e., Claude invented a song that wasn't retrieved).
    """
    ...


def parse_claude_response(
    raw_response: str,
    k: int,
) -> List[Tuple[str, str]]:
    """
    Extract the list of (title, explanation) pairs from Claude's raw
    text output.

    Claude is prompted to follow a specific line format, e.g.:
        1. ANTIFRAGILE by LE SSERAFIM — matches your intense hype vibe with driving tempo.

    This function parses that structured output into clean Python tuples.
    If the response is malformed or has fewer than k picks, it logs a
    warning and returns whatever it could extract rather than raising.

    Parameters
    ----------
    raw_response : str
        Claude's full text response from the generation API call.
    k : int
        Expected number of picks. Used to detect truncated responses.

    Returns
    -------
    list of (title_string, explanation_string) tuples
        Parsed picks. May be shorter than k if Claude's response was
        incomplete — callers should handle this gracefully.
    """
    ...


def run_pipeline(
    user_query: str,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, str]]:
    """
    End-to-end convenience function that runs all four pipeline stages
    in sequence and returns the final recommendations.

    Stages called in order:
    1. nl_parser.parse_query()       — extract prefs from query
    2. nl_parser.validate_prefs()    — normalize and guard prefs
    3. retriever.retrieve_candidates() — score catalog, get top N
    4. retriever.format_candidates_for_prompt() — format for Claude
    5. rag_context.build_rag_prompt() — assemble enriched prompt
    6. generate_recommendations()    — call Claude, parse response

    Logging is called at each stage boundary so the full trace is
    written to the log file regardless of where a failure occurs.

    Parameters
    ----------
    user_query : str
        Raw natural language input from the user.
    songs : list[dict]
        Full catalog loaded from songs.csv.
    k : int
        Number of final recommendations to return.

    Returns
    -------
    list of (song_dict, explanation_string) tuples
    """
    ...
