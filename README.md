# md_to_html

> 将 Markdown 转换为精美 HTML，集成 SenseNova AI 一键生图

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 功能特性

- **Markdown → 精美 HTML** — 基于 mistune + Pygments，支持代码高亮、表格、任务列表、数学公式、脚注
- **SenseNova AI 生图** — 一键为文档生成 AI 配图（封面、章节配图、信息图）
- **文字乱码修复** — 自动在 prompt 中追加"禁止文字"指令，避免 AI 生成乱码中文
- **提示词增强** — 可选使用 deepseek-v4 生成高质量提示词，提升图片质量
- **多种输出模式** — 支持 base64 嵌入或下载到本地目录
- **实时监听** — `--watch` 模式监听文件变化自动重新生成

## 安装

```bash
# 克隆仓库
git clone https://github.com/hainingyu/auto_html.git
cd auto_html

# 创建虚拟环境并安装
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev,watch]"
```

或使用 uv：

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev,watch]"
```

## 快速开始

### 基础用法

```bash
# Markdown 转 HTML
md_to_html input.md

# 指定输出路径
md_to_html input.md -o output.html

# 生成目录
md_to_html input.md --toc

# 管道模式
cat input.md | md_to_html

# 监听文件变化
md_to_html input.md --watch
```

### AI 生图（需设置 API Key）

```bash
export SENSENOVA_API_KEY=sk-xxx

# 生成封面图
md_to_html input.md --generate-cover --download-images

# 为每个 h2 章节生成配图
md_to_html input.md --generate-sections --download-images

# 生成信息图
md_to_html input.md --generate-infographic --download-images

# 一键生成全部（封面 + 章节配图 + 信息图）
md_to_html input.md --generate-all --download-images

# 使用 deepseek-v4 增强提示词质量
md_to_html input.md --generate-all --enhance-prompts
```

## 模型配额

| 模型 | 用途 | 免费配额 |
|------|------|---------|
| `sensenova-u1-fast` | 图片生成 | 1500次/5h |
| `sensenova-6.7-flash-lite` | 内容分析 / 提示词生成 | 1500次/5h |
| `deepseek-v4-flash` | 增强提示词（可选） | 150次/5h |

## 项目结构

```
auto_html/
├── src/md_to_html/
│   ├── __init__.py          # 包入口
│   ├── cli.py               # 命令行接口
│   ├── converter.py         # Markdown → HTML 转换引擎
│   ├── styles.py            # CSS 样式
│   ├── sensenova_client.py  # SenseNova API 客户端
│   └── image_generator.py   # AI 图片生成与嵌入
├── tests/                   # 测试
├── examples/                # 示例文档
├── pyproject.toml
└── README.md
```

## 开发

```bash
# 运行测试
pytest

# 代码格式化
ruff check src/
ruff format src/
```

## License

MIT
