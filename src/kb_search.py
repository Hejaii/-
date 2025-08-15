from __future__ import annotations

"""Knowledge base scanning and LLM-based ranking."""

from pathlib import Path
from typing import Dict, List, Tuple

from llm_client import LLMClient as Client
from .caching import LLMCache, llm_json
from .requirements_parser import RequirementItem


def scan_kb(kb_dir: Path) -> List[Path]:
    """Return all files under ``kb_dir``."""
    return [p for p in kb_dir.rglob('*') if p.is_file()]


def rank_files(requirement: RequirementItem, files: List[Path], *, topk: int, client: Client, cache: LLMCache, use_llm: bool = True) -> List[Tuple[Path, float]]:
    """Score and rank files for a requirement."""
    scores: List[Tuple[Path, float]] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        snippet = text[:800]
        if use_llm:
            system = (
                "Given a requirement and a file snippet, score the relevance between 0 and 1 "
                "and return JSON {\"score\": float}."
            )
            user = (
                f"Requirement: {requirement.title}\nKeywords: {', '.join(requirement.keywords)}\n"
                f"File: {path.name}\nSnippet:\n{snippet}"
            )
            data = llm_json(client, system, user, cache)
            score = float(data.get("score", 0.0))
        else:
            lower = (path.name + snippet).lower()
            score = sum(1 for kw in requirement.keywords if kw.lower() in lower)
        scores.append((path, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:topk]
