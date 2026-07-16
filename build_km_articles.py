#!/usr/bin/env python3
"""Build rendered KM article pages from Markdown sources."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent
TABULAR_MD = ROOT / "km.md"
AGENT_MD = Path(__file__).resolve().parents[1] / "02-Agent自动调优/素材/Agent调优方法与思想.md"

TABULAR_IMAGE_NAMES = [
    "image.png",
    "image-1.png",
    "image-2.png",
    "image-3.png",
    "image-4.png",
    "image-5.png",
    "image-6.png",
    "image-7.png",
    "image-8.png",
    "image-9.png",
    "image-10.png",
    "image-11.png",
]

AGENT_IMAGE_MAP = {
    "assets/images/textgrad_analogy.png": "assets/km-agent-textgrad/textgrad-analogy.svg",
    "assets/images/05_project_closed_loop.png": "assets/km-agent-textgrad/project-closed-loop.png",
    "assets/images/02_textgrad_optimization_loop.png": "assets/km-agent-textgrad/textgrad-optimization-loop.svg",
    "assets/images/03_attribution_decision_tree.png": "assets/km-agent-textgrad/attribution-decision-tree.svg",
    "assets/images/01_agent_architecture.png": "assets/km-agent-textgrad/agent-architecture.svg",
    "assets/images/04_evolution_timeline.png": "assets/km-agent-textgrad/evolution-timeline.svg",
}

HTML_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} · 侯奇瑞</title>
  <meta name="description" content="{description}" />
  <link rel="stylesheet" href="style.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css" crossorigin="anonymous" />
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js" crossorigin="anonymous"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function () {{
      if (!window.renderMathInElement) return;
      window.renderMathInElement(document.body, {{
        delimiters: [
          {{ left: "$$", right: "$$", display: true }},
          {{ left: "$", right: "$", display: false }}
        ],
        throwOnError: false
      }});
    }});
  </script>
</head>
<body>
  <nav class="nav project-nav">
    <a href="index.html" class="logo">Qirui Hou.</a>
    <ul>
      <li><a href="index.html#research">返回研究成果</a></li>
      <li><a href="index.html#projects">全部项目</a></li>
    </ul>
    <button id="themeToggle" aria-label="切换主题">🌙</button>
  </nav>
  <main class="project-library single-project">
    <article class="project-report article-report">
      <header class="report-header">
        <p class="report-kicker">{kicker}</p>
        <h1>{heading}</h1>
        <p class="report-summary">{summary}</p>
      </header>
{body}
    </article>
  </main>
  <footer><p>© 2026 侯奇瑞 · {footer_note}</p></footer>
  <script src="script.js"></script>
</body>
</html>
"""


def _preprocess_math(source: str) -> str:
    def display_math(match: re.Match[str]) -> str:
        body = match.group(1).strip()
        return f'\n\n<div class="math-display">$$\n{body}\n$$</div>\n\n'

    return re.sub(r"\$\$(.+?)\$\$", display_math, source, flags=re.S)


def _render_markdown(source: str) -> str:
    source = _preprocess_math(source)
    return markdown.markdown(
        source,
        extensions=["extra", "sane_lists", "tables", "fenced_code"],
    )


def _format_figure_caption(caption: str) -> str:
    caption = caption.strip()
    return re.sub(r"^(图\d+)(?!\s*·)", r"\1 · ", caption)


def _slugify_heading(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "", text).strip().lower()
    text = re.sub(r"\s+", "-", text)
    return text or "section"


