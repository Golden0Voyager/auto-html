# AGENTS.md

> 面向 OpenCode 会话的工作须知。CLAUDE.md 是用户使用文档（怎么运行工具），
> 本文件是开发工作须知（怎么改、怎么测、哪些坑容易踩）。

## 环境与工具链（强制）

- 包管理：`uv pip install <pkg>` — 禁止 `pip` / `python -m pip`
- 运行 Python：`uv run python <script>.py` — 禁止裸 `python`
- 运行 CLI / 测试 / ruff：`uv run <cmd>`
- 提交由用户主动发起，不要自动 commit

## 依赖注意

- `pyproject.toml` `[tool.uv.sources]` 中 `auto-hub` 来自**同级兄弟项目** `../auto_hub`（editable）。如果缺失，`sensenova_client.chat_completion()` 会静默回退到原生 SenseNova API（无 provider chain）。
- requires-python = `>=3.12`，ruff target-version = `py312`。代码使用 PEP 604/585（`str | None`、`list[...]`）。
- ruff select = `E,F,W,I,N,UP,B,C4,SIM`，ignore `E501`，line-length=100。**无 mypy/pyright**。

## 项目结构

```
src/md_to_html/        # 核心包（src layout）
  cli.py               # argparse 入口，console_script = md_to_html
  __main__.py          # 支持 python -m md_to_html
  converter.py         # mistune HTMLRenderer + 代码高亮 + 标题锚点 + TOC
  styles.py            # 内嵌 CSS 字符串（Catppuccin 主题 + 自定义样式）
  sensenova_client.py  # SenseNova API（chat + images + 下载），含重试 Session
  image_generator.py   # Markdown → AI 配图 → 嵌入
tests/                 # pytest，pythonpath=["src"]，无需 install
web/                   # 独立 FastAPI Web UI（不在 ruff src/ 范围）
  app.py               # POST /convert，ThreadPoolExecutor(4)，MAX_MD_LENGTH=100_000
  static/              # index.html + app.js + style.css
  output/<job_id>/     # 产出 index.html + images/（24h 惰性清理）
examples/              # 示例 md，PNG 在 .gitignore 内
```

## 常用命令

```bash
uv pip install -e ".[dev]"            # 基础
uv pip install -e ".[dev,web]"        # +fastapi/uvicorn

uv run pytest tests/test_converter.py -v  # 单文件
uv run pytest tests/test_cli.py::TestCliArgs::test_help -v  # 单测
uv run pytest -k "test_name"              # 名字匹配

uv run ruff check src/ tests/ web/ && uv run ruff format src/ tests/ web/
uv run md_to_html input.md
uv run uvicorn web.app:app --reload --port 8000  # Web UI
```

## AI 集成的非显然坑

1. **`SENSENOVA_API_KEY` 缺失** → `sensenova_client._api_key()` 抛 `RuntimeError`。
   测试用 `patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}, clear=True)` 注入。
2. **图片尺寸白名单**：`sensenova_client.VALID_IMAGE_SIZES` 是固定集合。CLI 默认
   `--image-size=2720x1536` 不在白名单内，但 `image_generator._size_for_type()` 会按
   类型映射到合法尺寸（如 `2752x1536`）。直接调用 `generate_image()` 传默认值会报错。
3. **Reasoning 模型回退**：`sensenova-6.7-flash-lite` 默认开 reasoning，content 可能为空。
   `chat_completion` 已处理：先取 `content`，fallback 到 `reasoning` 末尾非空行。
4. **U1 Fast 不会画文字**：`image_generator._NO_TEXT_SUFFIX` 自动追加"画面中不要出现任何文字"。
   改提示词模板时别去掉。
5. **`--enhance-prompts` 是双开关**：同时设 `enhance_prompts=True` 和 `use_deepseek=True`
   （cli.py:95-96），切到 `deepseek-v4-flash`（150次/5h）。默认 `sensenova-6.7-flash-lite`
   是 1500次/5h。
6. **图片缓存**：按文件名判定（`cover.png`、`section_NN.png`、`infographic.png`），
   存在就跳过。删图片 = 强制重生成。

## 测试模式

- fs 隔离用 `tmp_path`；CLI 测试用 `patch.object(sys, "argv", [...])` + `StringIO`
- 模拟网络：直接赋值 `sensenova_client._session = MagicMock()`（比 mock `_get_session` 稳）
- 已覆盖：`cli`、`converter`、`sensenova_client` — **`image_generator` 和 `web/app` 无测试**，
  改这两处手动验证
- Web UI 无测试覆盖，提交前至少 `uv run uvicorn web.app:app` 跑通

## 用户可见文案与 HTML 约定

- 所有用户可见字符串（CLI help、错误信息、HTML `lang`）都是中文
- HTML 固定 `<html lang="zh-CN">`，标题默认文件 stem，否则 `"stdin"` 或 `"Markdown Document"`
- 标题锚点去重在 `converter.py` 有两份实现（`heading_id` 方法 + `extract_toc` 函数），
  逻辑需同步
- 输出路径：`input.md` → 同目录 `input.html`；`-o` 覆盖；
  `--download-images` 时图目录为 `<output_stem>_images/`

## 不在仓库内但要知道

- 无 `.github/`、CI、pre-commit — 改完跑 `uv run ruff check src/ tests/ web/ && uv run pytest`
- 提交信息中英双语 + conventional commits，但**不要主动 commit**
- `*.html` 在 `.gitignore` 中，测试产出不会入库
