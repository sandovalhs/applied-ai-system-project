"""
app.py — Streamlit UI

Browser-based interface for the Natural Language Music Recommender.
The user types a free-text query and sees Top-K song recommendations
with Claude's explanation for each pick, plus a collapsible debug panel
showing the intermediate RAG state.

Run with:
    streamlit run app.py
"""

import streamlit as st

from src.logger import get_logger, log_error
from src.nl_parser import parse_query, validate_prefs
from src.rag_context import build_rag_prompt
from src.rag_recommender import generate_recommendations
from src.recommender import load_songs
from src.retriever import format_candidates_for_prompt, retrieve_candidates

_EXAMPLE_QUERY = "something hype for a late-night drive, kind of trap-ish"
_K = 5


def setup_page() -> None:
    """Configure page title, icon, layout, and header text."""
    st.set_page_config(
        page_title="Music Recommender",
        page_icon="🎵",
        layout="wide",
    )
    st.title("🎵 Natural Language Music Recommender")
    st.caption(
        "Describe your vibe in plain English. "
        "Claude will extract your preferences, retrieve matching songs, "
        "and explain every pick — powered by RAG."
    )


@st.cache_data
def load_catalog() -> list:
    """Load songs.csv once and cache it for the lifetime of the session."""
    return load_songs("data/songs.csv")


def render_query_input() -> str:
    """
    Render the text input and Submit button inside a form.

    Returns the stripped query string on submission, or an empty string
    if the button has not been clicked yet.
    """
    with st.form("query_form"):
        query = st.text_input(
            "What do you want to listen to?",
            placeholder=_EXAMPLE_QUERY,
        )
        submitted = st.form_submit_button("Recommend")
    return query.strip() if submitted else ""


def render_recommendations(recommendations: list) -> None:
    """
    Display each (song_dict, explanation) tuple as a card-style block.

    Shows rank, title, artist, four audio metrics, and Claude's
    one-sentence explanation. Falls back to a warning if the list is empty.
    """
    if not recommendations:
        st.warning("No recommendations returned. Try rephrasing your query.")
        return

    st.subheader("Your Recommendations")
    for i, (song, explanation) in enumerate(recommendations, start=1):
        with st.container():
            st.markdown(f"**#{i} — {song['title']}** by {song['artist']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Genre", song["genre"])
            c2.metric("Mood", song["mood"])
            c3.metric("Energy", f"{song['energy']:.2f}")
            c4.metric("Tempo", f"{song['tempo_bpm']:.0f} BPM")
            st.info(explanation)
            st.divider()


def render_debug_expander(prefs: dict, candidates: list) -> None:
    """
    Render a collapsed 'How it worked' section below the results.

    Shows the prefs dict Claude extracted and the full scored candidate
    list before Claude re-ranked them — essential for demonstrating the
    RAG pipeline to evaluators.
    """
    with st.expander("Debug — How it worked", expanded=False):
        st.subheader("Extracted Preferences")
        st.json(prefs)

        st.subheader("Retrieved Candidates (before Claude re-ranked)")
        for song, score, reason in candidates:
            st.markdown(
                f"**[{score:.2f}]** {song['title']} by {song['artist']} — _{reason}_"
            )


def main() -> None:
    """
    Streamlit entry point.

    Calls each pipeline stage individually (rather than run_pipeline) so
    the intermediate prefs and candidates are available for the debug panel.
    All exceptions are caught and shown as a user-friendly error message.
    """
    setup_page()
    songs = load_catalog()
    query = render_query_input()

    if not query:
        return

    logger = get_logger()

    with st.spinner("Finding your songs..."):
        try:
            prefs = validate_prefs(parse_query(query))
            candidates = retrieve_candidates(prefs, songs, top_n=_K * 2)
            formatted = format_candidates_for_prompt(candidates)
            prompt = build_rag_prompt(query, prefs, formatted, k=_K)
            recommendations = generate_recommendations(prompt, candidates, k=_K)
        except Exception as exc:
            log_error(logger, exc, "app.main", query)
            st.error(f"Something went wrong: {exc}")
            return

    render_recommendations(recommendations)
    render_debug_expander(prefs, candidates)


if __name__ == "__main__":
    main()
