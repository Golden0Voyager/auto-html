"""SenseNova Token Plan API 客户端.

封装图片生成和聊天补全接口，支持 OpenAI SDK 兼容调用.
"""
from __future__ import annotations

import os
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://token.sensenova.cn/v1"
DEFAULT_IMAGE_MODEL = "sensenova-u1-fast"
DEFAULT_CHAT_MODEL = "sensenova-6.7-flash-lite"
DEFAULT_REASONING_MODEL = "deepseek-v4-flash"

VALID_IMAGE_SIZES = {
    "2048x2048", "2752x1536", "1536x2752",
    "2496x1664", "1664x2496", "2368x1760",
    "1760x2368", "1824x2272", "2272x1824",
    "3072x1376", "1344x3136",
}

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        retries = Retry(total=2, backoff_factor=1, allowed_methods={"POST", "GET"})
        _session.mount("https://", HTTPAdapter(max_retries=retries))
    return _session


def _api_key() -> str:
    key = os.environ.get("SENSENOVA_API_KEY")
    if not key:
        raise RuntimeError(
            "请设置环境变量 SENSENOVA_API_KEY，值为你的 SenseNova Token Plan API Key（sk-xxx）"
        )
    return key


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }


def chat_completion(
    messages: list[dict],
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    timeout: int = 120,
) -> str:
    """调用 chat completions，返回文本内容.

    优先使用 auto_hub.llm 的 provider chain（设置 AI_PROVIDER_CHAIN 环境变量）。
    回退到原有的 SenseNova raw API 调用（仅需 SENSENOVA_API_KEY）。
    """
    try:
        from auto_hub.llm import LLMClient
        client = LLMClient.from_env()
        return client.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except (RuntimeError, ImportError):
        pass

    effective_model = model or DEFAULT_CHAT_MODEL
    resp = _get_session().post(
        f"{BASE_URL}/chat/completions",
        headers=_headers(),
        json={
            "model": effective_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    msg = data["choices"][0]["message"]
    content = msg.get("content")
    if content:
        return content
    reasoning = msg.get("reasoning", "")
    if reasoning:
        lines = reasoning.strip().splitlines()
        return lines[-1] if lines else ""
    return ""


def generate_image(
    prompt: str,
    size: str = "2720x1536",
    model: str = DEFAULT_IMAGE_MODEL,
    n: int = 1,
    timeout: int = 300,
) -> list[str]:
    """调用 images/generations，返回图片 URL 列表.

    Args:
        prompt: 图片生成提示词
        size: 尺寸字符串，如 "2720x1536"、"2048x2048" 等
        model: 图片生成模型，默认 sensenova-u1-fast
        n: 生成数量
        timeout: 超时秒数

    Returns:
        图片 URL 列表
    """
    if size not in VALID_IMAGE_SIZES:
        raise ValueError(
            f"不支持的图片尺寸 '{size}'，支持的尺寸: {', '.join(sorted(VALID_IMAGE_SIZES))}"
        )
    resp = _get_session().post(
        f"{BASE_URL}/images/generations",
        headers=_headers(),
        json={
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return [item["url"] for item in data["data"]]


def download_image(url: str, output_path: Path, timeout: int = 60) -> Path:
    """下载图片到本地."""
    resp = _get_session().get(url, timeout=timeout)
    resp.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)
    return output_path


def enhance_prompt_for_infographic(raw_prompt: str, use_deepseek: bool = False) -> str:
    """增强信息图 prompt，提升信息密度和排版质量.

    Args:
        raw_prompt: 原始提示词
        use_deepseek: 是否使用 deepseek-v4-flash（纯文本无 reasoning，质量更高）
    """
    system_msg = (
        "你是一位专业的视觉设计提示词工程师。"
        "你的任务是将用户的简短描述扩展为高质量、细节丰富的信息图生成提示词。"
        "提示词需要详细包含：主题、配色方案、排版风格、信息层级、视觉元素、布局结构。"
        "描述尽可能具体和详细，200-500字为宜。直接输出提示词，不要解释思考过程。"
    )
    user_msg = f"请为以下主题生成信息图提示词：\n\n{raw_prompt}"
    model = DEFAULT_REASONING_MODEL if use_deepseek else DEFAULT_CHAT_MODEL
    max_tokens = 4096 if use_deepseek else 16384
    enhanced = chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=0.8,
    )
    return enhanced.strip()


def summarize_markdown_for_image(
    md_text: str, section_title: str = "", use_deepseek: bool = False
) -> str:
    """将 markdown 内容总结为图片生成提示词.

    Args:
        md_text: Markdown 内容
        section_title: 章节标题
        use_deepseek: 是否使用 deepseek-v4-flash（纯文本无 reasoning，质量更高）
    """
    system_msg = (
        "你是一位视觉内容策划师。根据给定的文档内容，生成一段细节丰富、"
        "适合 AI 图片生成的高质量提示词。提示词应详细描述：画面主体、场景构图、"
        "艺术风格、色彩搭配、光影氛围、材质质感。描述尽可能具体丰富，"
        "100-300字为宜。直接输出提示词，不要解释。"
    )
    if section_title:
        user_msg = f"章节标题：{section_title}\n\n内容摘要：\n{md_text[:1500]}\n\n请生成配图提示词："
    else:
        user_msg = f"文档内容：\n{md_text[:2000]}\n\n请生成配图提示词："

    model = DEFAULT_REASONING_MODEL if use_deepseek else DEFAULT_CHAT_MODEL
    max_tokens = 4096 if use_deepseek else 16384
    return chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=0.8,
    ).strip()
