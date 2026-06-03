# Idea & Progress Tracking Research Assistant

## What this is
A personal tool that (1) captures my research ideas and summarizes them into my
notes, (2) pressure-tests each idea against my base paper and the live literature,
and (3) tracks each idea's progress as I run experiments. I run experiments in my
terminal and paste the output into the app; the assistant interprets the results
and updates the record for that idea.

This is a tool I actually use. It must run end to end, not just look complete.

## Exact stack (do not substitute)
- Python 3.11+
- Orchestration: langgraph + langchain-anthropic
- Base-paper RAG: pymupdf (parse) -> RecursiveCharacterTextSplitter (chunk)
  -> chromadb (local vector store) -> OpenAI text-embedding-3-small
- Literature search: `arxiv` package + Semantic Scholar API (both free, no key)
- Idea + progress storage: append/update Markdown sections in ideas.md (see below)
- UI: Streamlit
- Tracing: LangSmith (env vars only)

## How I interact with it
- New idea: I type or paste an idea into the Streamlit box.
- New result: I paste raw experiment output (terminal logs, metrics, a short
  description) into the Streamlit box and indicate which idea it belongs to.
- Every run pauses at a human checkpoint so I can approve or edit before anything
  is written to ideas.md.

## Architecture: a LangGraph with a router and two paths
A `router` node at the front classifies the input as a NEW IDEA or a NEW RESULT
and sends it down the matching path. The `critic` node is shared by both paths.

Nodes:
1. router            - classify input: "new_idea" or "result"; if a result, identify which idea
2. summarize         - raw idea -> clean structured note (new-idea path)
3. retrieve_base     - RAG over the base paper PDF
4. search_lit        - query arXiv + Semantic Scholar
5. interpret_result  - parse pasted experiment output vs the idea's hypothesis / baseline (result path)
6. critic            - new idea: judge novelty / conflicts with base paper / prior art.
                       result: comment on whether the result supports the idea or conflicts with the base paper.
7. human_checkpoint  - LangGraph interrupt(); I approve or edit
8. persist           - append a NEW idea + critique to ideas.md
9. update_idea       - update an EXISTING idea's status and append a dated result to its log

Flow (new idea):
  router -> summarize -> retrieve_base + search_lit -> critic -> human_checkpoint -> persist

Flow (new result):
  router -> interpret_result -> retrieve_base (for the relevant idea) -> critic -> human_checkpoint -> update_idea

## Progress tracking (ideas have a lifecycle — NOT append-only)
Each idea carries a status that changes over time as I run experiments:

  proposed -> testing -> supported / refuted / inconclusive

Each idea also has a dated log of experiment results. Logging a result interprets
the pasted output, lets the critic comment, then (after my approval) updates that
idea's status and appends a dated entry to its results log.

## State schema (the fields the graph passes between nodes)
Use a single TypedDict for graph state. Suggested shape:

```python
from typing import TypedDict, Optional, Literal

Status = Literal["proposed", "testing", "supported", "refuted", "inconclusive"]

class GraphState(TypedDict, total=False):
    input_text: str                 # raw text I pasted
    input_type: Literal["new_idea", "result"]   # set by router
    target_idea_id: Optional[str]   # which idea a result belongs to (result path)

    # new-idea path
    summary: dict                   # {title, statement, rationale, assumptions}

    # shared retrieval / search
    base_context: list[str]         # retrieved base-paper chunks
    literature: list[dict]          # [{title, abstract_snippet, url, year}]

    # result path
    result_analysis: dict           # {vs_hypothesis, vs_baseline, metrics, surprises}

    # shared output
    critique: str                   # critic's assessment / advice
    new_status: Status              # proposed status after this run
    approved: bool                  # set at the human checkpoint
    user_edits: Optional[str]       # any edits I make at the checkpoint
```

## Storage detail (ideas.md format)
Start with Markdown. Each idea is one section. Match this layout exactly so the
update_idea node can find and modify sections reliably:

```markdown
## [idea-0003] Short idea title
Status: testing
Created: 2026-06-02

**Idea:** one-paragraph statement of the idea.
**Why it matters / rationale:** ...
**Assumptions:** ...
**Critic notes:** novelty, conflicts with base paper, prior art found.

### Results log
- 2026-06-04 — supported: beat baseline 0.71 -> 0.78 F1. Critic: matches arXiv:xxxx.
- 2026-06-06 — inconclusive: high variance across seeds, rerun needed.
```

Each idea gets a stable id like `idea-0001`. The id is how a pasted result is
linked to its idea (`target_idea_id`).

If updating sections in Markdown becomes fragile, switch to SQLite (table `ideas`;
table `results` with a foreign key `idea_id`). ASK ME before switching.

## Rules
- All API keys go in a .env file, loaded with python-dotenv. NEVER hardcode keys.
- Keep a .env.example with key names but no values. Ensure .env is in .gitignore.
- Maintain requirements.txt as you add packages.
- v1 uses plain dense retrieval. Do NOT add hybrid search or a reranker yet.
- Keep functions small and readable. One node per function where practical.
- After each phase, actually RUN the code and confirm it works before saying done.
- ASK ME before any big architectural change (e.g. switching storage to SQLite,
  changing the node graph, or swapping a library in the stack above).

## Build phases (build in this order — do one phase at a time)
- Phase 1: Scaffold the repo (folder structure, requirements.txt, .env.example,
  Python .gitignore). Build the LangGraph skeleton with all nodes defined but
  stubbed; make summarize and persist fully work. Minimal Streamlit page: paste an
  idea -> it's summarized -> appended to ideas.md. Run it and prove it works.
- Phase 2: Implement retrieve_base (base-paper RAG) and search_lit (arXiv +
  Semantic Scholar) as real tools, then write the critic for the NEW IDEA path.
- Phase 3: Add the human_checkpoint with interrupt() and wire it into Streamlit
  (show critique, approve/edit buttons). Turn on LangSmith tracing. Write the
  README. Prep for Streamlit Community Cloud deploy.
- Phase 4 (progress tracking — build LAST): add the router, interpret_result, and
  update_idea nodes plus the status lifecycle. Now I can paste experiment output,
  have the critic comment on it, and update an existing idea's status and results
  log. This is layered on top only after Phases 1-3 run end to end.
```
