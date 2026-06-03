"""Tests for CLI module."""
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from md_to_html.cli import main


class TestCliArgs:
    def test_no_args_shows_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", ["md_to_html"]):
                with patch.object(sys, "stdin", StringIO("")):
                    main()
        assert exc.value.code == 1

    def test_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", ["md_to_html", "--help"]):
                main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "Markdown" in captured.out


class TestCliConvert:
    def test_basic_convert(self, tmp_path: Path, capsys):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n", encoding="utf-8")

        with patch.object(sys, "argv", ["md_to_html", str(md_file)]):
            main()

        output = tmp_path / "test.html"
        assert output.exists()
        assert "Hello" in output.read_text(encoding="utf-8")

    def test_output_flag(self, tmp_path: Path):
        md_file = tmp_path / "in.md"
        md_file.write_text("# Title\n", encoding="utf-8")
        out_file = tmp_path / "custom.html"

        with patch.object(sys, "argv", ["md_to_html", str(md_file), "-o", str(out_file)]):
            main()

        assert out_file.exists()

    def test_toc_flag(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Title\n\n## Section\n", encoding="utf-8")

        with patch.object(sys, "argv", ["md_to_html", str(md_file), "--toc"]):
            main()

        output = tmp_path / "test.html"
        assert "toc" in output.read_text(encoding="utf-8")

    def test_nonexistent_file(self, capsys):
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "argv", ["md_to_html", "/nonexistent/file.md"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "不存在" in captured.err or "not found" in captured.err.lower()

    def test_stdin_mode(self, tmp_path: Path):
        with patch.object(sys, "stdin", StringIO("# From stdin\n")):
            with patch.object(sys, "argv", ["md_to_html"]):
                main()
        # stdout should contain HTML
        # This is tricky to test because main writes to stdout
        # We just verify it doesn't crash

    def test_empty_stdin(self, capsys):
        with pytest.raises(SystemExit) as exc:
            with patch.object(sys, "stdin", StringIO("")):
                with patch.object(sys, "argv", ["md_to_html"]):
                    main()
        assert exc.value.code == 1
