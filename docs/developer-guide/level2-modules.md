# 核心模块详解

> 本文档是开发路径的第二篇，面向希望深入理解 weread-exporter 各模块实现的开发者。通过阅读本文档，你将全面掌握 CLI 层、业务层、浏览器层、工具层的设计原理和实现细节，能够进行模块级别的分析和二次开发。

## 学习目标

完成本章节学习后，你将能够详细解释每个核心模块的工作原理，理解关键设计决策背后的考量，并能够修改或扩展现有功能。此外，你还将掌握模块间接口的设计原则，学习如何在保持兼容性的前提下进行扩展。

### 基础目标

首先，你将深入理解 `__main__.py` 中的命令行解析逻辑和异步架构设计。其次，你将掌握 `WeReadExporter` 类的完整导出流程，包括 Markdown 提取、预处理和格式转换。第三，你将理解 `WeReadWebPage` 类如何与浏览器交互，包括请求拦截和内容提取。第四，你将熟悉工具函数的实现，包括 HTTP 请求、缓存管理和错误处理。

### 进阶目标

进阶目标要求你能够评估设计决策的优劣，理解为什么选择当前的实现方式。你还将具备设计模块扩展方案的能力，能够在保持向后兼容的前提下添加新功能。此外，你将能够识别模块间的依赖关系，理解修改一处代码可能带来的影响。

## 1.1 CLI 层深度解析

CLI 层是用户与系统交互的入口，负责解析参数、初始化环境、协调各模块工作。本节将深度解析 CLI 层的实现细节，包括参数解析机制、异步架构和错误处理策略。

### 1.1.1 参数解析机制

CLI 层的核心是 `async_main()` 函数，它实现了完整的参数解析和工作流程控制。参数解析使用 Python 标准库 `argparse`，提供了清晰的参数定义和错误提示：

```python
async def async_main():
    parser = argparse.ArgumentParser(
        prog="weread-exporter", 
        description="WeRead book export cmdline tool"
    )
    
    # 必选参数
    parser.add_argument("-b", "--book-id", help="book id")
    
    # 输出格式参数（可多次指定）
    parser.add_argument(
        "-o",
        "--output-format",
        help="output file format",
        action="append",
        choices=["md", "epub", "pdf", "mobi", "txt"]
    )
    
    # 可选参数
    parser.add_argument("--load-timeout", type=int, default=60,
                       help="load chapter page timeout")
    parser.add_argument("--load-interval", type=int, default=30,
                       help="load chapter page interval time")
    
    # 浏览器相关参数
    parser.add_argument("--headless", action="store_true", default=False)
    parser.add_argument("--force-login", action="store_true", default=False)
    parser.add_argument("--proxy-server", help="http proxy server")
    
    # 信息查询参数
    parser.add_argument("--list-booklists", action="store_true", default=False)
    parser.add_argument("--list-ids", action="store_true", default=False)
```

参数设计体现了几个重要原则。首先是灵活性，`-o` 参数使用 `action="append"` 允许用户指定多种输出格式。其次是合理的默认值，大多数参数都有合理的默认值，用户可以在大多数情况下只指定书籍 ID。第三是参数间的逻辑约束，例如 `--list-booklists` 不需要 `--book-id`，这种约束在参数解析后通过代码逻辑检查。

参数处理完成后，`async_main()` 会进行参数验证和预处理：

```python
# 设置默认输出格式
args.output_format = args.output_format or ["epub"]

# 处理 MOBI 格式的依赖
if "mobi" in args.output_format and "epub" not in args.output_format:
    args.output_format.append("epub")

# 验证书单 ID 格式
if "_" in args.book_id:
    # 书单 ID 包含下划线
    pass
```

### 1.1.2 异步架构设计

weread-exporter 使用 Python 的 `asyncio` 库实现异步执行，这是处理 I/O 密集型任务（如网络请求、浏览器操作）的最佳选择。异步架构的核心是事件循环的管理：

