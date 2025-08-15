from __future__ import annotations

"""Orchestrate end-to-end build from requirements to PDF."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
import logging
import tomllib

from llm_client import LLMClient as Client
from .logging_utils import get_logger
from .caching import LLMCache
from .requirements_parser import parse_requirements
from .kb_search import scan_kb, rank_files
from .content_merge import merge_contents
from .latex_renderer import markdown_to_latex, render_main_tex


DEFAULT_TEMPLATE = Path("templates/main.tex")


def load_config() -> Dict:
    path = Path("pyproject.toml")
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return data.get("tool", {}).get("build_pdf", {})
    return {}


def build_pdf(requirements: Path, kb: Path, out: Path, *, latex_template: Path | None = None, workdir: Path | None = None, topk: int = 5, use_llm: bool = True) -> None:
    """Main pipeline to build PDF."""
    workdir = workdir or Path("build")
    workdir.mkdir(parents=True, exist_ok=True)
    logger = get_logger("build_pdf", workdir)
    cache = LLMCache(workdir / "cache")
    config = load_config()
    model = config.get("model")
    temperature = config.get("temperature")
    client = Client(models=[model] if model else None, temperature=temperature if temperature is not None else 0.2)
    import inspect
    logger.debug("LLMClient.chat signature: %s", inspect.signature(client.chat))
    logger.debug("LLMClient.chat_json signature: %s", inspect.signature(client.chat_json))

    requirements_items = parse_requirements(requirements, client=client, cache=cache, use_llm=use_llm)
    files = scan_kb(kb)
    ranked: Dict[str, List] = {}
    for item in requirements_items:
        ranked[item.id] = rank_files(item, files, topk=topk, client=client, cache=cache, use_llm=use_llm)
    merged_md, meta = merge_contents(requirements_items, ranked, client=client, cache=cache, use_llm=use_llm)
    merged_md_path = workdir / "merged.md"
    merged_md_path.write_text(merged_md, encoding="utf-8")

    latex_body = markdown_to_latex(merged_md, client=client, cache=cache, use_llm=use_llm)
    template = latex_template or DEFAULT_TEMPLATE
    tex_path = workdir / "main.tex"
    render_main_tex(latex_body, template, tex_path)

    meta_path = workdir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    compile_pdf(tex_path, out, logger)


def compile_pdf(tex_path: Path, out_pdf: Path, logger: logging.Logger) -> None:
    """Compile LaTeX into PDF using latexmk or xelatex."""
    workdir = tex_path.parent
    cmd = ["latexmk", "-xelatex", "-interaction=nonstopmode", tex_path.name]
    try:
        subprocess.run(cmd, cwd=workdir, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(cmd, cwd=workdir, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        built_pdf = workdir / (tex_path.stem + ".pdf")
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        built_pdf.rename(out_pdf)
    except FileNotFoundError:
        logger.error("latexmk not found; please install TeX distribution")
    except subprocess.CalledProcessError as exc:
        logger.error("LaTeX compilation failed: %s", exc.stdout.decode("utf-8", errors="ignore"))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build PDF from requirements and knowledge base")
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--kb", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--latex-template", type=Path, default=None)
    parser.add_argument("--workdir", type=Path, default=Path("build"))
    parser.add_argument("--topk", type=int, default=5)
    parser.add_argument("--use-llm", type=str, default="true")

    args = parser.parse_args()
    use_llm = args.use_llm.lower() == "true"
    build_pdf(args.requirements, args.kb, args.out, latex_template=args.latex_template, workdir=args.workdir, topk=args.topk, use_llm=use_llm)


if __name__ == "__main__":
    main()
