# 开发与测试指南

> 本文档是开发路径的第三篇，面向希望为 weread-exporter 贡献代码或进行深度定制的开发者。通过阅读本文档，你将掌握完整的开发环境搭建方法，理解项目的代码规范和质量要求，学会编写和运行测试，以及了解如何进行代码审查和贡献。

## 学习目标

完成本章节学习后，你将能够搭建完整的开发环境，理解项目的代码规范和最佳实践，编写符合项目要求的测试用例，以及参与代码贡献流程。这些能力是成为项目贡献者的必备技能。

### 基础目标

首先，你将掌握开发环境的搭建步骤，包括 Python 环境配置、依赖安装、代码编辑器配置等。其次，你将理解项目的代码规范，包括 Python 风格指南、文档要求、命名约定等。第三，你将学会运行现有测试并理解测试覆盖范围。第四，你将掌握基本的调试技巧和问题定位方法。

### 进阶目标

进阶目标要求你能够设计新功能的测试方案，评估代码变更的影响范围，以及指导其他开发者参与贡献。你还将学会如何审查他人代码，提供建设性反馈，以及维护代码质量标准。

## 1.1 开发环境搭建

搭建一个高效的开发环境是贡献代码的第一步。本节将详细介绍从零开始搭建完整开发环境的过程，包括环境要求、工具选择和配置方法。

### 1.1.1 环境要求

开发 weread-exporter 需要以下基础环境：

Python 版本要求为 3.7 或更高版本，推荐使用 3.11 以获得最佳性能和兼容性。可以通过以下命令检查当前版本：

```bash
python --version
python3 --version
```

如果系统默认 Python 版本过低，建议使用 pyenv 或 conda 管理多个 Python 版本。

Git 版本控制工具是必需的，用于代码版本管理和提交 Pull Request。可以通过以下命令检查：

```bash
git --version
```

Chrome 或 Chromium 浏览器是运行时必需的，用于浏览器自动化测试。开发阶段不需要安装，但运行时需要。

### 1.1.2 环境配置步骤

以下是完整的开发环境配置步骤：

第一步，克隆项目仓库：

```bash
git clone https://github.com/drunkdream/weread-exporter.git
cd weread-exporter
```

第二步，创建 Python 虚拟环境。推荐使用 venv 创建隔离环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 验证激活
which python  # Linux/macOS
where python   # Windows
```

第三步，安装依赖包：

```bash
# 安装项目本身（可编辑模式）
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"

# 或者分别安装
pip install pytest pytest-cov
pip install black flake8 mypy
```

第四步，验证安装：

```bash
# 检查 weread-exporter 是否可用
weread-exporter --help

# 检查测试是否可用
pytest --version

# 检查代码格式化工具
black --version
flake8 --version
mypy --version
```

### 1.1.3 开发工具配置

推荐使用 VSCode 或 PyCharm 作为代码编辑器，以下是推荐的配置：

VSCode 配置（.vscode/settings.json）：

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/venv": true
    }
}
```

PyCharm 配置步骤：打开项目目录，配置 Python 解释器为 `./venv/bin/python`，在 Settings > Tools > Black 中配置 Black 格式化工具。

## 1.2 代码规范

weread-exporter 项目遵循 Python 社区的编码规范，同时有一些项目特定的约定。本节将详细介绍代码规范的具体要求。

### 1.2.1 Python 风格指南

项目主要遵循 PEP 8 风格指南，同时采用以下补充规则：

代码行长度限制为 100 字符，比 PEP 8 的 79 字符更宽松，但仍保持良好的可读性。使用 black 工具自动格式化可以确保一致性：

```bash
# 格式化整个项目
black weread_exporter/ tests/

# 检查格式（不修改）
black --check weread_exporter/ tests/
```

导入组织规范：导入应该分组，组之间用空行分隔。标准库导入在前，第三方库导入在后，最后是本地导入：

```python
# 标准库
import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, cast

# 第三方库
import bs4
import markdown

# 本地导入
from ebooklib import epub

from . import utils
```

命名约定遵循 PEP 8：类名使用 CamelCase，函数和变量使用 snake_case，常量使用全大写加下划线：

```python
class WeReadExporter:      # 类名
    DEFAULT_TIMEOUT = 60    # 类常量
    
    def export_markdown(self):  # 方法
        save_path = "output"    # 局部变量
```

### 1.2.2 文档要求

每个公共模块、类和函数都应该有文档字符串：