```python
def main():
    # ... 初始化代码 ...
    
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 运行主异步函数
        loop.run_until_complete(async_main())
    except Exception as e:
        logging.error("Fatal error in main program: %s" % str(e))
        return 1
    finally:
        # 确保事件循环被关闭
        loop.close()
```

这种设计确保了异步代码的正确执行，同时提供了异常处理的保障。事件循环的创建和关闭遵循了最佳实践，避免了资源泄漏。

异步函数的调用模式遵循了生产者-消费者模式：`async_main()` 是协调者，创建任务并等待完成；具体的工作由 `WeReadExporter` 和 `WeReadWebPage` 中的异步方法执行。

### 1.1.3 平台兼容性处理

CLI 层包含针对不同操作系统的兼容性处理代码：

```python
def patch_windows():
    """Windows 平台特定初始化"""
    bin_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                           "bin", "win32")
    os.environ["PATH"] += ";" + bin_path
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(bin_path)

def patch_generateRequestHash():
    """修补 Pyppeteer 的请求生成逻辑"""
    from pyppeteer import network_manager
    
    orig_generateRequestHash = network_manager.generateRequestHash
    
    def patched_generateRequestHash(request):
        # 移除 Origin 头避免跨域问题
        request["headers"].pop("Origin", None)
        return orig_generateRequestHash(request)
    
    network_manager.generateRequestHash = patched_generateRequestHash
```

`patch_windows()` 函数处理 Windows 平台的 DLL 搜索路径问题，确保 Chrome 运行时能够找到必要的依赖。`patch_generateRequestHash()` 函数修补了 Pyppeteer 的内部函数，移除了可能导致跨域问题的 HTTP 头。

## 1.2 业务层深度解析

业务层由 `WeReadExporter` 类实现，包含了导出流程的核心逻辑。本节将详细分析 `WeReadExporter` 的设计，包括 Markdown 提取、预处理和格式转换的实现细节。

### 1.2.1 Markdown 提取流程

`export_markdown()` 方法是业务层的核心，负责从浏览器获取所有章节的内容：

```python
async def export_markdown(self, timeout=60, interval=30):
    """导出所有章节为 Markdown"""
    # 初始化章节目录
    if not os.path.isdir(self._chapter_dir):
        os.makedirs(self._chapter_dir)
    
    # 加载书籍元数据
    meta_data = await self._load_meta_data()
    
    # 遍历所有章节
    for index, chapter in enumerate(meta_data["chapters"]):
        file_path = self._make_chapter_path(index, chapter["id"])
        
        # 检查缓存（大小大于 3 字节视为有效）
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 3:
            logging.info("Chapter %s cached, skipping", chapter["title"])
            continue
        
        # 导航到章节页面
        await self._goto_and_wait(chapter["id"], timeout)
        
        # 获取 Markdown 内容
        markdown = await self._page.get_markdown()
        
        # 保存文件
        self._save_chapter(file_path, markdown)
        
        # 等待间隔
        await asyncio.sleep(interval)
```

这个方法展示了几个重要的设计决策。首先是缓存检查，通过文件大小判断缓存是否有效，避免重复处理。其次是错误处理和重试机制，每章最多重试三次。第三是间隔控制，通过 `asyncio.sleep()` 控制请求频率。

### 1.2.2 图片预处理

`pre_process_markdown()` 方法负责处理章节中的图片资源：

```python
async def pre_process_markdown(self):
    """预处理 Markdown，处理图片引用"""
    meta_data = await self._load_meta_data()
    
    for index, chapter in enumerate(meta_data["chapters"]):
        chapter_path = self._make_chapter_path(index, chapter["id"])
        
        # 读取章节文件
        with open(chapter_path, "rb") as fp:
            text = fp.read().decode()
        
        # 处理 Markdown 中的图片引用
        text = await self._process_images(text)
        
        # 备份并保存
        if not os.path.isfile(chapter_path + ".bak"):
            os.rename(chapter_path, chapter_path + ".bak")
        
        with open(chapter_path, "wb") as fp:
            fp.write(text.encode())
```

