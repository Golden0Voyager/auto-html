"""Markdown → 图片生成 → 嵌入 → HTML.

为 Markdown 文档生成配图、封面和信息图，并嵌入到最终 HTML 中.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from . import sensenova_client


class MarkdownImageGenerator:
    """为 Markdown 文档生成 AI 配图并嵌入."""

    def __init__(
        self,
        image_size: str = "2720x1536",
        output_dir: Optional[Path] = None,
        enhance_prompts: bool = False,
        use_deepseek: bool = False,
    ):
        self.image_size = image_size
        self.output_dir = output_dir
        self.enhance_prompts = enhance_prompts
        self.use_deepseek = use_deepseek

    def _size_for_type(self, image_type: str) -> str:
        """根据图片类型选择最佳尺寸."""
        sizes = {
            "cover": "2752x1536",      # 16:9 封面
            "section": "2496x1664",    # 3:2 章节配图
            "infographic": "2368x1760", # 4:3 信息图
        }
        return sizes.get(image_type, self.image_size)

    def _download(self, url: str, filename: str) -> str:
        """下载图片并返回相对路径."""
        if self.output_dir is None:
            return url  # 不下载，直接使用 URL
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        sensenova_client.download_image(url, path)
        return str(path.relative_to(self.output_dir.parent) if self.output_dir.parent else path)

    # U1 Fast 文字渲染有已知问题，所有 prompt 默认禁止文字
    _NO_TEXT_SUFFIX = "画面中不要出现任何文字或字母，使用抽象图形、图标和色彩表达主题"
    _NO_TEXT_INFO_SUFFIX = "画面中不要出现具体文字内容，用占位符色块、框架线条和抽象图标表示信息区域"

    def generate_cover(self, md_text: str, title: str = "") -> str:
        """为文档生成封面图，返回 markdown 图片引用."""
        prompt = sensenova_client.summarize_markdown_for_image(
            md_text, title or "文档封面", use_deepseek=self.use_deepseek
        )
        if self.enhance_prompts:
            prompt = sensenova_client.enhance_prompt_for_infographic(
                prompt, use_deepseek=self.use_deepseek
            )
        prompt = f"{prompt}，高质量插画风格，色彩鲜明，{self._NO_TEXT_SUFFIX}"

        urls = sensenova_client.generate_image(
            prompt=prompt,
            size=self._size_for_type("cover"),
        )
        img_path = self._download(urls[0], "cover.png")
        return f"![封面]({img_path})\n\n"

    def generate_section_image(self, section_text: str, section_title: str, index: int) -> str:
        """为章节生成配图，返回 markdown 图片引用."""
        prompt = sensenova_client.summarize_markdown_for_image(
            section_text, section_title, use_deepseek=self.use_deepseek
        )
        prompt = f"{prompt}，清新扁平插画风格，{self._NO_TEXT_SUFFIX}"

        urls = sensenova_client.generate_image(
            prompt=prompt,
            size=self._size_for_type("section"),
        )
        img_path = self._download(urls[0], f"section_{index:02d}.png")
        return f"\n![{section_title}]({img_path})\n\n"

    def generate_infographic(self, md_text: str, title: str = "") -> str:
        """将整篇文档生成为信息图，返回 markdown 图片引用."""
        # 提取核心内容作为提示词基础
        prompt_base = sensenova_client.summarize_markdown_for_image(
            md_text, title or "信息图", use_deepseek=self.use_deepseek
        )
        prompt = (
            f"信息图：{prompt_base}。"
            "要求：结构清晰，信息密度高，使用图标和抽象图形结合，"
            f"专业商务风格，配色协调，排版美观，{self._NO_TEXT_INFO_SUFFIX}"
        )
        if self.enhance_prompts:
            prompt = sensenova_client.enhance_prompt_for_infographic(
                prompt, use_deepseek=self.use_deepseek
            )

        urls = sensenova_client.generate_image(
            prompt=prompt,
            size=self._size_for_type("infographic"),
        )
        img_path = self._download(urls[0], "infographic.png")
        return f"![信息图]({img_path})\n\n"

    def embed_images_in_markdown(
        self,
        md_text: str,
        cover: bool = False,
        sections: bool = False,
        infographic: bool = False,
    ) -> str:
        """在 markdown 中嵌入生成的图片.

        Args:
            md_text: 原始 markdown 文本
            cover: 是否生成封面
            sections: 是否为每个 h2 章节生成配图
            infographic: 是否生成信息图

        Returns:
            嵌入图片后的 markdown 文本
        """
        result_lines: list[str] = []

        # 封面放在最前面
        if cover:
            title = ""
            first_line = md_text.splitlines()[0] if md_text else ""
            if first_line.startswith("# "):
                title = first_line[2:].strip()
            result_lines.append(self.generate_cover(md_text, title))

        # 信息图也放前面
        if infographic:
            title = ""
            first_line = md_text.splitlines()[0] if md_text else ""
            if first_line.startswith("# "):
                title = first_line[2:].strip()
            result_lines.append(self.generate_infographic(md_text, title))

        if not sections:
            result_lines.append(md_text)
            return "\n".join(result_lines)

        # 按 h2 分节，为每个章节生成配图
        lines = md_text.splitlines()
        current_section: list[str] = []
        section_title = ""
        section_index = 0
        in_code_block = False

        for line in lines:
            # 跳过代码块
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                current_section.append(line)
                continue

            if in_code_block:
                current_section.append(line)
                continue

            # 检测到 h2 标题
            if re.match(r"^##\s+", line):
                # 先输出之前章节的内容
                if current_section:
                    section_text = "\n".join(current_section)
                    result_lines.append(section_text)
                    # 为之前章节生成配图（跳过第一个空章节）
                    if section_index > 0 or section_title:
                        section_index += 1
                        img_md = self.generate_section_image(
                            section_text, section_title or f"章节 {section_index}", section_index
                        )
                        result_lines.append(img_md)

                # 开始新章节
                section_title = re.sub(r"^##\s+", "", line).strip()
                section_index += 1
                current_section = [line]
            else:
                current_section.append(line)

        # 输出最后一节
        if current_section:
            section_text = "\n".join(current_section)
            result_lines.append(section_text)
            if section_index > 0:
                section_index += 1
                img_md = self.generate_section_image(
                    section_text, section_title or f"章节 {section_index}", section_index
                )
                result_lines.append(img_md)

        return "\n".join(result_lines)
