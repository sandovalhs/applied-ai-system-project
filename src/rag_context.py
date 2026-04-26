"""
rag_context.py — Stage 3: Build the Enriched Claude Prompt (RAG Augmentation)

Combines the user's original query, the extracted prefs, and the
formatted candidate songs into a single prompt. By injecting real catalog
data here, Claude's answer is grounded in actual songs — it cannot invent
titles or artists that don't exist in the retrieved set.
"""


def build_rag_prompt(
    user_query: str,
    prefs: dict,
    formatted_candidates: str,
    k: int = 5,
) -> str:
    """
    Assemble the enriched prompt sent to Claude in the generation stage.

    Three sections:
    1. The user's verbatim query so Claude understands the intent.
    2. The inferred taste profile (non-empty/non-default prefs only).
    3. The numbered candidate block with an explicit instruction to pick
       only from that list.
    """
    prefs_lines = "\n".join(
        f"  {key}: {value}"
        for key, value in prefs.items()
        if value not in ("", None, 0.0)
    )

    return (
        f'User\'s request: "{user_query}"\n\n'
        f"Inferred taste profile:\n{prefs_lines}\n\n"
        f"Candidate songs from the catalog (already scored against preferences):\n\n"
        f"{formatted_candidates}\n\n"
        f"Choose the {k} best songs from the list above. "
        f"For each pick, write one sentence explaining why it fits the user's vibe."
    )


def build_generation_system_prompt() -> str:
    """
    Return the static system prompt used during the generation stage.

    Claude acts as a music curator, not a preference extractor. The key
    constraint: it may only recommend songs from the provided candidate list.
    Output format is strict so parse_claude_response() can extract picks
    reliably with a single regex pass.
    """
    return """\
You are a music curator. You will receive a user's vibe description, their inferred
taste profile, and a numbered list of candidate songs with scores.

Rules:
- Recommend ONLY songs from the provided candidate list. Never invent titles or artists.
- Output exactly this format for each pick (one per line, no extra text before or after):
    N. Title by Artist — one-sentence explanation referencing the user's vibe.
- Use a real em dash (—) as the separator between the song and explanation.
- Do not add any introductory text, closing remarks, or blank lines between picks."""
