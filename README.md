# Research Assistant

A Streamlit research notebook assistant for capturing ideas, checking them against a base paper and live literature, and saving notes to `ideas.md`.

## Current Status

Phases 1-2 are implemented:

- Phase 1: scaffold, LangGraph skeleton, working summarize and persist path.
- Phase 2: base-paper RAG, arXiv and Semantic Scholar search, new-idea critic.

Phase 3 human approval/checkpoint wiring is intentionally not included in this version.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` as needed:

```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
BASE_PAPER_PATH=base_paper.pdf
CHROMA_PATH=.chroma
LANGSMITH_TRACING=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```

`ANTHROPIC_API_KEY` enables LLM summarization and critique. Without it, the app uses deterministic fallbacks.

`OPENAI_API_KEY` and `BASE_PAPER_PATH` enable base-paper retrieval with `text-embedding-3-small`. Without them, the app still runs and records that base-paper retrieval is not configured.

## Base Paper

Put the PDF anywhere convenient and point `BASE_PAPER_PATH` at it. The simplest local setup is:

```bash
BASE_PAPER_PATH=base_paper.pdf
```

with `base_paper.pdf` in the repository root. The vector index is written to `.chroma/`, which is ignored by git.

## Run

```bash
.venv/bin/streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

## Tests

```bash
.venv/bin/python scripts/phase1_smoke.py
.venv/bin/python scripts/phase2_smoke.py
```
