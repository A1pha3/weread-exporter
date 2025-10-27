# 微信读书导出工具 - 详细文档

## 项目概述

微信读书导出工具是一个Python工具，用于将微信读书中的书籍内容导出为多种格式（epub、pdf、mobi、txt）。该项目通过Hook技术捕获Canvas渲染内容，实现高质量的电子书导出功能。

## 核心特性

- **多格式支持**：支持epub、pdf、mobi、txt格式导出
- **高质量渲染**：通过Canvas Hook技术获取原始渲染内容
- **智能解析**：自动识别标题、代码块、图片等元素
- **批量处理**：支持书单批量导出
- **自定义样式**：可自定义CSS样式文件

## 技术架构

### 核心组件

1. **WeReadWebPage** (`webpage.py`) - 网页控制模块
2. **WeReadExporter** (`export.py`) - 导出处理模块
3. **Canvas Hook** (`hook.js`) - Canvas拦截模块
4. **工具函数** (`utils.py`) - 通用工具模块

### 技术栈

- **Python 3.7+** - 主要编程语言
- **Pyppeteer** - 无头浏览器控制
- **BeautifulSoup4** - HTML解析
- **EbookLib** - EPUB格式处理
- **WeasyPrint** - PDF格式生成
- **AIOHTTP** - 异步HTTP请求

## 详细使用指南

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/drunkdream/weread-exporter.git
cd weread-exporter

# 安装依赖
pip3 install -e .
```

### 基本用法

```bash
# 导出单本书籍
python -m weread_exporter -b 书籍ID -o epub -o pdf

# 导出书单（书籍ID包含下划线）
python -m weread_exporter -b 书单ID -o epub

# 自定义CSS样式
python -m weread_exporter -b 书籍ID -o epub --css-file custom.css
```

### 参数详解

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-b, --book-id` | 书籍ID或书单ID | 必填 |
| `-o, --output-format` | 输出格式（可重复） | epub |
| `--load-timeout` | 章节加载超时时间 | 60秒 |
| `--load-interval` | 章节加载间隔时间 | 30秒 |
| `--css-file` | 自定义CSS文件路径 | 无 |
| `--headless` | 无头模式 | False |
| `--force-login` | 强制登录 | False |
| `--use-default-profile` | 使用默认浏览器配置 | False |
| `--mock-user-agent` | 模拟用户代理 | False |
| `--proxy-server` | 代理服务器 | 无 |

### 获取书籍ID

1. 在微信读书网页版搜索目标书籍
2. 进入书籍详情页
3. 从URL中提取书籍ID

例如：`https://weread.qq.com/web/bookDetail/08232ac0720befa90825d88`
书籍ID为：`08232ac0720befa90825d88`

## 核心代码解析

### 1. 主程序入口 (`__main__.py`)

```python
async def async_main():
    # 参数解析和初始化
    parser = argparse.ArgumentParser(prog="weread-exporter")
    parser.add_argument("-b", "--book-id", help="book id", required=True)
    
    # 异步导出流程
    page = webpage.WeReadWebPage(book_id)
    await page.launch(headless=args.headless)
    
    exporter = export.WeReadExporter(page, save_path)
    await exporter.export_markdown(args.load_timeout, args.load_interval)
    
    # 格式转换
    if "epub" in args.output_format:
        await exporter.markdown_to_epub(save_path, extra_css=extra_css)
    if "pdf" in args.output_format:
        await exporter.markdown_to_pdf(save_path, extra_css=extra_css)
```

**关键特性：**
- 支持Windows系统DLL路径补丁
- 请求哈希生成函数Hook，移除Origin头
- 异步事件循环管理

### 2. 网页控制模块 (`webpage.py`)

**浏览器启动配置：**
```python
async def launch(self, headless=False, force_login=False):
    # Chrome检测和参数配置
    chrome = self._check_chrome()
    args = ["--no-first-run", "--remote-allow-origins=*"]
    if headless:
        args.append("--headless")
    
    # 浏览器指纹隐藏
    await self._page.evaluateOnNewDocument("""() => {
        if (navigator.webdriver) {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        }
    }""")
```

**请求拦截处理：**
```python
def handle_request(self, request):
    # 拦截Canvas相关脚本
    if "/web/1.392ec47a.js" in request.url:
        with open("hook.js", "rb") as fp:
            hook_script = fp.read()
            return await request.respond({
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": hook_script
            })
    
    # 模拟API响应
    if "/web/book/read" in request.url:
        body = b'{"succ":1,"synckey":%d}' % random.randint(10000000, 100000000)
        return await request.respond({"status": 200, "body": body})
```

