from __future__ import annotations

"""Parse requirement lists into a unified structure using LLM."""

import json
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from llm_client import LLMClient as Client
from doc_loader import load_document
from .caching import LLMCache, llm_json


@dataclass
class RequirementItem:
    """Standard requirement item."""

    id: str
    title: str
    keywords: List[str]
    source: str
    notes: str
    weight: float


def _from_dict(data: dict, index: int) -> RequirementItem:
    keywords = data.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]
    return RequirementItem(
        id=str(data.get("id", index + 1)),
        title=str(data.get("title", "")),
        keywords=keywords,
        source=str(data.get("source", "")),
        notes=str(data.get("notes", "")),
        weight=float(data.get("weight", 1.0)),
    )


def parse_requirements(path: Path, *, client: Client, cache: LLMCache, use_llm: bool = True) -> List[RequirementItem]:
    """Parse the requirement file into :class:`RequirementItem` objects.

    Supported formats include JSON/CSV/Markdown and PDF. PDF input relies on the
    LLM for structured extraction.
    """

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        if not use_llm:
            raise ValueError("PDF requirements need LLM parsing")
        text = load_document(path)
    else:
        text = path.read_text(encoding="utf-8")

    if use_llm:
        system = (
            "You convert requirement lists provided in JSON/CSV/Markdown/PDF into a JSON array "
            "of objects with fields id,title,keywords,source,notes,weight. keywords is a list of strings."
        )
        user = f"Input content:\n{text}\nReturn JSON array only."
        data = llm_json(client, system, user, cache)
        items_raw = data if isinstance(data, list) else data.get("items", [])
    else:
        if suffix == ".json":
            items_raw = json.loads(text)
        elif suffix == ".csv":
            reader = csv.DictReader(text.splitlines())
            items_raw = list(reader)
        else:
            lines = [line for line in text.splitlines() if line.strip()]
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            items_raw = []
            for line in lines[2:]:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                item = {headers[i]: parts[i] for i in range(min(len(headers), len(parts)))}
                items_raw.append(item)

    items = [_from_dict(d, i) for i, d in enumerate(items_raw)]
    return items