图片处理是导出的关键步骤之一。微信读书的图片使用 CDN 加速，导出的 Markdown 文件需要将远程 URL 替换为本地文件路径。这个方法首先解析 Markdown 中的图片引用，下载图片到本地，然后更新引用路径。

### 1.2.3 格式转换实现

业务层提供了多种格式转换方法，每种格式使用不同的技术栈：

EPUB 转换使用 EbookLib 库：

```python
async def markdown_to_epub(self, save_path, extra_css=None):
    """将 Markdown 转换为 EPUB"""
    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title(meta_data["title"])
    book.set_language("zh-cn")
    book.add_author(meta_data["author"])
    
    # 添加封面
    with open(self._cover_image_path, "rb") as fp:
        image_data = fp.read()
        book.set_cover("cover.jpg", image_data)
    
    # 转换每个章节
    chapters = []
    for index, chapter in enumerate(meta_data["chapters"]):
        chapter_path = self._make_chapter_path(index, chapter["id"])
        html = self._markdown_to_html(chapter_path)
        
        # 创建 EPUB 章节
        chap = epub.EpubHtml(
            title=chapter["title"], 
            file_name="chap_%.4d.xhtml" % (index + 1)
        )
        chap.content = html
        book.add_item(chap)
        chapters.append(chap)
    
    # 设置目录结构
    book.toc = [epub.Link("chap_0001.xhtml", "Chapter 1", "ch1")]
    book.spine = ["nav", *chapters]
    
    # 生成文件
    epub.write_epub(save_path, book, {})
```

PDF 转换使用 WeasyPrint 库：

```python
async def markdown_to_pdf(self, save_path, extra_css=None, 
                         image_format="jpg", dump_html=False):
    """将 Markdown 转换为 PDF"""
    from weasyprint import HTML, CSS
    
    meta_data = await self._load_meta_data()
    
    # 构建 HTML 内容
    raw_html = '<img src="cover.jpg" style="width: 100%;">\n'
    for index, chapter in enumerate(meta_data["chapters"]):
        chapter_path = self._make_chapter_path(index, chapter["id"])
        raw_html += self._markdown_to_html(chapter_path, wrap=False)
    
    # 加载 CSS 样式
    css_path = os.path.join(current_path, "style.css")
    with open(css_path) as fp:
        raw_css = fp.read()
    if extra_css:
        raw_css += "\n" + extra_css
    
    # 生成 PDF
    html = HTML(string=raw_html, base_url=self._save_dir)
    css = [CSS(string=raw_css)]
    html.write_pdf(save_path, stylesheets=css)
```

## 1.3 浏览器层深度解析

浏览器层由 `WeReadWebPage` 类实现，是 weread-exporter 与微信读书网站交互的桥梁。本节将详细分析浏览器层的关键实现，包括浏览器启动、请求拦截、内容提取和反检测机制。

### 1.3.1 浏览器启动与配置

`launch()` 方法负责启动 Chrome 浏览器实例：

```python
async def launch(self, headless=False, force_login=False,
                 use_default_profile=False, mock_user_agent=False,
                 proxy_server=None):
    """启动 Chrome 浏览器"""
    # 检查 Chrome 是否可用
    chrome = self._check_chrome()
    
    # 构建启动参数
    args = [
        "--no-first-run",
        "--remote-allow-origins=*",
    ]
    
    if headless:
        args.append("--headless")
        if sys.platform == "linux" and os.getuid() == 0:
            args.append("--no-sandbox")
    
    if not use_default_profile:
        args.append("--window-size=%d,%d" % self.__class__.window_size)
    
    if mock_user_agent:
        args.append('--user-agent="%s"' % utils.generate_user_agent())
    
    if proxy_server:
        args.append("--proxy-server=%s" % proxy_server)
    
    # 启动浏览器
    self._browser = await pyppeteer.launch(
        executablePath=chrome,
        ignoreDefaultArgs=True,
        args=args,
        defaultViewport=None,
        logLevel=logging.INFO,
    )
```

