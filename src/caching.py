from __future__ import annotations

"""Simple local cache for LLM calls to avoid repeated charges."""

import hashlib
import json
from pathlib import Path
from typing import Dict, List
import logging

from llm_client import LLMClient as Client  # alias as Client per instructions


class LLMCache:
    """Disk-based cache for LLM requests."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, messages: List[Dict[str, str]]) -> str:
        m = hashlib.sha256()
        for msg in messages:
            m.update(json.dumps(msg, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        return m.hexdigest()

    def get(self, messages: List[Dict[str, str]]) -> str | None:
        key = self._key(messages)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def set(self, messages: List[Dict[str, str]], value: str) -> None:
        key = self._key(messages)
        path = self.cache_dir / f"{key}.json"
        path.write_text(value, encoding="utf-8")


def llm_json(client: Client, system: str, user: str, cache: LLMCache, *, logger: logging.Logger | None = None) -> Dict:
    """Call LLM with caching and expect a JSON response."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    if logger:
        import inspect
        logger.debug("LLMClient.chat signature: %s", inspect.signature(client.chat))
    cached = cache.get(messages)
    if cached is not None:
        return json.loads(cached)
    text = client.chat(messages)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # attempt one more repair call
        repair_user = f"The previous response was not valid JSON: {text}. Please return valid JSON only."
        text = client.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": repair_user},
        ])
        data = json.loads(text)
    cache.set(messages, json.dumps(data, ensure_ascii=False))
    return data


def llm_rewrite(client: Client, system: str, user: str, cache: LLMCache) -> str:
    """Call LLM with caching for text generation or rewriting."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    cached = cache.get(messages)
    if cached is not None:
        return cached
    text = client.chat(messages)
    cache.set(messages, text)
    return text
