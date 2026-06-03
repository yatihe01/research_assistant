from __future__ import annotations

import re
from typing import Any

import arxiv
import requests


SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def search_literature(summary: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    query = _query_from_summary(summary)
    papers: list[dict[str, Any]] = []
    papers.extend(_search_arxiv(query, limit=limit))
    papers.extend(_search_semantic_scholar(query, limit=limit))
    return _deduplicate(papers)[: limit * 2]


def _query_from_summary(summary: dict[str, Any]) -> str:
    title = str(summary.get("title", "")).strip()
    statement = str(summary.get("statement", "")).strip()
    text = f"{title} {statement}"
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text.lower())
    stopwords = {
        "the",
        "and",
        "how",
        "what",
        "with",
        "from",
        "that",
        "this",
        "into",
        "under",
        "paper",
        "idea",
    }
    keywords = [word for word in words if word not in stopwords]
    return " ".join(keywords[:12]) or title or statement[:80]


def _search_arxiv(query: str, limit: int) -> list[dict[str, Any]]:
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = client.results(search)
        return [
            {
                "title": result.title,
                "abstract_snippet": _snippet(result.summary),
                "url": result.entry_id,
                "year": result.published.year,
                "source": "arxiv",
            }
            for result in results
        ]
    except Exception as exc:
        return [_error_result("arxiv", exc)]


def _search_semantic_scholar(query: str, limit: int) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            SEMANTIC_SCHOLAR_URL,
            params={
                "query": query,
                "limit": limit,
                "fields": "title,abstract,url,year",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        return [
            {
                "title": paper.get("title") or "Untitled paper",
                "abstract_snippet": _snippet(paper.get("abstract") or ""),
                "url": paper.get("url") or "",
                "year": paper.get("year"),
                "source": "semantic_scholar",
            }
            for paper in data
        ]
    except Exception as exc:
        return [_error_result("semantic_scholar", exc)]


def _deduplicate(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for paper in papers:
        key = str(paper.get("url") or paper.get("title", "")).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(paper)
    return unique


def _snippet(text: str, length: int = 320) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= length:
        return cleaned
    return cleaned[: length - 3].rstrip() + "..."


def _error_result(source: str, exc: Exception) -> dict[str, Any]:
    return {
        "title": f"{source} search unavailable",
        "abstract_snippet": str(exc),
        "url": "",
        "year": None,
        "source": source,
    }

