"""Miscellaneous utility helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF


def ensure_dir(path: Path) -> None:
    """Ensure parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text to ``path``."""
    ensure_dir(path)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    ensure_dir(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def markdown_to_pdf(md_path: Path) -> Path:
    """Convert a Markdown file to a simple PDF and return the PDF path."""
    text = md_path.read_text(encoding="utf-8")
    pdf_path = md_path.with_suffix(".pdf")
    doc = fitz.open()
    page = doc.new_page()
    y = 72  # 1 inch top margin
    for line in text.splitlines():
        page.insert_text(fitz.Point(72, y), line, fontsize=12)
        y += 14
        if y > page.rect.height - 72:
            page = doc.new_page()
            y = 72
    ensure_dir(pdf_path)
    doc.save(pdf_path)
    doc.close()
    return pdf_path
