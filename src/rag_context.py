"""
rag_context.py — Stage 3: Build the Enriched Claude Prompt (RAG Augmentation Step)

Responsibility: Combine the user's original query, the extracted prefs
dict, and the formatted candidate songs into a single prompt that
Claude will use to generate the final recommendations.

This is the "augmentation" half of Retrieval-Augmented Generation. By
injecting the real catalog data here, we guarantee that Claude's answer
is grounded in actual songs — it cannot invent titles or artists that
don't exist in the retrieved set.
"""


def build_rag_prompt(
    user_query: str,
    prefs: dict,
    formatted_candidates: str,
    k: int = 5,
) -> str:
    """
    Assemble the final prompt that will be sent to Claude in the
    generation stage.

    The prompt has three sections:
    1. The user's original query (verbatim) so Claude understands the
       intent in plain English.
    2. The extracted prefs dict rendered as a readable summary, so
       Claude knows what the parser inferred.
    3. The formatted candidate songs block from format_candidates_for_prompt(),
       with an instruction telling Claude to choose only from this list.

    Claude is also told the exact output format expected (title, artist,
    and a one-sentence explanation per pick) so the response is easy to
    parse in the generation stage.

    Parameters
    ----------
    user_query : str
        Original free-text query from the user.
    prefs : dict
        Validated and normalized prefs dict.
    formatted_candidates : str
        Pre-formatted candidate block from format_candidates_for_prompt().
    k : int
        How many songs Claude should pick. Passed into the prompt
        instructions so Claude knows the target count.

    Returns
    -------
    str
        Complete prompt string ready to send to the Claude API.
    """
    ...


def build_generation_system_prompt() -> str:
    """
    Return the static system prompt used during the generation stage.

    This is different from the system prompt in nl_parser.py. Here,
    Claude is acting as a music curator, not a preference extractor.

    The prompt tells Claude to:
    - Only recommend songs from the numbered candidate list provided.
    - Never invent song titles, artists, or features.
    - Explain each pick in one sentence referencing the user's stated
      vibe, not just the numeric score.
    - Output in a structured format (one song per line) so the response
      parser in rag_recommender.py can extract the picks reliably.

    Returns
    -------
    str
        System prompt string for the generation call.
    """
    ...
