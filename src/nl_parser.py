"""
nl_parser.py — Stage 1: Natural Language → Structured Preferences

Takes a raw user query and asks Gemini to extract a structured
preferences dictionary from it. This is the entry point of the RAG
pipeline — nothing downstream runs until this stage produces a valid dict.
"""

import json
import os
import re

from google import genai
from google.genai import types

# Keys expected in every prefs dict, with safe defaults used when Claude
# returns null or omits a key entirely.
_DEFAULTS: dict = {
    "genre": "",
    "mood": "",
    "energy": 0.5,
    "tempo_bpm": 100.0,
    "valence": 0.5,
    "danceability": 0.5,
    "acousticness": 0.3,
    "speechiness_range": (0.0, 0.5),
    "loudness_db": -8.0,
    "instrumentalness": 0.0,
}

# Float features whose valid range is [0.0, 1.0]
_UNIT_FLOAT_KEYS = (
    "energy", "valence", "danceability", "acousticness", "instrumentalness"
)


def build_system_prompt() -> str:
    """
    Return the static system prompt sent to Gemini on every parse_query call.

    Instructs the model to act as a music taste extractor, output only a
    JSON object with the required keys, and use null for anything the
    user did not mention.
    """
    return """\
You are a music taste extractor. Your only job is to read a user's natural language
music request and output a JSON object capturing their preferences.

Output ONLY a valid JSON object — no prose, no markdown code fences, no explanation.

Required keys and their types/constraints:
{
  "genre":             string | null   (e.g. "kpop", "trap", "lofi" — lowercase),
  "mood":              string | null   (e.g. "hype", "chill", "intense" — lowercase),
  "energy":            float 0.0–1.0  | null,
  "tempo_bpm":         float 40–250   | null,
  "valence":           float 0.0–1.0  | null  (0 = dark/sad, 1 = bright/happy),
  "danceability":      float 0.0–1.0  | null,
  "acousticness":      float 0.0–1.0  | null,
  "speechiness_range": [float, float] | null  (min and max, both 0.0–1.0),
  "loudness_db":       float          | null  (negative dB, e.g. -5.0),
  "instrumentalness":  float 0.0–1.0  | null
}

Use null for any preference the user did not mention. Never guess values not clearly implied by the input."""


def parse_query(user_query: str) -> dict:
    """
    Send the user's natural language query to Gemini and return the
    extracted preferences as a raw dict (before validation/normalization).

    The model is given a strict system prompt that requires JSON-only output.
    A regex extracts the JSON block in case the model adds any surrounding text,
    and json.loads converts it to a Python dict.

    Raises ValueError if no JSON object can be found or parsed.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
        ),
    )
    raw = response.text.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in Gemini response: {raw!r}")

    try:
        return json.loads(match.group())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse JSON from Gemini response: {raw!r}") from exc


def validate_prefs(prefs: dict) -> dict:
    """
    Normalize and guard the raw prefs dict before it reaches the retriever.

    Rules applied in order:
    - Missing or null keys fall back to _DEFAULTS.
    - genre and mood are lowercased and stripped.
    - Unit floats (energy, valence, etc.) are clamped to [0.0, 1.0].
    - tempo_bpm is clamped to [40, 250].
    - loudness_db is clamped to [-60, 0].
    - speechiness_range is coerced to a sorted tuple of two clamped floats.

    Always returns a complete, usable dict — never raises.
    """
    # Overlay non-null prefs values onto the defaults
    result = {
        **_DEFAULTS,
        **{k: v for k, v in prefs.items() if v is not None},
    }

    for key in ("genre", "mood"):
        if isinstance(result.get(key), str):
            result[key] = result[key].strip().lower()

    for key in _UNIT_FLOAT_KEYS:
        result[key] = float(max(0.0, min(1.0, result[key])))

    result["tempo_bpm"] = float(max(40.0, min(250.0, result["tempo_bpm"])))
    result["loudness_db"] = float(max(-60.0, min(0.0, result["loudness_db"])))

    sr = result["speechiness_range"]
    if isinstance(sr, list):
        sr = tuple(sr)
    a, b = (float(max(0.0, min(1.0, x))) for x in sr)
    result["speechiness_range"] = (min(a, b), max(a, b))

    return result
