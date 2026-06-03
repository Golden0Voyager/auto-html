from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
import mistune
from mistune import HTMLRenderer

from .styles import CSS


def _get_lexer(code: str, info: Optional[str]):
    if info:
        try:
            return get_lexer_by_name(info.strip(), stripall=True)
        except Exception:
            pass
    try:
        from pygments.lexers import guess_lexer
        return guess_lexer(code)
    except Exception:
        return TextLexer()


class MarkdownRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.headings: list[tuple[int, str, str]] = []

    def heading_id(self, text: str) -> str:
        slug = text.strip().lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug or "heading"

    def heading(self, text: str, level: int) -> str:
        head_id = self.heading_id(text)
        self.headings.append((level, text, head_id))
        anchor = f'<a class="anchor" href="#{head_id}" aria-hidden="true">#</a>'
        return f'<h{level} id="{head_id}">{text}{anchor}</h{level}>'

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        lexer = _get_lexer(code, info)
        formatter = HtmlFormatter(
            style="material",
            noclasses=True,
            wrapcode=False,
        )
        highlighted = highlight(code, lexer, formatter)
        lang = f' data-lang="{info.strip()}"' if info else ""
        return f'<div class="code-block"{lang}>{highlighted}</div>\n'


def extract_toc(md_text: str) -> list[tuple[int, str, str]]:
    headings = []
    for line in md_text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            slug = title.strip().lower()
            slug = re.sub(r"[^\w\s-]", "", slug)
            slug = re.sub(r"\s+", "-", slug)
            slug = re.sub(r"-+", "-", slug).strip("-")
            headings.append((level, title, slug or "heading"))
    return headings


def render_toc_html(headings: list[tuple[int, str, str]]) -> str:
    if not headings:
        return ""
    parts = ['<nav class="toc">', '<h2>📖 目录</h2>', "<ul>"]
    for level, title, anchor in headings:
        indent = "  " * (level - 1)
        parts.append(
            f'{indent}<li class="toc-h{level}"><a href="#{anchor}">{title}</a></li>'
        )
    parts.append("</ul></nav>")
    return "\n".join(parts)


def build_html(
    body: str,
    title: str = "",
    toc_html: str = "",
    css: str = CSS,
) -> str:
    pygments_css = HtmlFormatter(style="material").get_style_defs(".code-block .highlight")
    full_css = css + "\n" + pygments_css

    title_tag = title or "Markdown Document"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<style>
{full_css}
</style>
</head>
<body>
<article class="markdown-body">
{toc_html}
{body}
</article>
</body>
</html>"""


def convert(md_text: str, title: str = "", with_toc: bool = False) -> str:
    renderer = MarkdownRenderer()
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=[
            "table",
            "strikethrough",
            "task_lists",
            "math",
            "footnotes",
        ],
    )
    body = md(md_text)

    toc_html = ""
    if with_toc:
        headings = renderer.headings or extract_toc(md_text)
        toc_html = render_toc_html(headings)

    return build_html(body, title=title, toc_html=toc_html)


def convert_file(
    input_path: Path,
    output_path: Optional[Path] = None,
    title: str = "",
    with_toc: bool = False,
) -> Path:
    md_text = input_path.read_text(encoding="utf-8")
    html = convert(md_text, title=title, with_toc=with_toc)

    if output_path is None:
        output_path = input_path.with_suffix(".html")

    output_path.write_text(html, encoding="utf-8")
    return output_path