```python
def fetch(url: str, method: str = "GET", headers: Any = None,
          data: Any = None, respond_with_headers: bool = False) -> Union[bytes, Tuple[int, Any, bytes]]:
    """发送 HTTP 请求，支持重试机制。
    
    Args:
        url: 请求的 URL
        method: HTTP 方法，默认为 GET
        headers: 请求头字典
        data: 请求体数据
        respond_with_headers: 是否在返回值中包含响应头
    
    Returns:
        如果 respond_with_headers 为 True，返回 (status, headers, body) 元组
        否则返回响应体 bytes
    
    Raises:
        RuntimeError: 请求失败且重试用尽
    """
    pass
```

文档字符串使用 Google 风格，包含 Args、Returns、Raises 等部分。对于简单的函数，可以使用单行文档字符串。

### 1.2.3 类型注解

项目鼓励使用类型注解来提高代码可读性和 IDE 支持。类型注解应该尽可能精确，避免过度使用 Any：

```python
# 推荐
def get_book_info(self) -> dict[str, Any]:
    pass

# 避免
def get_book_info(self) -> dict:
    pass

# 对于复杂类型，使用 Union 或 Optional
def process_book(self, book_id: str, timeout: int | None = None) -> bool:
    pass
```

对于已有的代码，可以逐步添加类型注解。新代码应该从一开始就使用类型注解。

### 1.2.4 代码检查工具

项目使用多种工具进行代码检查：

```bash
# 运行 flake8 检查代码风格
flake8 weread_exporter/ tests/

# 运行 mypy 检查类型
mypy weread_exporter/

# 运行所有检查
flake8 weread_exporter/ tests/
mypy weread_exporter/
black --check weread_expreter/
```

建议在提交代码前运行所有检查工具，确保代码符合规范。

## 1.3 测试策略

测试是保证代码质量的关键。本节将介绍项目的测试策略、测试用例设计方法和测试运行方法。

### 1.3.1 测试结构

项目的测试文件位于 `tests/` 目录下，测试文件以 `test_` 开头：

```
tests/
├── __init__.py
├── test_export.py      # 导出功能测试
├── test_webpage.py     # 浏览器功能测试
├── test_utils.py       # 工具函数测试
└── conftest.py         # pytest 配置和 fixtures
```

测试目录结构与源代码目录结构对应，便于查找和维护。

### 1.3.2 测试用例设计

测试用例应该覆盖正常情况和异常情况。以下是测试用例设计原则：

**等价类划分**：将输入数据划分为等价类，每类取代表性值进行测试。例如，测试导出功能时，应该测试不同格式（EPUB、PDF、MOBI）的导出。

**边界值测试**：特别关注边界值。例如，测试章节加载超时时，应该测试超时时间为 0、1、60、非常大等情况。

**异常测试**：测试错误输入和异常情况的处理。例如，测试不存在的书籍 ID、错误的 cookie 等情况。

```python
# 测试示例
class TestExporter:
    """WeReadExporter 测试类"""
    
    def test_export_epub_format(self, exporter):
        """测试 EPUB 格式导出"""
        result = exporter.markdown_to_epub("test.epub")
        assert result is True
        assert os.path.exists("test.epub")
    
    def test_export_invalid_book(self, invalid_book_id):
        """测试无效书籍 ID 处理"""
        with pytest.raises(ValueError):
            exporter = WeReadExporter(invalid_book_id)
    
    def test_chapter_timeout_boundary(self, page, timeout_values):
        """测试章节加载超时边界值"""
        for timeout in timeout_values:
            page.set_timeout(timeout)
            result = page.load_chapter("chapter_id")
            # 验证超时行为
```

### 1.3.3 Fixture 配置

使用 pytest fixture 管理测试依赖和初始化数据：

```python
# tests/conftest.py
import pytest
import os

@pytest.fixture(scope="session")
def chrome_browser():
    """提供 Chrome 浏览器实例（会话级别复用）"""
    from pyppeteer import launch
    browser = await launch(headless=True)
    yield browser
    await browser.close()

@pytest.fixture
def sample_book_page(chrome_browser):
    """提供包含示例书籍的页面"""
    page = await chrome_browser.newPage()
    await page.goto("https://weread.qq.com/web/bookDetail/test_id")
    yield page
    await page.close()

@pytest.fixture
def temp_output_dir(tmp_path):
    """提供临时输出目录"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)
```

### 1.3.4 运行测试

运行测试的命令和选项：

```bash
# 运行所有测试
pytest tests/

# 运行指定测试文件
pytest tests/test_export.py

# 运行指定测试类
pytest tests/test_export.py::TestExporter

# 运行指定测试函数
pytest tests/test_export.py::TestExporter::test_export_epub_format

# 显示详细输出
pytest -v tests/

# 显示覆盖率报告
pytest --cov=weread_exporter tests/

# 生成 HTML 覆盖率报告
pytest --cov=weread_exporter --cov-report=html tests/
```

