"""Tests for converter module."""
from pathlib import Path

from md_to_html.converter import (
    build_html,
    convert,
    convert_file,
    extract_toc,
    render_toc_html,
)


class TestExtractToc:
    def test_single_heading(self):
        md = "# Hello World"
        result = extract_toc(md)
        assert result == [(1, "Hello World", "hello-world")]

    def test_multiple_headings(self):
        md = "# H1\n## H2\n### H3"
        result = extract_toc(md)
        assert result == [
            (1, "H1", "h1"),
            (2, "H2", "h2"),
            (3, "H3", "h3"),
        ]

    def test_headings_with_special_chars(self):
        md = "# Hello, World!\n## C++ & Python"
        result = extract_toc(md)
        assert result == [
            (1, "Hello, World!", "hello-world"),
            (2, "C++ & Python", "c-python"),
        ]

    def test_no_headings(self):
        assert extract_toc("just plain text") == []


class TestRenderTocHtml:
    def test_empty(self):
        assert render_toc_html([]) == ""

    def test_render(self):
        headings = [(1, "Title", "title"), (2, "Sub", "sub")]
        html = render_toc_html(headings)
        assert '<nav class="toc">' in html
        assert '<a href="#title">Title</a>' in html
        assert '<a href="#sub">Sub</a>' in html


class TestBuildHtml:
    def test_basic_structure(self):
        html = build_html("<p>hello</p>", title="Test")
        assert "<!DOCTYPE html>" in html
        assert '<title>Test</title>' in html
        assert "<p>hello</p>" in html
        assert "zh-CN" in html

    def test_with_toc(self):
        toc = '<nav class="toc"><ul><li><a href="#x">X</a></li></ul></nav>'
        html = build_html("<h1 id=\"x\">X</h1>", toc_html=toc)
        assert toc in html


class TestConvert:
    def test_basic_markdown(self):
        md = "# Hello\n\nThis is **bold**."
        html = convert(md)
        assert "<h1" in html
        assert "<strong>bold</strong>" in html

    def test_code_block(self):
        md = '```python\nprint("hi")\n```'
        html = convert(md)
        assert "code-block" in html
        assert "highlight" in html

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = convert(md)
        assert "<table>" in html
        assert "<td>1</td>" in html

    def test_with_toc(self):
        md = "# Title\n\n## Section"
        html = convert(md, with_toc=True)
        assert "toc" in html
        assert '<a href="#title">Title</a>' in html

    def test_heading_anchor(self):
        md = "# My Heading"
        html = convert(md)
        assert 'id="my-heading"' in html
        assert '<a class="anchor"' in html


class TestConvertFile:
    def test_convert_file(self, tmp_path: Path):
        input_file = tmp_path / "test.md"
        input_file.write_text("# Hello\n", encoding="utf-8")

        output = convert_file(input_file)

        assert output == tmp_path / "test.html"
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "Hello" in content

    def test_convert_file_with_output(self, tmp_path: Path):
        input_file = tmp_path / "in.md"
        input_file.write_text("# Hi\n", encoding="utf-8")
        output_file = tmp_path / "out.html"

        result = convert_file(input_file, output_path=output_file)

        assert result == output_file
        assert output_file.exists()
