"""Web UI for md_to_html with AI image generation."""
import asyncio
import secrets
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from md_to_html.converter import convert as md_convert
from md_to_html.image_generator import MarkdownImageGenerator

MAX_MD_LENGTH = 100_000
OUTPUT_TTL_HOURS = 24

_executor = ThreadPoolExecutor(max_workers=4)
_last_cleanup = 0.0

app = FastAPI(title="md_to_html Web")

WEB_DIR = Path(__file__).parent
OUTPUT_DIR = WEB_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")


@app.get("/")
async def root():
    return FileResponse(WEB_DIR / "static" / "index.html")


def _convert(
    md_text: str,
    job_id: str,
    images_dir: Path,
    generate_cover: bool,
    generate_sections: bool,
    generate_infographic: bool,
    enhance_prompts: bool,
    image_size: str,
) -> dict:
    """同步转换工作（在线程池中运行，避免阻塞事件循环）."""
    use_ai = generate_cover or generate_sections or generate_infographic

    if use_ai:
        generator = MarkdownImageGenerator(
            image_size=image_size,
            output_dir=images_dir,
            enhance_prompts=enhance_prompts,
            use_deepseek=enhance_prompts,
        )
        md_text = generator.embed_images_in_markdown(
            md_text,
            cover=generate_cover,
            sections=generate_sections,
            infographic=generate_infographic,
        )

    html = md_convert(md_text, with_toc=True)

    job_dir = images_dir.parent
    html_path = job_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")

    image_files = []
    if images_dir.exists():
        image_files = [
            f"/output/{job_id}/images/{f.name}"
            for f in sorted(images_dir.glob("*.png"))
        ]

    return {
        "job_id": job_id,
        "preview_url": f"/output/{job_id}/index.html",
        "images": image_files,
    }


def _maybe_cleanup():
    """惰性清理：每隔一小时执行一次，避免启动风暴和目录遍历开销."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 3600:
        return
    _last_cleanup = now
    cutoff = now - OUTPUT_TTL_HOURS * 3600
    for entry in OUTPUT_DIR.iterdir():
        if entry.is_dir():
            try:
                mtime = entry.stat().st_mtime
                if mtime < cutoff:
                    shutil.rmtree(entry, ignore_errors=True)
            except OSError:
                pass


@app.post("/convert")
async def convert(
    md_text: str = Form(...),
    generate_cover: bool = Form(False),
    generate_sections: bool = Form(False),
    generate_infographic: bool = Form(False),
    enhance_prompts: bool = Form(False),
    image_size: str = Form("2720x1536"),
):
    """Convert markdown to HTML with optional AI images."""
    if len(md_text) > MAX_MD_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Markdown 内容过长（{len(md_text)} 字符），最大支持 {MAX_MD_LENGTH} 字符",
        )

    job_id = secrets.token_hex(8)
    job_dir = OUTPUT_DIR / job_id
    images_dir = job_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    _maybe_cleanup()

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            _executor,
            _convert,
            md_text,
            job_id,
            images_dir,
            generate_cover,
            generate_sections,
            generate_infographic,
            enhance_prompts,
            image_size,
        )
    except Exception as e:
        return {"error": str(e), "job_id": job_id}

    return result