## 1.4 调试技巧

在开发和问题排查过程中，高效的调试技巧可以大大节省时间。本节将介绍常用的调试方法。

### 1.4.1 日志调试

使用 Python logging 模块进行调试：

```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
)

# 在代码中添加日志
logger = logging.getLogger(__name__)

def some_function(data):
    logger.debug("Processing data: %s", data)
    logger.info("Starting process")
    try:
        result = do_something(data)
        logger.info("Process completed successfully")
        return result
    except Exception as e:
        logger.error("Process failed: %s", str(e))
        logger.exception("Full traceback:")
        raise
```

### 1.4.2 交互式调试

使用 Python 内置的 pdb 模块进行交互式调试：

```python
import pdb

def complex_function(data):
    # 设置断点
    pdb.set_trace()
    
    # 或者使用更现代的 ipdb
    import ipdb
    ipdb.set_trace()
    
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        # 在这里可以使用 ipdb 检查变量
        # n: 下一行
        # s: 进入函数
        # c: 继续执行
        # p <variable>: 打印变量
    return result
```

### 1.4.3 浏览器调试

调试浏览器相关问题时，可以使用 Chrome DevTools：

```python
# 在 webpage.py 中添加调试代码
await self._page.screenshot({"path": "debug.png"})

# 或者保存页面 HTML
html = await self._page.evaluate("document.documentElement.outerHTML")
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(html)

# 启用浏览器控制台日志
def handle_console_msg(msg):
    print("Console [%s]: %s" % (msg.type, msg.text))

self._page.on("console", handle_console_msg)
```

## 1.5 贡献流程

如果你想为 weread-exporter 贡献代码，需要遵循一定的流程。本节将介绍完整的贡献流程。

### 1.5.1 Fork 与 Clone

首先Fork项目仓库到你的 GitHub 账户，然后克隆到本地：

```bash
# Fork 后的仓库 URL
git clone https://github.com/YOUR_USERNAME/weread-exporter.git
cd weread-exporter

# 添加上游仓库
git remote add upstream https://github.com/drunkdream/weread-exporter.git
```

### 1.5.2 创建分支

为每个功能或修复创建独立的分支：

```bash
# 确保在最新代码基础上
git checkout main
git fetch upstream
git merge upstream/main

# 创建新分支
git checkout -b feature/your-feature-name
# 或修复分支
git checkout -b fix/issue-description
```

### 1.5.3 开发与提交

进行代码开发，遵循项目的代码规范。提交代码时，使用清晰的提交信息：

```bash
# 提交更改
git add .
git commit -m "feat: 添加新功能描述

- 详细说明更改内容
- 解释为什么做这个更改
"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 1.5.4 创建 Pull Request

在 GitHub 上创建 Pull Request：

1. 转到你的 fork 仓库
2. 点击「Compare & pull request」按钮
3. 填写 PR 模板中的所有项目
4. 描述你做的更改
5. 链接相关的 Issue
6. 提交 PR

PR 模板通常包含以下内容：功能描述、测试用例、截图（如果涉及 UI）、检查清单。

### 1.5.5 代码审查响应

PR 提交后，项目维护者会进行代码审查。根据审查意见进行修改：

```bash
# 在原有分支上继续修改
git add .
git commit -m "fix: 响应审查意见的修改"
git push origin feature/your-feature-name
```

审查通过后，维护者会合并你的 PR。合并后可以删除分支：

```bash
# 删除远程分支
git push origin --delete feature/your-feature-name

# 删除本地分支
git checkout main
git branch -d feature/your-feature-name
```

## 1.6 本章小结

本章全面介绍了 weread-exporter 的开发与测试指南，包括环境搭建、代码规范、测试策略、调试技巧和贡献流程。掌握这些知识后，你已经具备了参与项目开发的基本能力。

完成本章节学习后，如果你想深入了解项目的架构设计和技术原理，请阅读进阶路径的相关文档。如果你准备好开始贡献代码，请遵循本章介绍的贡献流程。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| pytest | pytest | Python 测试框架 |
| fixture | pytest Fixture | 测试数据和环境的提供者 |
| flake8 | flake8 | Python 代码风格检查工具 |
| black | black | Python 代码格式化工具 |
| mypy | mypy | Python 静态类型检查工具 |
| Fork | Fork | 在 GitHub 上复制他人仓库到自己的账户 |
| Pull Request | Pull Request | 向原仓库提交代码更改的请求 |
