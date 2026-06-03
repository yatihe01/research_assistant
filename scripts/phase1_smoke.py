from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from research_assistant.graph import process_new_idea


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = Path.cwd()
        try:
            import os

            os.chdir(tmpdir)
            result = process_new_idea(
                "Use uncertainty-aware retrieval to decide when a small model should ask "
                "for additional paper context before proposing an experiment."
            )
            ideas = Path("ideas.md").read_text(encoding="utf-8")
        finally:
            os.chdir(cwd)

    assert result["persisted_idea_id"] == "idea-0001"
    assert "## [idea-0001]" in ideas
    assert "Status: proposed" in ideas
    assert "**Idea:**" in ideas
    print("Phase 1 smoke test passed: summarized and appended idea-0001.")


if __name__ == "__main__":
    main()