### 3. Canvas Hook模块 (`hook.js`)

**Canvas上下文代理：**
```javascript
HTMLCanvasElement.prototype.getContext = function (s) {
    ctx = origGetContext.call(this, s);
    
    // 收集页面元素
    canvasContextHandler.data.preList = getPreElemList();
    canvasContextHandler.data.imgList = getImgElemList();
    
    let p = new Proxy(ctx, canvasContextHandler);
    return p;
};
```

**Canvas操作拦截：**
```javascript
// 拦截fillText方法获取文本内容
if (name == "fillText") {
    // 分析字体大小、颜色等样式信息
    if (that.data.fontSize >= 27) {
        that.data.markdown += "\n\n## "; // 识别为标题
    } else if (that.data.fontColor !== defaultFontColor) {
        that.data.markdown += "`"; // 识别为高亮文本
    }
    
    that.data.markdown += args[0]; // 添加文本内容
}
```

### 4. 导出处理模块 (`export.py`)

**Markdown预处理：**
```python
async def pre_process_markdown(self):
    # 处理代码块格式
    for line in text.split("\n"):
        if line == "```":
            if not code_mode:
                output += "\n%s\n" % line
            else:
                output += "%s\n" % line
            code_mode = not code_mode
    
    # 下载并替换图片链接
    pos = output.find("](https://", pos)
    if pos >= 0:
        image_name = utils.md5(url) + ".jpg"
        with open(os.path.join(self._image_dir, image_name), "wb") as fp:
            fp.write(data)
        output = output[: pos + 2] + "images/" + image_name + output[pos1:]
```

**EPUB格式生成：**
```python
async def markdown_to_epub(self, save_path, extra_css=None):
    book = epub.EpubBook()
    book.set_title(meta_data["title"])
    book.set_language("zh-cn")
    book.add_author(meta_data["author"])
    
    # 添加章节
    for index, chapter in enumerate(meta_data["chapters"]):
        xhtml_name = "chap_%.4d.xhtml" % (index + 1)
        chap = epub.EpubHtml(title=chapter["title"], file_name=xhtml_name)
        html = self._markdown_to_html(chapter_path)
        chap.content = html.replace("code>", "epub-code>")
        book.add_item(chap)
```

**PDF格式生成：**
```python
async def markdown_to_pdf(self, save_path, extra_css=None, image_format="jpg"):
    # 合并所有章节HTML
    raw_html = '<img src="cover.jpg" style="width: 100%;">\n'
    for chapter in meta_data["chapters"]:
        raw_html += self._markdown_to_html(chapter_path, wrap=False)
    
    # 使用WeasyPrint生成PDF
    html = HTML(string=raw_html, base_url=self._save_dir)
    html.write_pdf(save_path, stylesheets=css)
```

## 设计原理和技巧

### 1. Canvas Hook技术原理

微信读书使用Canvas渲染文本内容以防止内容被轻易复制。本项目通过以下方式突破限制：

1. **JavaScript注入**：在页面加载时注入自定义脚本
2. **Proxy拦截**：拦截Canvas的getContext方法
3. **样式分析**：通过字体大小、颜色等样式信息识别文本结构
4. **实时转换**：在Canvas绘制过程中实时转换为Markdown

### 2. 异步处理架构

项目采用全异步架构设计：

- **Pyppeteer异步控制**：避免浏览器操作阻塞
- **AIOHTTP异步请求**：高效处理网络请求
- **协程并发**：支持多章节并行处理

### 3. 反检测机制

为应对网站的反爬虫检测：

- **浏览器指纹隐藏**：修改navigator.webdriver等属性
- **用户代理模拟**：随机生成Chrome版本号
- **请求头清理**：移除敏感请求头
- **Cookie管理**：智能处理登录状态

### 4. 缓存优化策略

- **资源文件缓存**：避免重复下载CSS、JS等静态资源
- **章节内容缓存**：支持断点续传
- **图片本地化**：将网络图片下载到本地

## 高级用法和自定义

### 自定义CSS样式

创建自定义CSS文件：
```css
/* custom.css */
html {
    background: #f5f5f5;
    color: #333;
    font-family: "Microsoft YaHei", sans-serif;
}

h1, h2, h3 {
    color: #2c3e50;
    border-bottom: 1px solid #eee;
}
```

### 批量处理脚本

```python
import asyncio
from weread_exporter import WeReadWebPage, WeReadExporter

