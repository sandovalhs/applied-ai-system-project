"""
app.py — Streamlit UI

Responsibility: Provide a browser-based interface where the user types
a natural language query and sees the top-K song recommendations
returned by the RAG pipeline.

Run with:
    streamlit run app.py

The app loads songs.csv once at startup, then calls run_pipeline() on
every query submission. Results are displayed with title, artist, score,
and Claude's plain-English explanation for each pick.
"""

import streamlit as st
from src.recommender import load_songs
from src.rag_recommender import run_pipeline
from src.logger import get_logger


def setup_page() -> None:
    """
    Configure the Streamlit page title, layout, and any global CSS or
    header text shown at the top of the app.

    Called once at the top of main() before any widgets are rendered.
    Sets the page to wide layout so the results table has room to
    breathe.
    """
    ...


def render_query_input() -> str:
    """
    Render the text input box and submit button for the user's query.

    Returns the query string when the user clicks Submit, or an empty
    string if the button has not been clicked yet. The input is
    pre-populated with an example query so new users know what to type.

    Returns
    -------
    str
        The user's query text, or "" if not yet submitted.
    """
    ...


def render_recommendations(recommendations: list) -> None:
    """
    Display the final list of recommended songs in the Streamlit UI.

    For each (song_dict, explanation) tuple in the list, renders:
    - Rank number and song title + artist as a header.
    - Key audio features (genre, mood, energy, tempo) as a small table
      or inline metrics so the user can see why it was picked.
    - Claude's one-sentence explanation as a callout block.

    If the recommendations list is empty (pipeline returned nothing),
    shows a friendly error message instead of a blank screen.

    Parameters
    ----------
    recommendations : list of (song_dict, explanation_string) tuples
        Output from run_pipeline().
    """
    ...


def render_debug_expander(prefs: dict, candidates: list) -> None:
    """
    Render a collapsed "Debug / How it worked" section below the results.

    When expanded, shows:
    - The structured prefs dict that Claude extracted from the query.
    - The full candidate list with scores before Claude re-ranked them.

    This section is hidden by default so it doesn't clutter the main
    view, but it's essential for demonstrating the RAG pipeline to
    graders or evaluators.

    Parameters
    ----------
    prefs : dict
        Validated prefs dict from the parse stage.
    candidates : list of (song_dict, score, reason_string) tuples
        Retrieved candidates before generation.
    """
    ...


def main() -> None:
    """
    Entry point for the Streamlit app.

    Execution order:
    1. setup_page()          — configure layout and title
    2. load_songs()          — load catalog once, cache with st.cache_data
    3. render_query_input()  — show text box, wait for submission
    4. run_pipeline()        — run all four RAG stages if query is present
    5. render_recommendations() — display results
    6. render_debug_expander()  — show internals in a collapsed section

    All exceptions from run_pipeline() are caught here and shown as a
    Streamlit error message so the app never shows a raw traceback to
    the user.
    """
    ...


if __name__ == "__main__":
    main()
