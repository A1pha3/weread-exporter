# 安装配置指南

## 系统要求

### 最低要求
- **操作系统**: Windows 10 / macOS 10.15+ / Ubuntu 18.04+
- **Python版本**: 3.7 或更高版本
- **内存**: 4GB RAM
- **磁盘空间**: 1GB 可用空间

### 推荐配置
- **操作系统**: Windows 11 / macOS 12+ / Ubuntu 20.04+
- **Python版本**: 3.9 或更高版本
- **内存**: 8GB RAM
- **磁盘空间**: 2GB 可用空间

### 浏览器要求
- **Chrome/Chromium**: 版本 90+
- **Edge**: 版本 90+
- **Firefox**: 版本 90+（部分功能可能受限）

## 环境准备

### 1. 检查Python环境

首先确认您的系统已安装Python 3.7或更高版本，并安装 `uv`：

```bash
# 检查Python版本
python --version
# 或
python3 --version

# 检查 uv 版本
uv --version
```

如果未安装Python，请根据您的操作系统选择安装方法：

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载最新版本的Python安装包
3. 安装时勾选"Add Python to PATH"选项
4. 完成安装后重启命令行

#### macOS
```bash
# 使用Homebrew安装
brew install python

# 或从官网下载安装包
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包管理器
sudo apt update

# 安装Python 3.9
sudo apt install python3.9 python3-pip

# 设置Python 3.9为默认版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

### 2. 安装Git（可选）

如果您计划从源码安装或参与开发，需要安装Git：

```bash
# Windows: 下载并安装Git for Windows
# macOS: brew install git
# Ubuntu: sudo apt install git
```

## 安装方法

### 方法一：使用 uv 从源码安装（推荐）

由于项目正在开发中，建议从源码安装：

```bash
# 克隆项目仓库
git clone https://github.com/drunkdream/weread-exporter.git
cd weread-exporter

# 同步核心依赖并准备环境
uv sync

# 运行（无需额外安装）
uv run weread-exporter --help
```

### 方法二：使用 uv 管理虚拟环境（强烈推荐）

使用虚拟环境可以避免依赖冲突：

```bash
# 创建并使用项目虚拟环境（默认 .venv）
uv venv

# 同步依赖
uv sync

# 运行工具
uv run weread-exporter -b <书籍ID> -o epub
```

## 依赖管理

### 核心依赖

项目会自动安装以下核心依赖：

| 包名 | 版本 | 用途 |
|------|------|------|
| `pyppeteer` | 最新版本 | 浏览器自动化控制 |
| `beautifulsoup4` | 最新版本 | HTML解析和处理 |
| `ebooklib` | 最新版本 | EPUB格式生成 |
| `weasyprint` | ==52.5 | PDF格式生成 |
| `aiohttp` | 最新版本 | 异步HTTP请求 |
| `markdown` | 最新版本 | Markdown格式处理 |

### 可选依赖

某些功能需要额外依赖：

```bash
# 如果需要MOBI格式支持（仅Windows，按需安装）
uv add Pillow

# 开发工具（一次性同步）
uv sync --extra dev

# 运行开发工具示例
uv run pytest
uv run black --check .
uv run flake8 .
```

## 浏览器配置

### 自动下载浏览器

首次运行时，工具会自动下载Chromium浏览器：

```bash
# 首次运行会触发浏览器下载
weread-exporter --help
```

### 手动指定浏览器路径

如果您已安装Chrome/Chromium，可以指定路径：

```bash
# Windows
export CHROMIUM_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# macOS
export CHROMIUM_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Linux
export CHROMIUM_PATH="/usr/bin/google-chrome"
```

### 浏览器兼容性

| 浏览器 | 支持状态 | 备注 |
|--------|----------|------|
| Chromium | ✅ 完全支持 | 自动下载版本 |
| Google Chrome | ✅ 完全支持 | 版本90+ |
| Microsoft Edge | ✅ 完全支持 | 版本90+ |
| Firefox | ⚠️ 部分支持 | 某些功能可能受限 |
| Safari | ❌ 不支持 | 缺少必要API |

## 验证安装

### 1. 检查安装是否成功

```bash
# 检查命令行工具是否可用
uv run weread-exporter --version

