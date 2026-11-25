"""Finds the pages of a document that best match a question (BM25 keyword ranking)."""
import math
import re
import unicodedata
from collections import Counter

STOPWORDS = set("""
a an and are as at be by can de des do does du en est et for from how i il in is it
la le les of on or ou par pour que qui quoi quel quelle sur the this to un une was what
when where which who why with dans ce cette au aux se sa son ses ne pas plus
""".split())

K1, B = 1.5, 0.75
SNIPPET_CHARS = 300
CONTEXT_CHARS = 2500  # text per page sent to the AI


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in STOPWORDS]


def _snippet(text: str, terms: set[str]) -> str:
    """Return a short extract around the first matching word."""
    clean = " ".join(text.split())
    lower = clean.lower()
    pos = min((lower.find(t) for t in terms if lower.find(t) >= 0), default=0)
    start = max(0, pos - SNIPPET_CHARS // 3)
    extract = clean[start:start + SNIPPET_CHARS]
    return ("…" if start else "") + extract + ("…" if start + SNIPPET_CHARS < len(clean) else "")


def search_pages(pages: list[dict], query: str, top_k: int = 4) -> list[dict]:
    terms = tokenize(query)
    if not terms:
        return []

    docs = [Counter(tokenize(p["text"])) for p in pages]
    n = len(docs)
    avg_len = sum(sum(d.values()) for d in docs) / max(n, 1) or 1

    scores = []
    for page, tf in zip(pages, docs):
        length = sum(tf.values())
        score = 0.0
        for t in set(terms):
            df = sum(1 for d in docs if t in d)
            if not tf[t]:
                continue
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            score += idf * tf[t] * (K1 + 1) / (tf[t] + K1 * (1 - B + B * length / avg_len))
        if score > 0:
            scores.append((score, page))

    scores.sort(key=lambda s: s[0], reverse=True)
    return [
        {
            "page_index": p["page_index"],
            "label": p["label"],
            "score": round(s, 3),
            "snippet": _snippet(p["text"], set(terms)),
            "text": " ".join(p["text"].split())[:CONTEXT_CHARS],
        }
        for s, p in scores[:top_k]
    ]
