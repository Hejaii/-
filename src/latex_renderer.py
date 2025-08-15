from __future__ import annotations

"""Rendering utilities: Markdown → LaTeX and template filling."""

from pathlib import Path

from llm_client import LLMClient as Client
from .caching import LLMCache, llm_rewrite


def markdown_to_latex(markdown: str, *, client: Client, cache: LLMCache, use_llm: bool = True) -> str:
    """Convert Markdown text to LaTeX."""
    if use_llm:
        system = "Convert the following Markdown into LaTeX code only."
        latex = llm_rewrite(client, system, markdown, cache)
    else:
        latex = "\\begin{verbatim}\n" + markdown + "\n\\end{verbatim}\n"
    return latex


def render_main_tex(body: str, template_path: Path, output_path: Path) -> str:
    """Fill the LaTeX template with body content."""
    template = template_path.read_text(encoding="utf-8")
    tex = template.replace("%%CONTENT%%", body)
    output_path.write_text(tex, encoding="utf-8")
    return tex
