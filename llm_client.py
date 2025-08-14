"""LLM client for DashScope/通义千问.

This module wraps the DashScope SDK to provide a simple chat interface with
retry and rate limiting. All text understanding and generation tasks in this
project rely on this client so that we do not use any local heuristics or
regular expressions for semantic work.
"""
from __future__ import annotations

from dataclasses import dataclass, field
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
    """Simple wrapper around DashScope's ChatCompletion API.

    The client cycles through a predefined list of models. After every two
    requests it waits one second. If the API returns a 400 status code the
    client automatically switches to the next model in the list.
    """

    models: Optional[List[str]] = None
    api_key: Optional[str] = None
    max_retries: int = 3
    temperature: float = 0.2
    max_tokens: int = 4000
    _model_index: int = field(init=False, default=0)
    _request_counter: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if self.models is None:
            self.models = [
                "qwen-plus-2025-07-14",
                "qwen-plus-2025-04-28",
                "qwen-plus-2025-01-25",
                "qwen-plus-1125",
                "qwen-plus-1127",
                "qwen-plus-1220",
                "qwen-plus-0112",
                "qwen-plus-0919",
                "qwen-plus-0723",
                "qwen-plus-0806",
            ]
        dashscope.api_key = self.api_key

    @property
    def model(self) -> str:
        return self.models[self._model_index]

    def _rotate_model(self) -> None:
        self._model_index += 1
        if self._model_index >= len(self.models):
            raise RuntimeError("All available models have been exhausted")

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
                self._request_counter += 1
                if self._request_counter % 2 == 0:
                    time.sleep(1)

                if response.status_code == 200:
                    return response.output.text
                elif response.status_code == 400:
                    self._rotate_model()
                    continue
                else:
                    raise RuntimeError(
                        f"Model call failed with status {response.status_code}: {response.message}"
                    )
            except Exception:
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
