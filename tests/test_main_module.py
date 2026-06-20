"""Test __main__.py entry point."""
from __future__ import annotations

from unittest.mock import patch


def test_main_module():
    with patch("md_to_html.cli.main"):
        import md_to_html.__main__
