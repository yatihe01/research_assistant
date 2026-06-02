import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def critique_new_idea(
    summary: dict[str, Any],
    base_context: list[str],
    literature: list[dict[str, Any]],
) -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _critique_with_anthropic(summary, base_context, literature)
        except Exception as exc:
            return f"{_fallback_critique(summary, base_context, literature)} Anthropic critique failed: {exc}"

    return _fallback_critique(summary, base_context, literature)


def _critique_with_anthropic(
    summary: dict[str, Any],
    base_context: list[str],
    literature: list[dict[str, Any]],
) -> str:
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
    prompt = (
        "Critique this new research idea. Judge novelty, conflicts with the base paper, "
        "nearby prior art, and one concrete next experiment. Be concise.\n\n"
        f"Summary:\n{summary}\n\n"
        f"Base paper context:\n{_format_base_context(base_context)}\n\n"
        f"Literature search:\n{_format_literature(literature)}"
    )
    response = model.invoke(prompt)
    return response.content if isinstance(response.content, str) else str(response.content)


def _fallback_critique(
    summary: dict[str, Any],
    base_context: list[str],
    literature: list[dict[str, Any]],
) -> str:
    lit_titles = [
        paper["title"]
        for paper in literature
        if paper.get("title") and "unavailable" not in str(paper.get("title", "")).lower()
    ]
    base_note = (
        "Base-paper retrieval found relevant context."
        if base_context
        else "Base-paper retrieval is not configured yet; set BASE_PAPER_PATH and OPENAI_API_KEY."
    )
    lit_note = (
        "Nearby literature found: " + "; ".join(lit_titles[:3]) + "."
        if lit_titles
        else "Literature search did not return usable papers in this run."
    )
    return (
        f"{base_note} {lit_note} Initial advice: treat '{summary.get('title', 'this idea')}' "
        "as proposed until Phase 3 approval and a baseline experiment are added."
    )


def _format_base_context(base_context: list[str]) -> str:
    if not base_context:
        return "No base-paper context retrieved."
    return "\n\n".join(f"- {chunk}" for chunk in base_context[:4])


def _format_literature(literature: list[dict[str, Any]]) -> str:
    if not literature:
        return "No literature retrieved."
    return "\n".join(
        f"- {paper.get('title')} ({paper.get('year')}): {paper.get('abstract_snippet')} {paper.get('url')}"
        for paper in literature[:6]
    )
