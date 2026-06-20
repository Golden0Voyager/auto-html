"""Tests for cli module — covering all code paths."""
from __future__ import annotations

from unittest.mock import patch

from md_to_html.cli import main


class TestCliArgs:
    def test_no_args_reads_stdin(self, capsys):
        with patch("sys.argv", ["md_to_html"]), patch("sys.stdin.read", return_value="# Hello\n\nWorld"):
            main()
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    def test_help_flag(self):
        with patch("sys.argv", ["md_to_html", "--help"]):
            try:
                main()
            except SystemExit:
                pass

    def test_nonexistent_file(self):
        with patch("sys.argv", ["md_to_html", "/nonexistent/file.md"]):
            try:
                main()
                assert False, "Should have raised SystemExit"
            except SystemExit as e:
                assert e.code != 0


class TestCliConvert:
    def test_basic_convert(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello\n\nWorld")
        with patch("sys.argv", ["md_to_html", str(md)]):
            main()
        assert (tmp_path / "test.html").exists()

    def test_output_flag(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "custom.html"
        with patch("sys.argv", ["md_to_html", str(md), "-o", str(out)]):
            main()
        assert out.exists()

    def test_toc_flag(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\n## Section 1\n\nContent\n\n## Section 2\n\nContent2")
        with patch("sys.argv", ["md_to_html", str(md), "--toc"]):
            main()

    def test_empty_stdin(self):
        with patch("sys.argv", ["md_to_html"]), patch("sys.stdin.read", return_value=""):
            try:
                main()
                assert False, "Should have raised SystemExit"
            except SystemExit as e:
                assert e.code != 0


class TestCliAIImage:
    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/cover.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_generate_cover(self, mock_sum, mock_gen, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-cover"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/sec.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_generate_sections(self, mock_sum, mock_gen, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-sections"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/info.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_generate_infographic(self, mock_sum, mock_gen, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-infographic"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/cover.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_generate_all(self, mock_sum, mock_gen, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-all"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.download_image")
    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/cover.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_download_images_with_output(self, mock_sum, mock_gen, mock_dl, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        out = tmp_path / "out.html"
        with patch("sys.argv", ["md_to_html", str(md), "-o", str(out), "--generate-cover", "--download-images"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.download_image")
    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/cover.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_download_images_without_output(self, mock_sum, mock_gen, mock_dl, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-cover", "--download-images"]):
            main()

    @patch("md_to_html.image_generator.sensenova_client.enhance_prompt_for_infographic", return_value="enhanced")
    @patch("md_to_html.image_generator.sensenova_client.generate_image", return_value=["https://example.com/cover.png"])
    @patch("md_to_html.image_generator.sensenova_client.summarize_markdown_for_image", return_value="prompt")
    def test_enhance_prompts(self, mock_sum, mock_gen, mock_enhance, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-cover", "--enhance-prompts"]):
            main()


class TestCliWatch:
    @patch("md_to_html.cli._watch")
    def test_watch_flag(self, mock_watch, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title")
        with patch("sys.argv", ["md_to_html", str(md), "--watch"]):
            main()
        mock_watch.assert_called_once()


class TestCliImageImportError:
    @patch.dict("sys.modules", {"md_to_html.image_generator": None})
    def test_generate_cover_import_error(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nBody")
        with patch("sys.argv", ["md_to_html", str(md), "--generate-cover"]):
            try:
                main()
                assert False, "Should have raised SystemExit"
            except SystemExit as e:
                assert e.code != 0