async def batch_export(book_ids, formats):
    for book_id in book_ids:
        page = WeReadWebPage(book_id)
        await page.launch(headless=True)
        
        exporter = WeReadExporter(page, f"cache/{book_id}")
        await exporter.export_markdown()
        
        for fmt in formats:
            if fmt == "epub":
                await exporter.markdown_to_epub(f"output/{book_id}.epub")
            elif fmt == "pdf":
                await exporter.markdown_to_pdf(f"output/{book_id}.pdf")
```

### 错误处理和调试

**调试模式启用：**
```bash
# 启用详细日志
python -m weread_exporter -b 书籍ID -o epub --headless

# 保存调试信息
# 程序会自动保存当前HTML和截图到当前目录
```

**常见错误处理：**
- **Chrome未安装**：确保Chrome已安装并添加到PATH
- **登录失败**：使用`--force-login`参数重新登录
- **章节加载超时**：调整`--load-timeout`和`--load-interval`参数

## 项目结构说明

```
weread-exporter/
├── weread_exporter/
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # 命令行入口
│   ├── export.py            # 导出处理逻辑
│   ├── webpage.py           # 网页控制逻辑
│   ├── utils.py             # 工具函数
│   ├── hook.js              # Canvas拦截脚本
│   ├── style.css            # PDF样式文件
│   └── epub.css             # EPUB样式文件
├── tests/                   # 测试文件
├── requirements.txt          # 依赖包列表
├── setup.py                 # 安装配置
└── README.md               # 项目说明
```

## 性能优化建议

1. **内存优化**：及时关闭浏览器实例，避免内存泄漏
2. **网络优化**：使用代理服务器处理网络不稳定情况
3. **并发控制**：合理设置章节加载间隔，避免被封IP
4. **缓存利用**：充分利用本地缓存减少重复请求

## 法律和道德声明

本工具仅供技术研究和学习使用，请遵守以下原则：

1. **尊重版权**：仅用于个人学习，不得用于商业用途
2. **合理使用**：不要对服务器造成过大压力
3. **遵守协议**：遵守微信读书的用户协议
4. **责任自负**：使用本工具产生的任何问题由使用者自行承担

## 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. **代码规范**：遵循PEP 8编码规范
2. **测试覆盖**：新增功能请添加相应测试
3. **文档更新**：修改功能时同步更新文档
4. **兼容性**：确保兼容Python 3.7+版本

## 更新日志

- **v0.1.0**：初始版本，支持epub、pdf、mobi格式导出
- **后续版本**：持续优化Hook逻辑，提升导出质量

---

## 深入技术细节

### Canvas Hook实现原理详解

#### 1. Canvas渲染流程分析

微信读书的Canvas渲染流程如下：
```javascript
// 1. 获取Canvas上下文
const ctx = canvas.getContext('2d');

// 2. 设置字体和颜色
ctx.font = '18px "PingFang SC"';
ctx.fillStyle = 'rgb(208, 211, 216)';

// 3. 绘制文本
ctx.fillText('文本内容', x, y);
```

#### 2. Proxy拦截机制

项目使用ES6 Proxy对象拦截Canvas操作：
```javascript
const canvasContextHandler = {
    get(target, name) {
        if (name in target) {
            if (target[name] instanceof Function) {
                return function (...args) {
                    // 拦截fillText方法
                    if (name === 'fillText') {
                        // 分析样式并转换为Markdown
                        this.analyzeTextStyle(args);
                    }
                    return target[name](...args);
                };
            }
        }
        return target[name];
    },
    
    set(target, name, value) {
        // 拦截属性设置
        if (name === 'font') {
            this.analyzeFont(value);
        } else if (name === 'fillStyle') {
            this.analyzeColor(value);
        }
        target[name] = value;
        return true;
    }
};
```

#### 3. 样式识别算法

**标题识别逻辑：**
```javascript
if (this.data.fontSize >= 27) {
    // 一级标题
    this.data.markdown += "\n\n# ";
    this.data.titleMode = true;
} else if (this.data.fontSize >= 23) {
    // 二级标题
    this.data.markdown += "\n\n## ";
    this.data.titleMode = true;
}
```

**高亮文本识别：**
```javascript
if (this.data.fontColor !== defaultFontColor) {
    if (!this.data.highlightMode) {
        this.data.markdown += "`";
        this.data.highlightMode = true;
    }
}
```

### 异步架构设计模式

#### 1. 协程并发模型

项目采用asyncio协程实现高效并发：
```python
async def export_book(book_id):
    # 创建浏览器实例
    page = WeReadWebPage(book_id)
    await page.launch()
    
    # 并发处理章节
    tasks = []
    for chapter in chapters:
        task = asyncio.create_task(export_chapter(page, chapter))
        tasks.append(task)
    
    # 等待所有章节完成
    await asyncio.gather(*tasks)
