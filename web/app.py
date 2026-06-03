"""Web UI for md_to_html with AI image generation."""
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from md_to_html.converter import convert as md_convert
from md_to_html.image_generator import MarkdownImageGenerator

app = FastAPI(title="md_to_html Web")

WEB_DIR = Path(__file__).parent
OUTPUT_DIR = WEB_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")


@app.get("/")
async def root():
    return FileResponse(WEB_DIR / "static" / "index.html")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload a markdown file."""
    content = await file.read()
    return {"filename": file.filename, "content": content.decode("utf-8")}


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
    job_id = str(uuid.uuid4())[:8]
    job_dir = OUTPUT_DIR / job_id
    images_dir = job_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    use_ai = generate_cover or generate_sections or generate_infographic

    if use_ai:
        try:
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
        except Exception as e:
            return {"error": str(e), "job_id": job_id}

    html = md_convert(md_text, with_toc=True)

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
