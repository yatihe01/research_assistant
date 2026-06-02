from datetime import date
from pathlib import Path
import re


IDEAS_PATH = Path("ideas.md")


def append_idea(
    summary: dict,
    critique: str = "Critic not implemented in Phase 1.",
    status: str = "proposed",
    ideas_path: Path = IDEAS_PATH,
) -> str:
    idea_id = next_idea_id(ideas_path)
    section = format_idea_section(idea_id, summary, critique, status)
    ideas_path.parent.mkdir(parents=True, exist_ok=True)
    existing = ideas_path.read_text(encoding="utf-8") if ideas_path.exists() else ""
    separator = "\n" if existing and not existing.endswith("\n") else ""
    ideas_path.write_text(f"{existing}{separator}{section}", encoding="utf-8")
    return idea_id


def next_idea_id(ideas_path: Path = IDEAS_PATH) -> str:
    if not ideas_path.exists():
        return "idea-0001"

    content = ideas_path.read_text(encoding="utf-8")
    ids = [int(match) for match in re.findall(r"## \[idea-(\d{4})\]", content)]
    next_number = max(ids, default=0) + 1
    return f"idea-{next_number:04d}"


def format_idea_section(idea_id: str, summary: dict, critique: str, status: str) -> str:
    title = _clean_inline(summary.get("title") or "Untitled idea")
    statement = _clean_paragraph(summary.get("statement") or "")
    rationale = _clean_paragraph(summary.get("rationale") or "")
    assumptions = _format_assumptions(summary.get("assumptions") or [])
    critic_notes = _clean_paragraph(critique)

    return (
        f"## [{idea_id}] {title}\n"
        f"Status: {status}\n"
        f"Created: {date.today().isoformat()}\n\n"
        f"**Idea:** {statement}\n"
        f"**Why it matters / rationale:** {rationale}\n"
        f"**Assumptions:** {assumptions}\n"
        f"**Critic notes:** {critic_notes}\n\n"
        "### Results log\n\n"
    )


def _format_assumptions(assumptions: list[str]) -> str:
    cleaned = [_clean_inline(item) for item in assumptions if str(item).strip()]
    return "; ".join(cleaned) if cleaned else "None recorded yet."


def _clean_inline(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def _clean_paragraph(value: object) -> str:
    return _clean_inline(value) or "To be refined."

