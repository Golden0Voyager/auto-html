from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert, convert_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 Markdown 转换为精美的 HTML 文档，支持 SenseNova AI 生图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "基础用法:\n"
            "  md_to_html input.md                       输出 input.html\n"
            "  md_to_html input.md -o output.html        指定输出路径\n"
            "  md_to_html input.md --toc                 生成目录\n\n"
            "AI 生图用法 (需设置 SENSENOVA_API_KEY):\n"
            "  md_to_html input.md --generate-cover      生成封面图\n"
            "  md_to_html input.md --generate-sections   为每个 h2 章节生成配图\n"
            "  md_to_html input.md --generate-infographic 生成信息图\n"
            "  md_to_html input.md --generate-all        封面+章节配图+信息图\n"
            "  md_to_html input.md --enhance-prompts     用 deepseek-v4 增强提示词\n"
        ),
    )
    parser.add_argument("input", nargs="?", type=Path, default=None,
                        help="输入的 Markdown 文件路径（省略则从 stdin 读取）")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="输出的 HTML 文件路径")
    parser.add_argument("--title", type=str, default="",
                        help="文档标题（默认取文件名）")
    parser.add_argument("--toc", action="store_true",
                        help="生成目录（Table of Contents）")
    parser.add_argument("--watch", action="store_true",
                        help="监听文件变化自动重新生成")

    # AI 生图参数
    parser.add_argument("--generate-cover", action="store_true",
                        help="为文档生成 AI 封面图")
    parser.add_argument("--generate-sections", action="store_true",
                        help="为每个 h2 章节生成 AI 配图")
    parser.add_argument("--generate-infographic", action="store_true",
                        help="将文档内容生成为信息图")
    parser.add_argument("--generate-all", action="store_true",
                        help="一键生成封面+章节配图+信息图")
    parser.add_argument("--image-size", type=str, default="2720x1536",
                        help="图片尺寸 (默认: 2720x1536, 可选: 2048x2048, 1536x2720 等)")
    parser.add_argument("--enhance-prompts", action="store_true",
                        help="用 deepseek-v4-flash 增强提示词（消耗 deepseek 配额，纯文本无 reasoning，质量更高）")
    parser.add_argument("--download-images", action="store_true",
                        help="将生成的图片下载到本地（默认使用远程 URL）")

    args = parser.parse_args()

    # 处理 generate-all
    if args.generate_all:
        args.generate_cover = True
        args.generate_sections = True
        args.generate_infographic = True

    use_ai = args.generate_cover or args.generate_sections or args.generate_infographic

    # 读取输入
    if args.input is not None:
        if not args.input.exists():
            print(f"错误: 文件不存在: {args.input}", file=sys.stderr)
            sys.exit(1)
        md_text = args.input.read_text(encoding="utf-8")
        title = args.title or args.input.stem
    else:
        md_text = sys.stdin.read()
        if not md_text.strip():
            print("错误: stdin 为空", file=sys.stderr)
            sys.exit(1)
        title = args.title or "stdin"

    # AI 生图处理
    if use_ai:
        try:
            from .image_generator import MarkdownImageGenerator
        except ImportError as e:
            print(f"错误: 缺少依赖: {e}", file=sys.stderr)
            sys.exit(1)

        output_dir: Path | None = None
        if args.download_images and args.output:
            output_dir = args.output.parent / (args.output.stem + "_images")
        elif args.download_images and args.input:
            output_dir = args.input.parent / (args.input.stem + "_images")

        generator = MarkdownImageGenerator(
            image_size=args.image_size,
            output_dir=output_dir,
            enhance_prompts=args.enhance_prompts,
            use_deepseek=args.enhance_prompts,
        )

        print("🎨 正在生成图片，请稍候...")
        md_text = generator.embed_images_in_markdown(
            md_text,
            cover=args.generate_cover,
            sections=args.generate_sections,
            infographic=args.generate_infographic,
        )
        print("✅ 图片生成完成")

    # 转换为 HTML
    html = convert(md_text, title=title, with_toc=args.toc)

    if args.output:
        args.output.write_text(html, encoding="utf-8")
        print(f"✅ 已生成: {args.output}")
    elif args.input:
        output_path = args.input.with_suffix(".html")
        output_path.write_text(html, encoding="utf-8")
        print(f"✅ 已生成: {output_path}")
    else:
        sys.stdout.write(html)

    if args.watch and args.input:
        _watch(args.input, args.output, title=title, with_toc=args.toc)


def _watch(input_path: Path, output_path: Path | None, title: str, with_toc: bool) -> None:
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path == str(input_path.resolve()):
                convert_file(input_path, output_path, title=title, with_toc=with_toc)
                print(f"🔄 已更新: {output_path or input_path.with_suffix('.html')}")

    observer = Observer()
    observer.schedule(Handler(), path=str(input_path.parent))
    observer.start()
    print(f"👀 正在监听 {input_path} ...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
