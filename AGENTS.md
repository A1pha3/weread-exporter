# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-11 16:44:31
**Commit:** 34279ead (refactor: 优化异常处理并补充项目文档)
**Branch:** main

## OVERVIEW

Python CLI工具，用于将微信读书书籍导出为EPUB/PDF/MOBI/TXT/Markdown格式。使用Canvas Hook + pyppeteer进行内容提取。

## STRUCTURE

```
./
├── weread_exporter/     # 核心包 (CLI, Export, Browser, Utils)
├── scripts/             # 构建和实用脚本
├── tests/              # 测试套件
├── docs/                # 文档
├── cache/               # 运行时缓存 (cookie, 书籍数据)
├── output/              # 生成的文件
├── pyproject.toml       # PEP 517 构建配置
├── setup.py             # 传统 setuptools
├── requirements.txt     # 运行时依赖
└── CLAUDE.md           # Claude Code 指导
```

## WHERE TO LOOK

| 任务 | 位置 | 备注 |
|------|------|------|
| CLI 入口 | `weread_exporter/__main__.py` | argparse, async_main 循环 |
| 导出工作流 | `weread_exporter/export.py` | WeReadExporter, 格式转换 |
| 浏览器自动化 | `weread_exporter/webpage.py` | WeReadWebPage, pyppeteer, Canvas Hook |
| 工具函数 | `weread_exporter/utils.py` | HTTP请求, 书单, 哈希 |
| Canvas Hook 注入 | `weread_exporter/hook.js` | JavaScript 内容拦截 |
| 构建脚本 | `scripts/` | build.py, install.py, update_deps.py |
| 测试 | `tests/` | pytest, 最小覆盖 |

## CONVENTIONS

- **异步优先**: 所有I/O使用 `async`/`await` 和 `aiohttp`
- **错误处理**: 自定义异常在 `utils.py` (ChromeNotInstalledError, LoginRequiredError, LoadChapterFailedError, InvalidUserError)
- **日志**: `logging.root.level = logging.INFO`, 格式 `[%(asctime)s][%(levelname)s]%(message)s`
- **自定义异常**: 定义在 `utils.py`, 按需导入
- **平台二进制**: `weread_exporter/bin/{linux,win32}/kindlegen` 用于MOBI

## ANTI-PATTERNS (本项目)

- `webpage.py:678` - 已注释的 `clear_cache()` 未使用
- 混合同步/异步在测试设置中 (`scripts/update_deps.py`)
- 一些硬编码值 (超时, 图片格式)

## UNIQUE STYLES

- **Windows PATH 补丁** 在 `__main__.py:8-12` 用于DLL发现
- **Chrome 反检测** 通过 `page.evaluateOnNewDocument()` 注入 (webdriver, plugins, languages 伪装)
- **请求拦截** 用于模拟API响应和注入Canvas Hook
- **缓存层级**: `cache/<book-id>/{meta.json, chapters/, images/, cover.jpg}`

## COMMANDS

```bash
# 开发
pip install -e .                    # 开发模式安装
pip install -e ".[dev]"            # 带测试/开发依赖
python -m pytest tests/             # 运行测试
python -m pytest --cov weread_exporter  # 带覆盖率

# CLI 使用
weread-exporter -b <book-id> -o epub -o pdf
weread-exporter -b <booklist-id> --list-ids
weread-exporter --list-booklists

# 构建
python build.py                     # PyInstaller 打包
python setup.py sdist bdist_wheel  # PyPI 包分发
```

## NOTES

- **需要Chrome** 在PATH中, 自动检测 macOS/Linux/Windows
- **MOBI仅支持Linux** (kindlegen 二进制)
- **Windows PNG** vs **Linux/JPG** 用于PDF图片
- Cookie认证通过 `cache/cookie.txt` (JSON格式)
- 书单ID包含 `_` 分隔符 (例如 `12345_67890`)