参数配置体现了对不同场景的支持：无头模式用于自动化执行，窗口大小设置影响页面布局，用户代理设置用于反检测，代理服务器设置用于绕过网络限制。

### 1.3.2 反检测机制

weread-exptuneer 使用多种技术伪装浏览器环境，以避免被微信读书识别为自动化访问：

```python
ANTI_DETECTION_SCRIPT = """
() => {
    // 伪装 navigator.webdriver
    if (navigator.webdriver) {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    }
    
    // 伪装 navigator.plugins
    if (navigator.plugins.length === 0) {
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    }
    
    // 伪装 navigator.languages
    if (navigator.languages.length === 0) {
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    }
    
    // 伪装 Chrome 对象
    window.chrome = window.chrome || {
        runtime: {},
    };
}
"""
```

反检测脚本通过 `evaluateOnNewDocument()` 方法注入到每个新页面中，在页面内容加载之前执行。这种方式确保了反检测措施在页面渲染之前就生效。

### 1.3.3 请求拦截机制

`WeReadWebPage` 实现了请求拦截功能，用于注入 Canvas Hook 和模拟 API 响应：

```python
async def pre_load_page(self):
    """启用请求拦截"""
    await self._page.setRequestInterception(True)
    self._page.on("request", self.handle_request)

async def _handle_request(self, request):
    """处理拦截到的请求"""
    url = request.url
    
    # 注入 Canvas Hook
    if "/web/1.392ec47a.js" in url:
        with open("hook.js", "rb") as fp:
            hook_script = fp.read()
        response = {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": hook_script,
        }
        return await request.respond(response)
    
    # 模拟 API 响应
    if "/web/book/read" in url:
        body = b'{"succ":1,"synckey":%d}' % random.randint(10000000, 100000000)
        response = {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": body,
        }
        return await request.respond(response)
    
    # 其他请求继续处理
    await request.continue_()
```

请求拦截机制允许工具在请求发送前或响应返回前进行干预。这是注入 Canvas Hook 和模拟 API 响应的关键技术基础。

## 1.4 工具层深度解析

工具层提供了各种通用功能的实现，包括 HTTP 请求、缓存管理、错误处理等。本节将详细分析工具层的关键实现。

### 1.4.1 HTTP 请求实现

`fetch()` 函数实现了带重试机制的异步 HTTP 请求：

```python
async def fetch(url: str, method: str = "GET", headers: Any = None,
                data: Any = None, respond_with_headers: bool = False):
    """发送 HTTP 请求，带重试机制"""
    request_headers = headers or {}
    request_headers.pop("sec-ch-ua", None)
    request_headers.pop("sec-ch-ua-platform", None)
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            try:
                http_method = getattr(session, method.lower())
                async with http_method(url, headers=request_headers, 
                                       data=data) as response:
                    result = await response.read()
                    if respond_with_headers:
                        return response.status, response.headers, result
                    return result
            except (aiohttp.ClientError, asyncio.TimeoutError, 
                    RuntimeError) as e:
                logging.warning("Failed to fetch URL %s (attempt %d/3): %s" 
                              % (url, attempt + 1, str(e)))
                if attempt == 2:
                    raise RuntimeError(f"Fetch url {url} failed after 3 attempts")
```

HTTP 请求实现的关键特点包括：使用 aiohttp 实现异步请求、提供最多三次重试、支持响应头返回模式、统一的请求头清理。

### 1.4.2 异常体系设计

工具层定义了清晰的异常体系，便于调用者进行针对性处理：

