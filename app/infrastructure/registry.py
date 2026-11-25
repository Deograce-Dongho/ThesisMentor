"""Stores the page index of each uploaded PDF as a JSON file (no database needed)."""
import json
import os
import re

DATA_DIR = os.path.join("app", "data")
_DOC_ID = re.compile(r"^[0-9a-f]{32}$")  # uuid4().hex


def _path(doc_id: str) -> str:
    if not _DOC_ID.match(doc_id):
        raise ValueError("Invalid doc_id")
    return os.path.join(DATA_DIR, f"{doc_id}.json")


def save_index(doc_id: str, pages: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_path(doc_id), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False)


def load_index(doc_id: str) -> list[dict] | None:
    """Return the pages of a document, or None if it is unknown."""
    try:
        with open(_path(doc_id), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return None
