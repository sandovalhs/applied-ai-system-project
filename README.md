# Show Me a Song 🎵
### A Natural Language Music Recommender powered by RAG + Gemini

---

## Table of Contents

1. [Project Summary](#project-summary)
2. [Original Project](#original-project)
3. [Architecture Overview](#architecture-overview)
4. [Setup Instructions](#setup-instructions)
5. [Sample Interactions](#sample-interactions)
6. [Design Decisions](#design-decisions)
7. [Testing Summary](#testing-summary)
8. [Reflection](#reflection)

---

## Project Summary

**Show Me a Song** is an AI-powered music recommender that lets you describe what you want to hear in plain English — and actually gets it right. Instead of clicking through genre filters or mood toggles, you type something like *"something dark and fast for a late-night drive"* and the system figures out the rest.

Under the hood, the app uses **Retrieval-Augmented Generation (RAG)**: it first extracts your musical preferences from your natural language query using Gemini, retrieves the best matching songs from a curated catalog using a scoring engine, and then passes that retrieved context back to Gemini to generate a final ranked list with a plain-English explanation for each pick. The result is a recommendation that is both grounded in real catalog data and explained in human terms — not a black box.

This matters because most recommendation systems either require rigid structured input (dropdowns, sliders) or operate as opaque black boxes users cannot interrogate. Show Me a Song is transparent by design: every recommendation shows you the score, the reasoning, and the audio features that drove the match.

---

## Original Project

This project extends **SuperCoolRecommender 1.0**, built during Modules 1–3 of the CodePath Applied AI course.

The original mission came from a startup music platform trying to understand how apps like Spotify and TikTok predict what users will love next. The goal was to simulate and explain how a basic recommendation system works by designing a modular Python architecture that transforms song data and structured "taste profiles" into personalized suggestions. The system scored every song in a 19-song catalog against a hand-crafted user profile using three signals — genre match (+2.0 pts), mood match (+1.0 pt), and energy proximity (up to +1.0 pt) — then returned the top K results with a plain-language explanation of each score.

Testing that system with adversarial profiles revealed its core limitation: the genre bonus was large enough to dominate every other signal, creating a "genre bubble" where mood and energy became nearly decorative. Show Me a Song was built to solve exactly that problem — by letting a language model interpret what the user actually means rather than forcing them to match catalog labels exactly.

---

## Architecture Overview

The system is a four-stage RAG pipeline. A full diagram is available in [`system_diagram.md`](system_diagram.md).

```
User types query
      │
      ▼
① Claude NL Parser        Sends query to Gemini, extracts a structured
                          prefs dict: {genre, mood, energy, tempo, ...}
      │
      ▼
② Song Retriever          Scores every song in songs.csv against the prefs
  (RAG: Retrieve)         dict using the original scoring engine. Returns
                          top N candidates with scores and reasons.
      │
      ▼
③ RAG Context Builder     Packages the user query + prefs + scored candidates
  (RAG: Augment)          into a single enriched prompt for Gemini.
      │
      ▼
④ Gemini Recommender      Receives the enriched prompt. Can only pick songs
  (RAG: Generate)         from the retrieved list — grounded, not hallucinated.
      │
      ▼
  Streamlit UI            Displays Top-K picks with audio metrics and
                          Claude's one-sentence explanation per song.
```

**Logging** runs at every stage boundary, writing to `logs/rag_pipeline.log`.
**Testing** covers each stage independently: pure functions are tested directly; Gemini API calls are mocked so the test suite runs fully offline.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd applied-ai-system-project
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

```bash
export GEMINI_API_KEY="your-key-here"
```

To make this permanent across sessions:

```bash
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

### 6. (Optional) Run the original CLI recommender

```bash
python3 -m src.main
```

### 7. (Optional) Run the test suite

No API key required — all Gemini calls are mocked.

```bash
pytest tests/ -v
```

---

## Sample Interactions

Each example below shows a natural language query, the structured preferences Gemini extracted, and the final recommendations returned by the system.

---

### Example 1

**Query:** `"something dark and fast for a late-night drive"`

<!-- Add screenshot here -->

---

### Example 2

**Query:** `"chill r&b to study to, nothing too intense"`

<!-- Add screenshot here -->

---

### Example 3

**Query:** `"hype kpop like ANTIFRAGILE"`

<!-- Add screenshot here -->

---

## Design Decisions

### Why RAG instead of pure prompt engineering?

The simplest approach would be to send the user's query directly to Gemini and ask it to recommend songs. The problem: Gemini would invent titles, fabricate artists, and produce songs that sound plausible but don't exist in the catalog. RAG solves this by injecting the actual catalog data into the prompt — Gemini can only pick from songs it was shown, so every recommendation is verifiable.

### Why keep the original scoring engine?

The rule-based scorer from Modules 1–3 is fast, deterministic, and transparent. Rather than replacing it, the RAG pipeline uses it as the retrieval layer: it narrows 57 songs down to the top 10 candidates before Gemini ever sees the prompt. This keeps API calls short and cheap, and it means the system degrades gracefully if the API is unavailable — the scored candidates are still meaningful on their own.

### Why Gemini for both stages?

Two separate Gemini calls are made: one to extract structured preferences from the user's query (Stage 1), and one to generate the final recommendations from the retrieved candidates (Stage 4). Each call uses a different system prompt tuned for its specific task — extractor vs. curator. Splitting them means each prompt stays small and focused, which reduces hallucination risk and makes failures easier to diagnose.

### Why Streamlit?

Streamlit was already in the project's `requirements.txt` and lets a functional UI be built in under 100 lines of Python. The collapsible debug panel (showing extracted prefs and raw candidate scores) is a direct product of this choice — it makes the RAG pipeline visible to anyone evaluating the project, not just developers reading the logs.

### Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Two Gemini calls per query | Clean separation of concerns | Doubles API latency vs. one call |
| Rule-based retriever (not semantic search) | No embeddings/vector DB required | Genre label mismatch still affects retrieval |
| `gemini-2.5-flash` model | Free tier, fast | Less capable than larger models on edge cases |
| 57-song catalog | Easy to inspect and debug | Too small to stress-test diversity meaningfully |

---

## Testing Summary

The project includes **48 automated tests** across four test files. All 48 pass. No API key is required to run them.

```
tests/test_recommender.py      2 tests   Original scoring logic
tests/test_nl_parser.py       18 tests   NL parsing + prefs validation
tests/test_retriever.py       13 tests   Candidate retrieval + formatting
tests/test_rag_pipeline.py    15 tests   End-to-end pipeline + response parser
```

### What worked

- **`validate_prefs`** was the most valuable function to test. It catches silent failures like mismatched string casing (`"KPop"` vs `"kpop"`), out-of-range floats, and inverted `speechiness_range` tuples — exactly the class of bugs that caused wrong results in the original recommender.
- **Mocking the Gemini API** with `unittest.mock.patch` worked cleanly. Patching `src.nl_parser.genai` and `src.rag_recommender.genai` independently meant each stage's behavior could be tested in isolation without any API calls.
- **`parse_claude_response`** edge cases were easy to write tests for (empty response, truncated list, titles containing the word "by") and all passed first try once `rfind(" by ")` was used instead of `find`.

### What didn't work at first

- The first switch from Anthropic to Gemini used the deprecated `google.generativeai` package, which produced `FutureWarning` and a different client API. Switching to `google.genai` required updating both source files and all test mocks.
- The first Gemini integration used `os.environ["GEMINI_API_KEY"]` which raised `KeyError` before the mock could intercept the call. Changing to `os.environ.get(...)` fixed it — the mock catches the `genai.Client()` call before any real API request is made.
- The free tier `429 RESOURCE_EXHAUSTED` error with `limit: 0` was caused by creating the API key from the Google Cloud Console rather than from AI Studio directly. Creating a new key at `aistudio.google.com` resolved it.

### What I learned

Writing the tests before the implementation existed (TDD-adjacent) forced clearer thinking about function boundaries. The hardest part was not the tests themselves but deciding exactly what each function should own — for example, whether `validate_prefs` should log corrections (it doesn't; logging is the caller's responsibility) and whether `parse_claude_response` should raise on a short response (it doesn't; it returns what it found and the caller handles it). Those decisions only became obvious when writing the test cases.

---

## Reflection

Building Show Me a Song taught me that the hardest part of an AI system is not the model — it is the plumbing around it. The Gemini API call itself is five lines of code. What took real thought was deciding how to structure the prompt so the model outputs parseable JSON, how to validate that output without crashing, how to match parsed titles back to catalog entries case-insensitively, and how to log enough information at each stage that failures can be diagnosed without re-running the whole pipeline.

The RAG architecture specifically changed how I think about language model limitations. A raw LLM will confidently fabricate song recommendations that sound real but aren't. RAG doesn't make the model smarter — it constrains it. By injecting the actual catalog into the prompt and telling the model it may only pick from that list, the output becomes trustworthy not because the model improved but because the environment it operates in changed. That reframing — thinking about what context you give the model, not just what model you use — felt like the most important practical lesson of the project.

The adversarial testing from Modules 1–3 also paid forward here. Having already documented exactly how the original scoring engine failed (genre dominance, case sensitivity, silent degradation on out-of-range inputs) made it straightforward to write targeted tests for the new pipeline. Every bug I expected showed up in the tests before it ever reached the UI.
