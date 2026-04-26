# System Diagram — Natural Language Music Recommender (RAG)

## Architecture Overview

```mermaid
flowchart TD
    U(["👤 User\n(natural language query)\ne.g. 'hype songs for a late-night drive'"])

    U -->|raw text input| PARSE

    subgraph PARSE["① Parse — Intent Extraction"]
        P["Claude NL Parser\n──────────────────\n• Reads user's free-text query\n• Extracts structured preferences\n  genre · mood · energy · tempo · valence\n• Returns a prefs dict"]
    end

    subgraph RAG["② Retrieve + Augment — RAG Core"]
        DB[("📀 songs.csv\n20 songs with\naudio features")]
        R["Song Retriever\n──────────────────\n• Calls existing score_song logic\n• Scores every song against prefs\n• Returns top candidate songs\n  with scores + reasons"]
        CTX["RAG Context Builder\n──────────────────\n• Combines prefs dict\n  + retrieved songs\n  into a structured Claude prompt\n• AI answer is grounded in\n  real catalog data, not invented"]
        DB --> R
        PARSE -->|structured prefs dict| R
        R -->|top candidate songs + scores| CTX
        PARSE -->|prefs| CTX
    end

    subgraph GEN["③ Generate — AI Response"]
        G["Claude Recommender\n──────────────────\n• Receives enriched prompt\n  with retrieved songs as context\n• Ranks best matches\n• Generates plain-English\n  explanation for each pick"]
    end

    subgraph OUT["④ Output"]
        UI["Streamlit UI\n──────────────────\n• Displays Top-K songs\n• Shows score + reason per song\n• Text input box for next query"]
    end

    RAG -->|enriched prompt| GEN
    GEN -->|Top-K songs + explanations| OUT
    OUT -->|reads results| U

    subgraph OBS["Logging & Guardrails  (runs throughout)"]
        LOG[("📋 Logger\n──────────────\nlogs: raw query\nextracted prefs\nretrieved candidates\nfinal response\nerrors + fallbacks")]
    end

    PARSE -.->|log extracted prefs| LOG
    RAG   -.->|log retrieved songs| LOG
    GEN   -.->|log AI response| LOG

    subgraph CHECK["Human & Automated Checks"]
        T["pytest Test Suite\n──────────────────\n• Consistency: same query → same prefs\n• Guardrails: bad input doesn't crash\n• Retrieval: k songs always returned\n• Coverage: edge-case user profiles"]
        HR(["👤 Human Reviewer\nchecks that recommendations\n'make sense' for the query"])
    end

    T   -->|validates each component| PARSE
    T   -->|validates each component| RAG
    T   -->|validates each component| GEN
    HR  -->|reviews output quality| OUT
```

---

## Data Flow Summary

| Step | Component | Input | Output |
|------|-----------|-------|--------|
| 1 | **Claude NL Parser** | Free-text query | Structured prefs dict |
| 2 | **Song Retriever** | Prefs dict + songs.csv | Scored candidate songs |
| 3 | **RAG Context Builder** | Prefs + candidates | Enriched Claude prompt |
| 4 | **Claude Recommender** | Enriched prompt | Top-K songs + explanations |
| 5 | **Streamlit UI** | Recommendations | User-facing display |

---

## Why This is RAG (Not Just a Chatbot)

Without RAG, Claude would guess song recommendations from training data.
With RAG, Claude's answer is **grounded in the actual catalog** — it can only recommend songs that exist in `songs.csv`, with accurate feature values.

```
Without RAG:  User query ──→ Claude ──→ made-up recommendations
With RAG:     User query ──→ Retrieve from catalog ──→ Claude ──→ grounded recommendations
```

---

## Where Humans Are Involved

1. **Query input** — user writes the natural language query
2. **Output review** — human reads recommendations and judges if they feel right
3. **Test authoring** — developer writes pytest cases for consistency and edge cases
4. **Guardrail tuning** — developer adjusts logging + error handling based on observed failures
