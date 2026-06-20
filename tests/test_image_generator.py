"""Tests for image_generator module — all API calls mocked."""
from __future__ import annotations

from unittest.mock import patch

from md_to_html.image_generator import MarkdownImageGenerator


class TestSizeForType:
    def test_cover_size(self):
        gen = MarkdownImageGenerator()
        assert gen._size_for_type("cover") == "2752x1536"

    def test_section_size(self):
        gen = MarkdownImageGenerator()
        assert gen._size_for_type("section") == "2496x1664"

    def test_infographic_size(self):
        gen = MarkdownImageGenerator()
        assert gen._size_for_type("infographic") == "2368x1760"

    def test_unknown_type_uses_default(self):
        gen = MarkdownImageGenerator(image_size="1024x1024")
        assert gen._size_for_type("unknown") == "1024x1024"


class TestDownload:
    def test_no_output_dir_returns_url(self):
        gen = MarkdownImageGenerator(output_dir=None)
        result = gen._download("https://example.com/img.png", "test.png")
        assert result == "https://example.com/img.png"

    @patch("md_to_html.image_generator.sensenova_client.download_image")
    def test_with_output_dir(self, mock_download, tmp_path):
        gen = MarkdownImageGenerator(output_dir=tmp_path)
        result = gen._download("https://example.com/img.png", "test.png")
        mock_download.assert_called_once()
        assert "test.png" in result


class TestGenerateCover:
    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="test prompt")
    def test_generate_cover(self, mock_summarize, mock_generate):
        mock_generate.return_value = ["https://example.com/cover.png"]
        gen = MarkdownImageGenerator()
        result = gen.generate_cover("# Test\n\nSome text", "Test")
        assert "![封面]" in result
        mock_summarize.assert_called_once()
        mock_generate.assert_called_once()

    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.enhance_prompt_for_infographic", return_value="enhanced")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="test prompt")
    def test_generate_cover_with_enhance(self, mock_summarize, mock_enhance, mock_generate):
        mock_generate.return_value = ["https://example.com/cover.png"]
        gen = MarkdownImageGenerator(enhance_prompts=True)
        result = gen.generate_cover("# Test", "Test")
        assert "![封面]" in result
        mock_enhance.assert_called_once()

    def test_generate_cover_returns_cached(self, tmp_path):
        (tmp_path / "cover.png").touch()
        gen = MarkdownImageGenerator(output_dir=tmp_path)
        result = gen.generate_cover("# Test", "Test")
        assert "![封面]" in result

    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="p")
    def test_generate_cover_empty_title(self, mock_sum, mock_gen):
        mock_gen.return_value = ["https://example.com/cover.png"]
        gen = MarkdownImageGenerator()
        gen.generate_cover("# Test", "")
        mock_sum.assert_called_once()


class TestGenerateSectionImage:
    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="section prompt")
    def test_generate_section(self, mock_sum, mock_gen):
        mock_gen.return_value = ["https://example.com/sec.png"]
        gen = MarkdownImageGenerator()
        result = gen.generate_section_image("section text", "Section 1", 1)
        assert "![Section 1]" in result

    def test_generate_section_returns_cached(self, tmp_path):
        (tmp_path / "section_01.png").touch()
        gen = MarkdownImageGenerator(output_dir=tmp_path)
        result = gen.generate_section_image("text", "Title", 1)
        assert "![Title]" in result


class TestGenerateInfographic:
    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="info prompt")
    def test_generate_infographic(self, mock_sum, mock_gen):
        mock_gen.return_value = ["https://example.com/info.png"]
        gen = MarkdownImageGenerator()
        result = gen.generate_infographic("# Test", "Test")
        assert "![信息图]" in result

    @patch("md_to_html.image_generator.sensenova_client.generate_image")
    @patch("md_to_html.image_generator.sensenova_client.enhance_prompt_for_infographic", return_value="enhanced")
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="p")
    def test_generate_infographic_with_enhance(self, mock_sum, mock_enhance, mock_gen):
        mock_gen.return_value = ["https://example.com/info.png"]
        gen = MarkdownImageGenerator(enhance_prompts=True)
        gen.generate_infographic("# Test", "Test")
        mock_enhance.assert_called_once()

    def test_generate_infographic_returns_cached(self, tmp_path):
        (tmp_path / "infographic.png").touch()
        gen = MarkdownImageGenerator(output_dir=tmp_path)
        result = gen.generate_infographic("# Test", "Test")
        assert "![信息图]" in result


class TestEmbedImagesInMarkdown:
    @patch.object(MarkdownImageGenerator, "generate_infographic", return_value="![info](info.png)\n\n")
    @patch.object(MarkdownImageGenerator, "generate_cover", return_value="![cover](cover.png)\n\n")
    def test_embed_cover_and_infographic(self, mock_cover, mock_infographic):
        gen = MarkdownImageGenerator()
        result = gen.embed_images_in_markdown("# Title\n\nBody", cover=True, infographic=True)
        assert "![cover]" in result
        assert "![info]" in result
        assert "# Title" in result

    def test_embed_no_flags(self):
        gen = MarkdownImageGenerator()
        result = gen.embed_images_in_markdown("# Title\n\nBody")
        assert result == "# Title\n\nBody"

    @patch.object(MarkdownImageGenerator, "generate_section_image", return_value="![img](img.png)\n\n")
    @patch.object(MarkdownImageGenerator, "generate_cover", return_value="![cover](cover.png)\n\n")
    def test_embed_sections_with_h2(self, mock_cover, mock_section):
        gen = MarkdownImageGenerator()
        md = "# Title\n\n## Section 1\n\nContent 1\n\n## Section 2\n\nContent 2"
        result = gen.embed_images_in_markdown(md, cover=True, sections=True)
        assert "![cover]" in result
        assert result.count("![img]") >= 1

    @patch.object(MarkdownImageGenerator, "generate_section_image", return_value="![img](img.png)\n\n")
    def test_embed_sections_with_code_block(self, mock_section):
        gen = MarkdownImageGenerator()
        md = "## Section 1\n\n```\ncode\n```\n\n## Section 2\n\nContent"
        result = gen.embed_images_in_markdown(md, sections=True)
        assert "```" in result

    @patch.object(MarkdownImageGenerator, "generate_section_image", return_value="![img](img.png)\n\n")
    def test_embed_sections_empty_title(self, mock_section):
        gen = MarkdownImageGenerator()
        md = "# Title\n\n## \n\nContent"
        result = gen.embed_images_in_markdown(md, sections=True)
        assert "![img]" in result

    @patch.object(MarkdownImageGenerator, "generate_infographic", return_value="![info](info.png)\n\n")
    def test_embed_infographic_no_title(self, mock_infographic):
        gen = MarkdownImageGenerator()
        result = gen.embed_images_in_markdown("Body text", infographic=True)
        assert "![info]" in result

    @patch.object(MarkdownImageGenerator, "generate_section_image", return_value="![img](img.png)\n\n")
    def test_embed_sections_single_section(self, mock_section):
        gen = MarkdownImageGenerator()
        md = "## Only Section\n\nContent only"
        result = gen.embed_images_in_markdown(md, sections=True)
        assert "Content only" in result
