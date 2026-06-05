# AGENTS.md

> 面向 OpenCode 会话的工作须知。CLAUDE.md 是用户使用文档（怎么运行工具），
> 本文件是开发工作须知（怎么改、怎么测、哪些坑容易踩）。

## 环境与工具链（强制）

- 包管理：`uv pip install <pkg>` — 禁止 `pip` / `python -m pip`
- 运行 Python：`uv run python <script>.py` — 禁止裸 `python`
- 运行 CLI / 测试 / ruff：`uv run <cmd>`
- 提交由用户主动发起，不要自动 commit

## 项目结构

```
src/md_to_html/        # 核心包（src layout，pytest 通过 pythonpath=["src"] 直接找到）
  cli.py               # argparse 入口，console script = md_to_html
  __main__.py          # 支持 `python -m md_to_html`
  converter.py         # mistune MarkdownRenderer + 代码高亮 + 标题锚点 + TOC
  styles.py            # 内嵌 CSS（Catppuccin 主题 + 自定义阅读样式）
  sensenova_client.py  # SenseNova API：chat + images + 下载，含重试 Session
  image_generator.py   # Markdown → AI 配图 → 嵌入，封面/章节/信息图
tests/                 # pytest，pythonpath=["src"]，无需 install 即可跑
web/                   # 独立的 FastAPI Web UI（不在 ruff src/ 范围）
  app.py               # POST /convert，ThreadPoolExecutor(4) 跑阻塞 AI 调用
  static/              # index.html + app.js + style.css
  output/<job_id>/     # 每次任务产物（24h 惰性清理）
examples/              # 示例 md，AI 输出 PNG 在 .gitignore 内
```

- Python 3.10+（`pyproject.toml` requires-python）。代码使用 PEP 604/585 语法
  （`str | None`、`list[...]`、`tuple[...]`），不要降到 3.9 兼容写法
- ruff：`target-version=py310`、`line-length=100`、select=`E,F,W,I,N,UP,B,C4,SIM`、
  ignore `E501`
- **没有配置 mypy/pyright**，无 typecheck 步骤

## 常用命令

```bash
# 安装（开发）
uv pip install -e ".[dev]"            # 基础（converter + tests + ruff）
uv pip install -e ".[dev,watch]"      # 加 watchdog（--watch 模式）
uv pip install -e ".[dev,web]"        # 加 fastapi/uvicorn（Web UI）

# 跑测试（无需 install，pyproject 已配 pythonpath=["src"]）
uv run pytest                                 # 全部
uv run pytest tests/test_converter.py -v      # 单文件
uv run pytest tests/test_cli.py::TestCliArgs::test_help -v   # 单测

# Lint / 格式
uv run ruff check src/ tests/ web/    # README 漏了 tests/ 和 web/，改时一起扫
uv run ruff format src/ tests/ web/

# 跑 CLI（任选其一）
uv run md_to_html input.md
uv run python -m md_to_html input.md

# 跑 Web UI
uv run uvicorn web.app:app --reload --port 8000
```

## AI 集成的几个非显然坑

这些都是 README/CLAUDE.md 没强调、踩过一次才会注意的：

1. **`SENSENOVA_API_KEY` 缺失** → `sensenova_client._api_key()` 抛 `RuntimeError`。
   测试里用 `patch.dict(os.environ, {"SENSENOVA_API_KEY": "sk-test"}, clear=True)` 注入。
2. **图片尺寸白名单**：`sensenova_client.VALID_IMAGE_SIZES` 是一组固定值
   （`2048x2048`、`2752x1536`、`1536x2752` 等），传其他尺寸直接 `ValueError`。
   CLI 默认 `--image-size=2720x1536` **不在白名单里**，是错的吗？—— CLI 不会校验，
   直接打到 API 才报错。修 CLI 默认值时记得对齐。
3. **Reasoning 模型回退**：`sensenova-6.7-flash-lite` 默认开 reasoning 模式，
   可能把答案放在 `reasoning` 字段、`content` 为空。`chat_completion` 已经处理：
   先取 `content`，再 fallback 到 `reasoning` 最后一非空行。
4. **U1 Fast 不会画文字**：`image_generator._NO_TEXT_SUFFIX` 自动追加"画面中不要
   出现任何文字"，所有提示词都受影响。如果改提示词模板，别去掉这个后缀。
5. **`--enhance-prompts` 是双开关**：同时启用 `enhance_prompts=True` 和
   `use_deepseek=True`（cli.py:96），会切到 `deepseek-v4-flash`（仅 150次/5h 配额）。
   默认 `sensenova-6.7-flash-lite` 是 1500次/5h，量大便宜。
6. **图片缓存**：生成器按文件名判定（`cover.png`、`section_NN.png`、
   `infographic.png`），文件已存在就跳过生成直接复用。删除图片等于强制重生成。

## 测试模式

- 用 `tmp_path` 隔离 fs，CLI 测试 `patch.object(sys, "argv", [...])` +
  `patch.object(sys, "stdin", StringIO(...))`
- 模拟网络：直接赋值 `sensenova_client._session = MagicMock()`，比 mock `_get_session`
  函数更稳（参考 `tests/test_sensenova_client.py` 的 `_mock_session`）
- 已覆盖：`cli`、`converter`、`sensenova_client` — **`image_generator` 和 `web/app`
  尚无测试**，改这两处要手动验证
- FastAPI 路径无测试覆盖，提交前至少本地 `uv run uvicorn web.app:app` 跑通

## 用户可见文案与 HTML 约定

- 所有用户可见字符串（CLI help、错误信息、HTML `lang`）都是中文；
  改文案时保持中文风格，与现有术语一致
- 输出 HTML 固定 `<html lang="zh-CN">`，标题默认取文件 stem，否则 `"stdin"` 或
  `"Markdown Document"`
- 标题锚点重复时用 `slug`、`slug-2`、`slug-3` 去重，TOC 用同一套算法
  （见 `converter.py:heading_id` / `extract_toc`，两份实现要同步改）
- 任务输出文件名：默认 `input.md` → 同目录 `input.html`；`-o` 覆盖；
  `--download-images` 时图目录为 `<output_stem>_images/`

## 不在仓库内但要知道

- 仓库没有 `.github/`、没有 CI、没有 pre-commit — 改完自己跑
  `uv run ruff check src/ tests/ web/ && uv run pytest`
- 提交信息中英双语 + conventional commits 格式，但 **不要主动 commit**
- CLAUDE.md 是用户文档；AGENTS.md 是开发文档，两者内容不重复：
  CLI 用法 → CLAUDE.md；架构、坑、测试模式 → 本文件