def _add_heading_ids(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        level, attrs, content = match.group(1), match.group(2), match.group(3)
        if 'id="' in attrs:
            return match.group(0)
        heading_id = _slugify_heading(content)
        return f'<h{level}{attrs} id="{heading_id}">{content}</h{level}>'

    return re.sub(r"<h([1-6])([^>]*)>(.*?)</h\1>", repl, html, flags=re.S)


def _rewrite_agent_images(html: str) -> str:
    for old, new in AGENT_IMAGE_MAP.items():
        html = html.replace(old, new)
    return html


def _rewrite_tabular_images(html: str) -> str:
    for name in TABULAR_IMAGE_NAMES:
        html = html.replace(name, f"assets/km-tabular/{name}")
    return html


def _demote_all_headings(source: str) -> str:
    return re.sub(
        r"^(#{1,5})\s",
        lambda match: f"{'#' * (len(match.group(1)) + 1)} ",
        source,
        flags=re.M,
    )


def _drop_leading_title_heading(source: str) -> str:
    return re.sub(r"^#\s+.+\n+", "", source, count=1, flags=re.M)


def _extract_inline_images(html: str) -> str:
    pattern = re.compile(r"<p>([^<]*<img[^>]+>[^<]*)</p>", flags=re.S)

    def repl(match: re.Match[str]) -> str:
        inner = match.group(1)
        img_match = re.search(r"<img[^>]+>", inner)
        if not img_match:
            return match.group(0)
        img = img_match.group(0)
        text = (inner[: img_match.start()] + inner[img_match.end() :]).strip()
        if text:
            return f'<p>{text}</p><figure class="article-figure">{img}</figure>'
        return f'<figure class="article-figure">{img}</figure>'

    return pattern.sub(repl, html)


def _finalize_figures(html: str) -> str:
    html = re.sub(r'<figure class="article-figure">\s*</figure>', "", html)

    split_figure = re.compile(
        r'<figure class="article-figure"><figcaption>(.*?)</figcaption></figure>\s*'
        r'(?:<p>.*?</p>\s*){0,2}'
        r'<figure class="article-figure"><img([^>]+)></figure>',
        flags=re.S,
    )

    def merge(match: re.Match[str]) -> str:
        caption = _format_figure_caption(match.group(1).strip())
        img_attrs = match.group(2).strip()
        if 'loading=' not in img_attrs:
            img_attrs += ' loading="lazy"'
        return (
            f'<figure class="article-figure">'
            f"<img {img_attrs} />"
            f"<figcaption>{caption}</figcaption>"
            f"</figure>"
        )

    html = split_figure.sub(merge, html)

    caption_paragraph = re.compile(
        r'<p><strong>(图\d+[^<]*)</strong>([^<]*)</p>\s*'
        r'<figure class="article-figure"><img([^>]+)></figure>',
        flags=re.S,
    )

    def merge_caption(match: re.Match[str]) -> str:
        caption = _format_figure_caption(
            f"{match.group(1).strip()}{match.group(2).strip()}"
        )
        img_attrs = match.group(3).strip()
        if 'loading=' not in img_attrs:
            img_attrs += ' loading="lazy"'
        return (
            f'<figure class="article-figure">'
            f"<img {img_attrs} />"
            f"<figcaption>{caption}</figcaption>"
            f"</figure>"
        )

    return caption_paragraph.sub(merge_caption, html)


def _enhance_figures(html: str) -> str:
    pattern = re.compile(
        r'(?:<p><strong>(图\d+[^<]*)</strong>([^<]*)</p>\s*)?'
        r'<p><img alt="([^"]*)" src="([^"]+)"(?:\s*/)?></p>',
        flags=re.S,
    )

    def repl(match: re.Match[str]) -> str:
        caption_head = (match.group(1) or "").strip()
        caption_tail = (match.group(2) or "").strip()
        alt = match.group(3).strip() or "配图"
        src = match.group(4)
        caption_text = f"{caption_head}{caption_tail}".strip()
        if caption_text:
            caption = _format_figure_caption(caption_text)
        elif alt and alt != "alt text":
            caption = f"<strong>配图</strong> {alt}"
        else:
            caption = ""
        if not caption:
            return (
                f'<figure class="article-figure">'
                f'<img src="{src}" alt="{alt}" loading="lazy" />'
                f"</figure>"
            )
        return (
            f'<figure class="article-figure">'
            f'<img src="{src}" alt="{alt}" loading="lazy" />'
            f"<figcaption>{caption}</figcaption>"
            f"</figure>"
        )

    html = pattern.sub(repl, html)

    caption_then_figure = re.compile(
        r'<p><strong>(图\d+[^<]*)</strong>(?:[^<]|<(?!/p>))*</p>\s*'
        r'<figure class="article-figure"><img alt="([^"]*)" src="([^"]+)"[^>]*></figure>',
        flags=re.S,
    )

    def merge_caption(match: re.Match[str]) -> str:
        caption = match.group(1)
        alt = match.group(2)
        src = match.group(3)
        return (
            f'<figure class="article-figure">'
            f'<img src="{src}" alt="{alt}" loading="lazy" />'
            f"<figcaption>{caption}</figcaption>"
            f"</figure>"
        )

    return caption_then_figure.sub(merge_caption, html)


def _enhance_blockquotes(html: str) -> str:
    return html.replace("<blockquote>", '<blockquote class="article-quote">')


def _postprocess_html(html: str) -> str:
    html = _enhance_blockquotes(_enhance_figures(_add_heading_ids(html)))
    html = _extract_inline_images(html)
    return _finalize_figures(html)


def _prepare_tabular_assets() -> None:
    target_dir = ROOT / "assets/km-tabular"
    target_dir.mkdir(parents=True, exist_ok=True)
    for name in TABULAR_IMAGE_NAMES:
        source = ROOT / name
        destination = target_dir / name
        if source.exists():
            shutil.copy2(source, destination)


def _prepare_agent_assets() -> None:
    target_dir = ROOT / "assets/km-agent-textgrad"
    target_dir.mkdir(parents=True, exist_ok=True)

    closed_loop_source = (
        Path(__file__).resolve().parents[1] / "02-Agent自动调优/05_project_closed_loop.png"
    )
    closed_loop_target = target_dir / "project-closed-loop.png"
    if closed_loop_source.exists():
        shutil.copy2(closed_loop_source, closed_loop_target)

    svg_sources = {
        "textgrad-analogy.svg": ROOT / "assets/km-agent-textgrad/textgrad-analogy.svg",
        "textgrad-optimization-loop.svg": ROOT / "assets/km-agent-textgrad/textgrad-optimization-loop.svg",
        "attribution-decision-tree.svg": ROOT / "assets/km-agent-textgrad/attribution-decision-tree.svg",
        "agent-architecture.svg": ROOT / "assets/km-agent-textgrad/agent-architecture.svg",
        "evolution-timeline.svg": ROOT / "assets/km-agent-textgrad/evolution-timeline.svg",
    }
    for name, path in svg_sources.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing agent illustration: {path}")


def build_tabular_page() -> None:
    _prepare_tabular_assets()
    source = TABULAR_MD.read_text(encoding="utf-8")
    source = re.sub(r"^!\[[^\]]*\]\(image\.png\)\s*", "", source)
    source = _demote_all_headings(source)
    body = _postprocess_html(_rewrite_tabular_images(_render_markdown(source)))
    html = HTML_SHELL.format(
        title="LLM 在表格数据预测中的最新进展调研",
        description="系统梳理 TabPFN、TabLLM、InsightTab、FeatLLM 等表格预测路线，并总结端到端优化框架。",
        kicker="腾讯 KM · 技术好文",
        heading="LLM 在表格数据预测中的最新进展调研",
        summary="从 XGBoost 统治的数值范式，到 LLM 引入语义推理后的四条研究路径：通用基础模型、模型微调、LLM × 传统 ML 协作，以及端到端预测优化。",
        body=body,
        footer_note="KM 技术好文网页版",
    )
    (ROOT / "km-tabular-prediction.html").write_text(html, encoding="utf-8")


def build_agent_page() -> None:
    _prepare_agent_assets()
    source = AGENT_MD.read_text(encoding="utf-8")
    source = _drop_leading_title_heading(source)
    body = _postprocess_html(_rewrite_agent_images(_render_markdown(source)))
    html = HTML_SHELL.format(
        title="从手工试错到可回滚闭环：RAG Agent 的 TextGrad 式调优实践",
        description="基于 TextGrad 范式的 RAG Agent 调优方法论与分付规则解释助手实战。",
        kicker="腾讯 KM · Agent 调优",
        heading="借鉴 TextGrad 思想的 RAG Agent 调优方法与实战",
        summary="从为什么要调优、会遇到什么问题，到 TextGrad 六步闭环、Prompt/KB 归因决策树与人工闸门，最后用分付规则解释助手完整走一遍落地过程。",
        body=body,
        footer_note="KM 技术分享网页版",
    )
    (ROOT / "km-agent-textgrad.html").write_text(html, encoding="utf-8")


def main() -> None:
    build_tabular_page()
    build_agent_page()
    print("Built km-tabular-prediction.html and km-agent-textgrad.html")


if __name__ == "__main__":
    main()
