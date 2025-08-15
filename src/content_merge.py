from __future__ import annotations

"""Merge selected knowledge base snippets into unified Markdown."""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from llm_client import LLMClient as Client
from .caching import LLMCache, llm_rewrite
from .requirements_parser import RequirementItem


def merge_contents(requirements: List[RequirementItem], ranked: Dict[str, List[Tuple[Path, float]]], *, client: Client, cache: LLMCache, use_llm: bool = True) -> tuple[str, Dict]:
    """Merge contents for requirements.

    Returns merged Markdown text and metadata mapping.
    """
    sections: List[str] = []
    meta: Dict[str, Dict] = {}
    for req in requirements:
        files = ranked.get(req.id, [])
        meta_item = {"title": req.title, "candidates": []}
        snippets: List[str] = []
        for path, score in files:
            meta_item["candidates"].append({"path": str(path), "score": score})
            try:
                snippets.append(path.read_text(encoding="utf-8"))
            except Exception:
                continue
        if not snippets:
            placeholder = f"未找到与需求 {req.title} 相关的内容。"
            sections.append(f"### {req.title}\n\n{placeholder}\n")
            meta_item["selected"] = None
        else:
            if use_llm:
                system = (
                    "Combine the following content pieces into a coherent Markdown section. "
                    "Remove duplicates but keep footnotes referencing original file paths."
                )
                user_parts = []
                for (path, _), snippet in zip(files, snippets):
                    user_parts.append(f"Source: {path}\n{snippet}")
                user = f"Requirement: {req.title}\n\n" + "\n\n".join(user_parts)
                merged = llm_rewrite(client, system, user, cache)
            else:
                merged = "\n\n".join(snippets)
            sections.append(f"### {req.title}\n\n{merged}\n")
            meta_item["selected"] = [str(p) for p, _ in files]
        meta[req.id] = meta_item
    merged_markdown = "\n".join(sections)
    return merged_markdown, meta