```

#### 2. 资源管理策略

**浏览器实例池：**
```python
class BrowserPool:
    def __init__(self, max_browsers=5):
        self.max_browsers = max_browsers
        self.browsers = []
        self.semaphore = asyncio.Semaphore(max_browsers)
    
    async def get_browser(self):
        async with self.semaphore:
            if self.browsers:
                return self.browsers.pop()
            else:
                return await self.create_browser()
```

### 反检测技术深度解析

#### 1. 浏览器指纹隐藏

```javascript
// 隐藏webdriver属性
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// 伪造插件列表
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// 伪造语言设置
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});
```

#### 2. 请求头伪装

```python
async def fetch_with_headers(url, headers=None):
    default_headers = {
        'User-Agent': generate_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    if headers:
        default_headers.update(headers)
    
    # 移除敏感头信息
    default_headers.pop('sec-ch-ua', None)
    default_headers.pop('sec-ch-ua-platform', None)
    
    return await fetch(url, headers=default_headers)
```

### 缓存系统设计

#### 1. 多级缓存架构

```python
class CacheSystem:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.file_cache = FileCache(cache_dir)
    
    async def get(self, key, fetch_func):
        # 内存缓存
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # 文件缓存
        cached_data = await self.file_cache.get(key)
        if cached_data:
            self.memory_cache[key] = cached_data
            return cached_data
        
        # 网络获取
        data = await fetch_func()
        self.memory_cache[key] = data
        await self.file_cache.set(key, data)
        return data
```

#### 2. 智能缓存策略

```python
class SmartCache:
    def __init__(self):
        self.access_times = {}
        self.size_limit = 100 * 1024 * 1024  # 100MB
    
    async def should_cache(self, url, data):
        # 根据文件类型和大小决定是否缓存
        if len(data) > 10 * 1024 * 1024:  # 大于10MB不缓存
            return False
        
        if url.endswith(('.jpg', '.png', '.gif')):
            return True
        
        if url.endswith(('.css', '.js')):
            return len(data) < 1 * 1024 * 1024  # CSS/JS小于1MB
        
        return False
```

## 扩展开发指南

### 1. 添加新的输出格式

```python
class CustomExporter(WeReadExporter):
    async def markdown_to_custom_format(self, save_path, **kwargs):
        # 读取Markdown内容
        meta_data = await self._load_meta_data()
        
        # 自定义格式转换逻辑
        custom_content = self.convert_to_custom_format(meta_data)
        
        # 保存文件
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(custom_content)
```

### 2. 自定义Hook逻辑

```javascript
// 扩展Canvas Hook功能
canvasContextHandler.customFeature = {
    // 添加新的文本识别规则
    analyzeCustomText: function(text, style) {
        if (style.font.includes('特殊字体')) {
            return `**${text}**`;  // 加粗处理
        }
        return text;
    }
};
```

### 3. 插件系统设计

```python
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    
    async def process_hook(self, hook_type, data):
        for plugin in self.plugins:
            if hasattr(plugin, hook_type):
                data = await getattr(plugin, hook_type)(data)
        return data
```

## 性能监控和调试

### 1. 性能指标收集

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(description):
    start = time.time()
    yield
    end = time.time()
    print(f'{description}: {end - start:.2f}s')

# 使用示例
with timer('章节导出'):
    await exporter.export_markdown()
```

### 2. 内存使用监控

```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

# 定期检查内存使用
async def monitor_memory():
    while True:
        memory_mb = get_memory_usage()
        if memory_mb > 500:  # 超过500MB警告
            logging.warning(f'内存使用过高: {memory_mb}MB')
        await asyncio.sleep(60)  # 每分钟检查一次
```

## 安全注意事项

### 1. 代码安全

- 避免硬编码敏感信息
- 使用环境变量存储配置
- 定期更新依赖包修复安全漏洞

### 2. 使用安全

- 不要对服务造成过大压力
- 遵守robots.txt规则
- 合理设置请求间隔

---

*本文档持续更新，欢迎贡献和改进*