# 或使用Python模块方式
uv run python -m weread_exporter --help
```

### 2. 运行简单测试

```bash
# 测试基本功能（不实际导出）
weread-exporter --book-id test --output-format epub --dry-run
```

### 3. 检查依赖完整性

```bash
# 检查所有依赖是否正常安装
python -c "import pyppeteer, bs4, ebooklib, weasyprint; print('所有依赖正常')"
```

## 配置选项

### 环境变量配置

您可以通过环境变量配置工具行为：

```bash
# 设置缓存目录
export WEREAD_CACHE_DIR="~/.weread/cache"

# 设置输出目录
export WEREAD_OUTPUT_DIR="~/Documents/books"

# 设置代理服务器
export WEREAD_PROXY="http://proxy.example.com:8080"

# 设置超时时间（秒）
export WEREAD_TIMEOUT="300"
```

### 配置文件

创建配置文件 `~/.weread/config.ini`：

```ini
[general]
cache_dir = ~/.weread/cache
output_dir = ~/Documents/books
timeout = 300

[proxy]
enabled = false
server = http://proxy.example.com:8080

[browser]
headless = true
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## 故障排除

### 常见安装问题

#### 问题1: 权限错误

**症状**: `Permission denied` 或 `Access denied`

**解决方案**:
```bash
# 使用用户安装
pip install --user weread-exporter

# 或使用虚拟环境
python -m venv venv && source venv/bin/activate
pip install weread-exporter
```

#### 问题2: 依赖冲突

**症状**: 版本冲突或安装失败

**解决方案**:
```bash
# 清理现有安装
pip uninstall weread-exporter

# 重新安装最新版本
pip install --upgrade weread-exporter

# 或使用conda环境
conda create -n weread python=3.9
conda activate weread
pip install weread-exporter
```

#### 问题3: 浏览器下载失败

**症状**: 浏览器下载超时或失败

**解决方案**:
```bash
# 手动指定已安装的浏览器
export PUPPETEER_SKIP_DOWNLOAD=true
export CHROMIUM_PATH="/path/to/your/chrome"

# 或使用代理下载
export HTTPS_PROXY="http://proxy.example.com:8080"
```

### 网络问题

如果遇到网络连接问题：

```bash
# 使用国内镜像源安装/同步
UV_PYPI_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync

# 或使用阿里云镜像
UV_PYPI_INDEX=https://mirrors.aliyun.com/pypi/simple/ uv sync
```

### 系统特定问题

#### Windows系统

```bash
# 确保已安装Visual C++ Redistributable
# 下载地址: https://aka.ms/vs/16/release/vc_redist.x64.exe

# 以管理员身份运行命令提示符
```

#### macOS系统

```bash
# 如果遇到证书错误
/Applications/Python\ 3.9/Install\ Certificates.command

# 或手动安装证书
pip install certifi
/Applications/Python\ 3.9/python -m certifi
```

#### Linux系统

```bash
# 安装系统依赖（Ubuntu/Debian）
sudo apt install libnss3-dev libatk-bridge2.0-dev libdrm-dev libxkbcommon-dev libxcomposite-dev libxdamage-dev libxrandr-dev libgbm-dev libxss-dev

# 安装系统依赖（CentOS/RHEL）
sudo yum install alsa-lib-devel cups-devel libXcomposite-devel libXrandr-devel pango-devel
```

## 下一步

安装完成后，您可以：

1. 📖 阅读[使用教程](usage.md)学习基本用法
2. 🔧 查看[高级功能](advanced.md)了解自定义配置
3. 🚀 尝试导出您的第一本书籍

---

**安装遇到问题？** 查看[故障排除指南](troubleshooting.md)获取更多帮助！ 🔧