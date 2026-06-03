"""Tests for sensenova_client module."""
import os
from unittest.mock import Mock, patch

import pytest

from md_to_html import sensenova_client


class TestApiKey:
    def test_missing_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="SENSENOVA_API_KEY"):
                sensenova_client._api_key()

    def test_key_from_env(self):
        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            assert sensenova_client._api_key() == "sk-test"


class TestHeaders:
    def test_headers_structure(self):
        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            headers = sensenova_client._headers()
            assert headers["Authorization"] == "Bearer sk-test"
            assert headers["Content-Type"] == "application/json"


class TestChatCompletion:
    @patch("md_to_html.sensenova_client.requests.post")
    def test_success(self, mock_post):
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={
                "choices": [{"message": {"content": "hello"}}]
            }),
        )

        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            result = sensenova_client.chat_completion(
                messages=[{"role": "user", "content": "hi"}]
            )

        assert result == "hello"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == sensenova_client.DEFAULT_CHAT_MODEL

    @patch("md_to_html.sensenova_client.requests.post")
    def test_reasoning_fallback(self, mock_post):
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={
                "choices": [{"message": {"content": "", "reasoning": "thinking...\nfinal answer"}}]
            }),
        )

        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            result = sensenova_client.chat_completion([{"role": "user", "content": "hi"}])

        assert result == "final answer"

    @patch("md_to_html.sensenova_client.requests.post")
    def test_empty_response(self, mock_post):
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={
                "choices": [{"message": {"content": ""}}]
            }),
        )

        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            result = sensenova_client.chat_completion([{"role": "user", "content": "hi"}])

        assert result == ""


class TestGenerateImage:
    @patch("md_to_html.sensenova_client.requests.post")
    def test_success(self, mock_post):
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={
                "data": [{"url": "https://example.com/img.png"}]
            }),
        )

        with patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}):
            urls = sensenova_client.generate_image("a cat", size="2048x2048")

        assert urls == ["https://example.com/img.png"]
        call_args = mock_post.call_args
        assert call_args[1]["json"]["size"] == "2048x2048"
        assert call_args[1]["json"]["prompt"] == "a cat"


class TestDownloadImage:
    @patch("md_to_html.sensenova_client.requests.get")
    def test_download(self, mock_get, tmp_path):
        mock_get.return_value = Mock(
            raise_for_status=Mock(),
            content=b"fake-image-data",
        )

        output = tmp_path / "img.png"
        result = sensenova_client.download_image("https://example.com/img.png", output)

        assert result == output
        assert output.read_bytes() == b"fake-image-data"


class TestSummarizeMarkdown:
    @patch("md_to_html.sensenova_client.chat_completion")
    def test_basic(self, mock_chat):
        mock_chat.return_value = "A beautiful landscape with mountains"

        result = sensenova_client.summarize_markdown_for_image("# Hello\n\nWorld")

        assert result == "A beautiful landscape with mountains"
        call_args = mock_chat.call_args[1]
        assert call_args["model"] == sensenova_client.DEFAULT_CHAT_MODEL
        assert "Hello" in call_args["messages"][1]["content"]

    @patch("md_to_html.sensenova_client.chat_completion")
    def test_with_deepseek(self, mock_chat):
        mock_chat.return_value = "Enhanced prompt"

        result = sensenova_client.summarize_markdown_for_image(
            "content", section_title="My Section", use_deepseek=True
        )

        assert result == "Enhanced prompt"
        call_args = mock_chat.call_args[1]
        assert call_args["model"] == sensenova_client.DEFAULT_REASONING_MODEL
        assert "My Section" in call_args["messages"][1]["content"]


class TestEnhancePrompt:
    @patch("md_to_html.sensenova_client.chat_completion")
    def test_enhance(self, mock_chat):
        mock_chat.return_value = "Detailed infographic prompt"

        result = sensenova_client.enhance_prompt_for_infographic("summary")

        assert result == "Detailed infographic prompt"
        call_args = mock_chat.call_args[1]
        assert "视觉设计提示词工程师" in call_args["messages"][0]["content"]
