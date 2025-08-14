"""Generate requirement-by-requirement response files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from llm_client import LLMClient
from utils import ensure_dir, write_text

RESPONSE_PROMPT = (
    "你是一名投标响应编写专家。根据给定的单条要求、可用证据文本，"\
    "生成针对性的响应说明。使用 Markdown 并包含脚注引用。"\
    "输出字段：title, content, source_refs, missing_items。"
)


def write_response(req: Dict, evidence: Dict[str, str], llm: LLMClient,
                   out_dir: Path) -> Path:
    messages = [
        {"role": "system", "content": RESPONSE_PROMPT},
        {"role": "user", "content": json.dumps({"requirement": req, "evidence": evidence}, ensure_ascii=False)},
    ]
    result = llm.chat_json(messages)
    filename = f"要求_{req['id']}.md"
    out_path = out_dir / filename
    ensure_dir(out_path.parent)
    write_text(out_path, result.get("content", ""))
    return out_path
