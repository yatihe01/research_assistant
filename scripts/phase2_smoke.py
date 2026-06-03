from pathlib import Path
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from research_assistant.graph import process_new_idea
from research_assistant.summarizer import summarize_idea


def main() -> None:
    summary = summarize_idea("Chess paper:\nHow do we describe an optimal strategy?")
    assert summary["title"] == "Chess paper"

    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            result = process_new_idea(
                "Chess paper:\n"
                "How do we describe an optimal chess strategy in natural language, "
                "then evaluate it by having an LLM play under that description?"
            )
            ideas = Path("ideas.md").read_text(encoding="utf-8")
        finally:
            os.chdir(cwd)

    assert result["summary"]["title"] == "Chess paper"
    assert result["new_status"] == "proposed"
    assert "## [idea-0001] Chess paper" in ideas
    assert "**Critic notes:**" in ideas
    assert "literature" in result
    assert "base_context" in result
    print("Phase 2 smoke test passed: title, retrieval/search nodes, critic, and persistence ran.")


if __name__ == "__main__":
    main()
