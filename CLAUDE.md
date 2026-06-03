## ⚠️ 环境约束（强制）

- **包管理器**：`uv pip install <pkg>`（禁止 `pip` / `python -m pip`）
- **运行脚本**：`uv run python <script>.py`（禁止直接 `python`）

---

# md_to_html - Markdown 转 HTML 转换器（含 SenseNova AI 生图）

## 架构
- Python CLI 工具，使用 mistune + pygments
- `converter.py`：核心转换逻辑（解析、代码高亮、HTML 生成）
- `styles.py`：CSS 样式（Catppuccin 主题代码高亮 + 自定义阅读体验）
- `sensenova_client.py`：SenseNova Token Plan API 客户端（图片生成 + 聊天）
- `image_generator.py`：Markdown → AI 配图 → 嵌入 → HTML
- `cli.py`：命令行入口

## 基础使用
```bash
uv run md_to_html input.md                  # 基本转换
uv run md_to_html input.md --toc            # 生成目录
uv run md_to_html input.md -o output.html   # 指定输出
cat input.md | uv run md_to_html            # 管道模式
uv run md_to_html input.md --watch          # 监听模式
```

## AI 生图使用（需设置 SENSENOVA_API_KEY）

```bash
export SENSENOVA_API_KEY=sk-xxx

# 生成封面图
uv run md_to_html input.md --generate-cover --download-images

# 为每个 h2 章节生成配图
uv run md_to_html input.md --generate-sections --download-images

# 生成信息图（将文档内容浓缩为一张图）
uv run md_to_html input.md --generate-infographic --download-images

# 一键生成全部（封面 + 章节配图 + 信息图）
uv run md_to_html input.md --generate-all --download-images

# 用 LLM 增强提示词质量（消耗 deepseek-v4-flash 配额）
uv run md_to_html input.md --generate-all --enhance-prompts

# 指定图片尺寸
uv run md_to_html input.md --generate-cover --image-size 2048x2048
```

## 模型配额说明

| 模型 | 用途 | 配额 |
|------|------|------|
| `sensenova-u1-fast` | 图片生成 | 1500次/5h |
| `sensenova-6.7-flash-lite` | 内容分析 / 提示词生成 | 1500次/5h |
| `deepseek-v4-flash` | 备用（纯文本，无 reasoning） | 150次/5h |

> 默认使用 `sensenova-6.7-flash-lite` 做内容分析，将 `max_tokens` 设到 4096 以绕过其 reasoning 模式对 token 的占用。全程不消耗宝贵的 deepseek 配额。

## 开发
```bash
uv venv && source .venv/bin/activate && uv pip install -e .
```
