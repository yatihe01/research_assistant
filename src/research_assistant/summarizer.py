import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()


SUMMARY_KEYS = ("title", "statement", "rationale", "assumptions")


def summarize_idea(raw_idea: str) -> dict[str, Any]:
    """Summarize an idea with Anthropic when configured, else use a local fallback."""
    text = raw_idea.strip()
    if not text:
        raise ValueError("Idea text cannot be empty.")

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _summarize_with_anthropic(text)
        except Exception:
            return _fallback_summary(text)

    return _fallback_summary(text)


def _summarize_with_anthropic(text: str) -> dict[str, Any]:
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
    prompt = (
        "Turn this research idea into JSON with exactly these keys: "
        "title, statement, rationale, assumptions. "
        "The title should be short. If the idea starts with an explicit label "
        "like 'Chess paper:', use that label as the title. "
        "The statement and rationale should each be "
        "one paragraph. Assumptions should be a concise list of strings.\n\n"
        f"Idea:\n{text}"
    )
    response = model.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)
    parsed = json.loads(_extract_json(content))
    return _normalize_summary(parsed, text)


def _fallback_summary(text: str) -> dict[str, Any]:
    first_sentence = _first_sentence(text)
    return {
        "title": _explicit_title(text) or _title_from_text(first_sentence),
        "statement": text,
        "rationale": "To be refined after the base paper and literature checks are implemented.",
        "assumptions": ["The idea can be evaluated against a measurable baseline."],
    }


def _normalize_summary(summary: dict[str, Any], original_text: str) -> dict[str, Any]:
    normalized = {key: summary.get(key, "") for key in SUMMARY_KEYS}
    normalized["title"] = _explicit_title(original_text) or _title_from_text(
        str(normalized["title"] or original_text)
    )
    normalized["statement"] = str(normalized["statement"] or original_text).strip()
    normalized["rationale"] = str(normalized["rationale"] or "").strip()

    assumptions = normalized["assumptions"]
    if isinstance(assumptions, str):
        assumptions = [assumptions]
    if not isinstance(assumptions, list):
        assumptions = []
    normalized["assumptions"] = [str(item).strip() for item in assumptions if str(item).strip()]
    return normalized


def _extract_json(content: str) -> str:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Anthropic response.")
    return match.group(0)


def _first_sentence(text: str) -> str:
    match = re.search(r"(.+?[.!?])(?:\s|$)", text, flags=re.DOTALL)
    return (match.group(1) if match else text).strip()


def _title_from_text(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text)
    title = " ".join(words[:8]) or "Untitled idea"
    return title[:80].strip().capitalize()


def _explicit_title(text: str) -> str | None:
    first_line = text.strip().splitlines()[0].strip()
    match = re.match(r"^([A-Za-z][A-Za-z0-9 &'/-]{1,60}):\s*", first_line)
    if not match:
        return None
    return _clean_title(match.group(1))


def _clean_title(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()[:80]
