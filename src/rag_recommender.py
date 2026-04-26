"""
rag_recommender.py — Stage 4: Generate Final Recommendations (RAG Generation)

Sends the enriched prompt to Gemini and parses its response into a
structured list of (song_dict, explanation) pairs. The model's answer is
grounded in the retrieved catalog — it cannot recommend songs that were
not passed in as candidates.
"""

import os
import re
from typing import Dict, List, Tuple

from google import genai
from google.genai import types

from .logger import get_logger, log_candidates, log_error, log_prefs, log_query, log_response
from .nl_parser import parse_query, validate_prefs
from .rag_context import build_generation_system_prompt, build_rag_prompt
from .retriever import format_candidates_for_prompt, retrieve_candidates


def generate_recommendations(
    rag_prompt: str,
    candidates: List[Tuple[Dict, float, str]],
    k: int = 5,
) -> List[Tuple[Dict, str]]:
    """
    Send the enriched RAG prompt to Gemini and return a structured list
    of (song_dict, explanation) tuples.

    Steps:
    1. Call the Gemini API with the rag_prompt and the generation system prompt.
    2. Log the raw response for debugging.
    3. Parse the response with parse_claude_response().
    4. Look up each parsed title in the candidates pool to retrieve the
       full song dict (case-insensitive match).

    Raises ValueError if Gemini recommends a title not found in candidates,
    which would indicate a RAG grounding failure.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=rag_prompt,
        config=types.GenerateContentConfig(
            system_instruction=build_generation_system_prompt(),
        ),
    )
    raw = response.text

    logger = get_logger()
    log_response(logger, raw)

    picks = parse_claude_response(raw, k)

    # Case-insensitive lookup so minor capitalisation differences don't break matching
    catalog = {song["title"].lower().strip(): song for song, _, _ in candidates}

    results = []
    for title, explanation in picks:
        song = catalog.get(title.lower().strip())
        if song is None:
            raise ValueError(
                f"Gemini recommended {title!r} which is not in the retrieved candidate list."
            )
        results.append((song, explanation))

    return results


def parse_claude_response(
    raw_response: str,
    k: int,
) -> List[Tuple[str, str]]:
    """
    Extract (title, explanation) pairs from Claude's structured text output.

    Expects lines of the form:
        1. Title by Artist — one-sentence explanation.

    Uses rfind(" by ") to handle titles that contain the word "by"
    (e.g. "Boy's a liar by PinkPantheress"). Returns fewer than k results
    without raising if Claude's response was truncated — callers handle
    short lists gracefully.
    """
    picks = []
    for line in raw_response.splitlines():
        line = line.strip()
        if not re.match(r"^\d+\.", line):
            continue

        line = re.sub(r"^\d+\.\s*", "", line)

        # Split on em-dash (—), en-dash (–), or spaced hyphen ( - )
        parts = re.split(r"\s*[—–]\s*|\s+-\s+", line, maxsplit=1)
        if len(parts) < 2:
            continue

        title_artist, explanation = parts[0].strip(), parts[1].strip()

        # rfind to handle "by" appearing inside the title
        by_idx = title_artist.lower().rfind(" by ")
        title = title_artist[:by_idx].strip() if by_idx != -1 else title_artist

        picks.append((title, explanation))
        if len(picks) == k:
            break

    return picks


def run_pipeline(
    user_query: str,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, str]]:
    """
    End-to-end convenience function that runs all four pipeline stages
    in sequence and returns the final (song_dict, explanation) list.

    Stages in order:
        parse_query → validate_prefs → retrieve_candidates →
        format_candidates_for_prompt → build_rag_prompt →
        generate_recommendations

    All exceptions are caught, logged, and converted to an empty list so
    the Streamlit UI never receives a raw traceback.
    Empty queries are rejected early before any API call is made.
    """
    logger = get_logger()

    if not user_query.strip():
        logger.warning("Empty query received — returning no recommendations.")
        return []

    log_query(logger, user_query)

    try:
        prefs = validate_prefs(parse_query(user_query))
        log_prefs(logger, prefs)

        candidates = retrieve_candidates(prefs, songs, top_n=k * 2)
        log_candidates(logger, candidates)

        formatted = format_candidates_for_prompt(candidates)
        prompt = build_rag_prompt(user_query, prefs, formatted, k=k)

        return generate_recommendations(prompt, candidates, k=k)

    except Exception as exc:
        log_error(logger, exc, "run_pipeline", user_query)
        return []
