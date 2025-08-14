"""LLM client for DashScope/通义千问.

This module wraps the DashScope SDK to provide a simple chat interface with
retry and rate limiting. All text understanding and generation tasks in this
project rely on this client so that we do not use any local heuristics or
regular expressions for semantic work.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import time
from typing import Dict, List, Optional

import dashscope


def _hash_messages(messages: List[Dict[str, str]]) -> str:
    """Return a short hash of messages for logging/manifest."""
    m = hashlib.sha256()
    for msg in messages:
        m.update(json.dumps(msg, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return m.hexdigest()[:10]


@dataclass
class LLMClient:
    """Simple wrapper around DashScope's ChatCompletion API."""

    model: Optional[str] = None
    api_key: Optional[str] = None
    max_retries: int = 3
    temperature: float = 0.2
    max_tokens: int = 4000

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if self.model is None:
            self.model = os.getenv("QWEN_MODEL", "qwen-plus")
        dashscope.api_key = self.api_key

    def chat(self, messages: List[Dict[str, str]], *,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None) -> str:
        """Send chat messages to the model and return the response text."""
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        attempt = 0
        while True:
            try:
                response = dashscope.Generation.call(
                    model=self.model,
                    input={"messages": messages},
                    parameters={"temperature": temperature, "max_tokens": max_tokens},
                )
                return response['output']['text']
            except Exception as exc:  # pragma: no cover - network errors
                attempt += 1
                if attempt >= self.max_retries:
                    raise
                time.sleep(2 ** attempt)

    def chat_json(self, messages: List[Dict[str, str]], *,
                  temperature: Optional[float] = None,
                  max_tokens: Optional[int] = None) -> Dict:
        """Call :py:meth:`chat` and parse the result as JSON."""
        text = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            # Surface the raw text to help debugging.
            raise ValueError(f"LLM output is not valid JSON: {text}") from exc