```python
class ChromeNotInstalledError(Exception):
    """Chrome 未安装或找不到"""
    pass

class LoginRequiredError(RuntimeError):
    """需要登录才能继续操作"""
    pass

class LoadChapterFailedError(RuntimeError):
    """加载章节失败"""
    pass

class InvalidUserError(RuntimeError):
    """用户信息无效"""
    pass
```

异常设计遵循了几个原则：首先，区分了检查型异常（应该提前检查并处理）和运行时异常（表示程序错误）。其次，提供了足够的上下文信息，便于调试和错误报告。第三，异常名称清晰表达了错误含义，便于调用者判断如何处理。

### 1.4.3 缓存管理

`get_book_list()` 和 `get_book_list_full()` 函数实现了书单解析功能：

```python
async def get_book_list(book_list_id: str):
    """获取书单中的书籍列表（返回哈希 ID）"""
    book_list = []
    url = "https://weread.qq.com/misc/booklist/" + book_list_id
    result = await fetch(url)
    html = result.decode()
    
    # 解析 HTML 获取书籍信息
    pos = html.find("window.__NUXT__")
    if pos <= 0:
        raise RuntimeError(f"Unexpected html for book list {book_list_id}")
    
    # 提取书籍数据
    # ... 解析逻辑
    
    return book_list
```

书单解析通过查找 Nuxt.js 注入的 `__NUXT__` 变量来提取页面数据。这种方法比解析 DOM 更可靠，因为数据直接来自服务端渲染。

## 1.5 模块接口设计

良好的模块接口设计是系统可维护性的关键。本节将分析 weread-exporter 的模块接口设计原则。

### 1.5.1 接口抽象

业务层与浏览器层之间通过抽象接口交互：

```python
# 浏览器层提供的接口（WeReadWebPage 类方法）
async def get_book_info(self) -> dict:
    """获取书籍基本信息"""
    pass

async def goto_chapter(self, chapter_id: str, timeout=120):
    """导航到指定章节"""
    pass

async def get_markdown(self) -> str:
    """获取当前页面的 Markdown 内容"""
    pass
```

这种设计使得业务层不依赖于具体的浏览器实现，便于测试和替换。

### 1.5.2 错误传播机制

各层之间的错误通过异常机制传播：

```python
async def export_markdown(self, timeout=60, interval=30):
    try:
        await self._page.goto_chapter(chapter["id"], timeout=timeout)
    except utils.LoadChapterFailedError:
        # 转换为更具体的错误
        raise
    except Exception as e:
        # 包装为业务错误
        raise utils.LoadChapterFailedError(
            f"Failed to load chapter {chapter['title']}: {str(e)}"
        ) from e
```

错误处理遵循了几个原则：保留原始异常信息（使用 `from e`）、将低层错误转换为业务语义明确的错误、允许调用者区分不同类型的错误。

## 1.6 本章小结

本章深入分析了 weread-exporter 的四大核心模块：CLI 层、业务层、浏览器层和工具层。你已经学习了各模块的设计原理、实现细节和接口约定。这些知识为进行二次开发和问题排查提供了坚实的基础。

完成本章节学习后，建议通过实践任务巩固所学知识。如果你想学习如何搭建开发环境和进行测试，请继续阅读开发路径的下一级「开发与测试指南」。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 事件循环 | Event Loop | asyncio 的核心机制，管理异步任务的执行 |
| 请求拦截 | Request Interception | 在请求发送前或响应返回前进行干预 |
| Canvas Hook | Canvas Hook | 拦截 Canvas 绘制方法以提取内容 |
| 依赖注入 | Dependency Injection | 通过参数传入依赖，提高可测试性 |
| 异常传播 | Exception Propagation | 错误在不同模块间传递的机制 |
| EPUB | EPUB | 开放电子书标准格式 |
| WeasyPrint | WeasyPrint | 基于 CSS 的 PDF 渲染引擎 |
