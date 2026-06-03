from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


def base_paper_path() -> Path | None:
    value = os.getenv("BASE_PAPER_PATH", "").strip()
    if not value:
        return None
    return Path(value).expanduser()


def chroma_path() -> Path:
    return Path(os.getenv("CHROMA_PATH", ".chroma")).expanduser()

