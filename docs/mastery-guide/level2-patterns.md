# 核心设计模式详解

> 本文档是进阶路径的第二篇，面向希望深入学习软件设计模式的开发者。通过阅读本文档，你将掌握 weread-exporter 中使用的核心设计模式，理解每种模式的意图、结构、适用场景，以及如何在实际项目中应用这些模式。这些知识将帮助你提升软件设计能力，写出更加优雅、可维护的代码。

## 学习目标

完成本章节学习后，你将能够识别并理解 weread-exporter 中使用的设计模式，掌握每种模式的应用场景和实现技巧，并能够将这些模式应用到自己的项目中。此外，你还将学会如何根据问题特点选择合适的设计模式，以及如何避免滥用设计模式。

### 基础目标

首先，你将深入理解六种核心设计模式：模板方法模式、策略模式、装饰器模式、责任链模式、工厂模式和观察者模式。其次，你将掌握每种模式在 weread-exporter 中的具体实现，理解代码结构背后的设计考量。第三，你将学会识别代码中的模式应用，能够阅读他人代码并理解其设计意图。

### 进阶目标

进阶目标要求你能够批判性地分析设计模式的使用，理解每种模式的优缺点和适用边界。你还将具备设计新模式的能力，能够根据具体问题创造性地应用或组合设计模式。此外，你将能够指导他人学习设计模式，帮助团队提升代码质量。

## 1.1 模板方法模式

模板方法模式是一种行为型模式，它在抽象类中定义算法的骨架，将某些步骤的具体实现延迟到子类中。这样可以在不改变算法整体结构的情况下，允许子类重写算法的某些特定步骤。

### 1.1.1 模式结构与意图

模板方法模式的核心思想是：「在一个方法中定义算法的骨架，将某些步骤的具体实现留给子类」。这使得算法可以在不改变其结构的情况下，被扩展和定制。

该模式的主要参与者包括：抽象类（AbstractClass）定义模板方法和算法中的各个步骤；具体类（ConcreteClass）实现抽象类中未定义的步骤。模板方法通常是一个 final 方法，防止子类修改算法的核心流程。

### 1.1.2 weread-exporter 中的应用

在 weread-exporter 的格式转换中，模板方法模式被广泛应用。以下是一个简化的示例：

```python
from abc import ABC, abstractmethod
from typing import Optional
import asyncio


class FormatConverter(ABC):
    """格式转换器基类，定义了转换的模板方法"""
    
    async def convert(self, book_id: str, output_path: str, **options) -> bool:
        """模板方法：定义转换的完整流程
        
        这个方法定义了格式转换的骨架流程：
        1. 加载书籍数据
        2. 预处理内容
        3. 执行格式转换
        4. 保存输出文件
        
        子类只需要实现具体的转换逻辑。
        """
        # 步骤 1：加载数据（所有格式都需要）
        book_data = await self._load_book_data(book_id)
        if book_data is None:
            return False
        
        # 步骤 2：预处理（可被子类覆盖）
        processed_data = await self._preprocess(book_data)
        
        # 步骤 3：执行具体格式转换（子类实现）
        converted = await self._do_convert(processed_data, **options)
        
        # 步骤 4：保存文件（所有格式都需要）
        success = await self._save(converted, output_path)
        
        return success
    
    async def _load_book_data(self, book_id: str) -> Optional[dict]:
        """加载书籍数据"""
        # 具体实现：读取缓存或从网络获取
        pass
    
    async def _preprocess(self, book_data: dict) -> dict:
        """预处理数据，默认实现"""
        return book_data
    
    @abstractmethod
    async def _do_convert(self, book_data: dict, **options) -> bytes:
        """执行具体格式转换，由子类实现"""
        pass
    
    async def _save(self, content: bytes, output_path: str) -> bool:
        """保存输出文件"""
        import aiofiles
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(content)
        return True


class EPUBConverter(FormatConverter):
    """EPUB 格式转换器"""
    
    async def _do_convert(self, book_data: dict, **options) -> bytes:
        """实现 EPUB 特有的转换逻辑"""
        from ebooklib import epub
        
        book = epub.EpubBook()
        book.set_title(book_data["title"])
        book.set_language("zh-cn")
        book.add_author(book_data["author"])
        
        # 添加封面
        if "cover" in book_data:
            book.set_cover("cover.jpg", book_data["cover"])
        
        # 添加章节
        for chapter in book_data["chapters"]:
            chap = epub.EpubHtml(
                title=chapter["title"],
                file_name=f"chap_{chapter['id']}.xhtml"
            )
            chap.content = self._chapter_to_html(chapter)
            book.add_item(chap)
        
        # 生成 EPUB 文件
        import io
        output = io.BytesIO()
        epub.write_epub(output, book, {})
        return output.getvalue()


class PDFConverter(FormatConverter):
    """PDF 格式转换器"""
    
    async def _do_convert(self, book_data: dict, **options) -> bytes:
        """实现 PDF 特有的转换逻辑"""
        from weasyprint import HTML, CSS
        
        # 构建 HTML 内容
        html_content = self._build_html(book_data)
        
        # 应用样式
        css = CSS(string=self._get_css(options))
        
        # 生成 PDF
        html = HTML(string=html_content)
        return html.write_pdf(stylesheets=[css])
```

这个设计清晰地展示了模板方法模式的应用。`FormatConverter` 类定义了转换算法的骨架：加载数据、预处理、执行转换、保存文件。具体的转换逻辑则由子类 `EPUBConverter` 和 `PDFConverter` 实现。

### 1.1.3 模式优缺点分析

模板方法模式的优点体现在多个方面。首先是代码复用，算法骨架只需在抽象类中定义一次，所有子类都可以复用这套逻辑。其次是扩展性好，只需创建新的子类并实现特定方法即可添加新的格式支持，符合开闭原则。第三是控制反转，父类控制流程，子类实现细节，符合依赖倒置原则。

该模式的缺点包括：继承关系的约束，子类必须继承自抽象类，这在某些语言中可能是单一继承的限制。另一个缺点是难以理解，如果模板方法过于复杂，子类可能难以理解算法的完整流程。

### 1.1.4 适用场景与注意事项

模板方法模式适用于以下场景：需要定义算法的骨架，但某些步骤的具体实现需要由子类提供；多个类有相同的算法流程，只有部分步骤不同；需要控制子类的扩展点，避免子类破坏算法结构。

使用该模式时需要注意以下事项：保持模板方法简洁，只包含算法骨架，避免在其中实现过多逻辑；为每个步骤提供有意义的默认实现，减少子类的负担；使用 final 关键字保护模板方法，防止子类修改算法核心流程。

## 1.2 策略模式

策略模式是一种行为型模式，它定义了一系列算法，将每个算法封装起来，使它们可以相互替换。策略模式让算法独立于使用它的客户端而变化。

### 1.2.1 模式结构与意图

策略模式的核心思想是：「将可变的算法或行为封装为独立的对象，使它们可以独立于使用它们的代码而变化」。这使得可以在运行时动态选择不同的算法或行为。

该模式的主要参与者包括：上下文（Context）持有对策略对象的引用，根据客户端的配置使用不同的策略；策略接口（Strategy）定义算法的公共接口；具体策略（ConcreteStrategy）实现不同的算法或行为。

### 1.2.2 weread-exporter 中的应用

在 weread-exporter 中，策略模式被用于支持不同的输出格式和下载器实现：

```python
from abc import ABC, abstractmethod
from typing import Any, Protocol
from enum import Enum


class OutputFormat(Enum):
    """输出格式枚举"""
    EPUB = "epub"
    PDF = "pdf"
    MOBI = "mobi"
    TXT = "txt"
    MARKDOWN = "md"


class ConverterStrategy(ABC):
    """转换策略基类"""
    
    @abstractmethod
    async def convert(self, book_data: dict, output_path: str, **options) -> bool:
        """执行格式转换
        
        Args:
            book_data: 书籍数据
            output_path: 输出文件路径
            options: 其他选项
            
        Returns:
            是否转换成功
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        pass


class EPUBConverterStrategy(ConverterStrategy):
    """EPUB 转换策略"""
    
    async def convert(self, book_data: dict, output_path: str, **options) -> bool:
        from ebooklib import epub
        import io
        
        # 实现 EPUB 转换逻辑
        book = epub.EpubBook()
        # ... 设置书籍元数据
        
        # 添加章节
        for chapter in book_data["chapters"]:
            # ... 处理每个章节
        
        # 生成文件
        output = io.BytesIO()
        epub.write_epub(output, book, {})
        
        # 写入文件
        with open(output_path, "wb") as f:
            f.write(output.getvalue())
        
        return True
    
    def get_file_extension(self) -> str:
        return ".epub"


class PDFConverterStrategy(ConverterStrategy):
    """PDF 转换策略"""
    
    async def convert(self, book_data: dict, output_path: str, **options) -> bool:
        from weasyprint import HTML, CSS
        
        # 构建 HTML
        html_content = self._build_html(book_data)
        
        # 应用样式
        css = CSS(string=options.get("css", ""))
        
        # 生成 PDF
        html = HTML(string=html_content)
        html.write_pdf(output_path, stylesheets=[css])
        
        return True
    
    def get_file_extension(self) -> str:
        return ".pdf"


class ConverterContext:
    """转换上下文，管理策略"""
    
    def __init__(self):
        self._strategies: dict[OutputFormat, ConverterStrategy] = {}
    
    def register_strategy(self, format_type: OutputFormat, strategy: ConverterStrategy):
        """注册策略"""
        self._strategies[format_type] = strategy
    
    async def convert(
        self, 
        format_type: OutputFormat,
        book_data: dict,
        output_path: str,
        **options
    ) -> bool:
        """使用指定格式的策略进行转换"""
        strategy = self._strategies.get(format_type)
        if strategy is None:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return await strategy.convert(book_data, output_path, **options)


# 使用示例
async def main():
    context = ConverterContext()
    context.register_strategy(OutputFormat.EPUB, EPUBConverterStrategy())
    context.register_strategy(OutputFormat.PDF, PDFConverterStrategy())
    
    # 统一调用，不同格式自动选择对应策略
    await context.convert(
        OutputFormat.EPUB,
        book_data,
        "output/book.epub"
    )
    await context.convert(
        OutputFormat.PDF,
        book_data,
        "output/book.pdf"
    )
```

### 1.2.3 策略模式的高级应用

策略模式可以与工厂模式结合，创建更灵活的策略管理系统：

```python
class ConverterStrategyFactory:
    """策略工厂，根据配置创建策略"""
    
    _strategies: dict[str, type[ConverterStrategy]] = {
        "epub": EPUBConverterStrategy,
        "pdf": PDFConverterStrategy,
        "mobi": MOBIConverterStrategy,
        "txt": TXTConverterStrategy,
        "md": MarkdownConverterStrategy,
    }
    
    @classmethod
    def create(cls, format_type: str, **config) -> ConverterStrategy:
        """创建指定格式的转换策略"""
        strategy_class = cls._strategies.get(format_type.lower())
        if strategy_class is None:
            raise ValueError(f"Unknown format: {format_type}")
        return strategy_class(**config)
    
    @classmethod
    def register(cls, format_type: str, strategy_class: type[ConverterStrategy]):
        """注册新的策略"""
        cls._strategies[format_type.lower()] = strategy_class


# 运行时动态添加新策略
class NewFormatConverterStrategy(ConverterStrategy):
    async def convert(self, book_data: dict, output_path: str, **options) -> bool:
        # 新格式的实现
        pass
    
    def get_file_extension(self) -> str:
        return ".newformat"


# 注册新策略
ConverterStrategyFactory.register("newformat", NewFormatConverterStrategy)

# 使用
strategy = ConverterStrategyFactory.create("newformat")
await strategy.convert(book_data, "output.newformat")
```

## 1.3 装饰器模式

装饰器模式是一种结构型模式，它允许向对象动态地添加额外职责。就添加功能而言，装饰器比生成子类更加灵活。

### 1.3.1 模式结构与意图

装饰器模式的核心思想是：「通过组合而非继承的方式，为对象动态添加新功能」。装饰器与被装饰对象实现相同的接口，可以在不修改原有代码的情况下扩展功能。

该模式的主要参与者包括：组件接口（Component）定义对象可以执行的操作；具体组件（ConcreteComponent）实现接口的基本对象；装饰器（Decorator）持有一个组件引用，实现与组件相同的接口，在调用前后添加额外行为。

### 1.3.2 weread-exporter 中的应用

在 weread-exporter 中，装饰器模式可以用于添加日志、缓存、错误处理等横切关注点：

```python
from abc import ABC, abstractmethod
from typing import Any, Callable
import time
import asyncio


class Downloader(ABC):
    """下载器接口"""
    
    @abstractmethod
    async def download(self, url: str) -> bytes:
        """下载资源"""
        pass


class HTTPDownloader(Downloader):
    """基础 HTTP 下载器"""
    
    async def download(self, url: str) -> bytes:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()


class DownloaderDecorator(Downloader):
    """下载器装饰器基类"""
    
    def __init__(self, wrapped: Downloader):
        self._wrapped = wrapped
    
    async def download(self, url: str) -> bytes:
        return await self._wrapped.download(url)


class LoggingDecorator(DownloaderDecorator):
    """添加日志功能的装饰器"""
    
    async def download(self, url: str) -> bytes:
        start_time = time.time()
        print(f"[INFO] Downloading: {url}")
        
        try:
            result = await self._wrapped.download(url)
            elapsed = time.time() - start_time
            print(f"[INFO] Downloaded {url} in {elapsed:.2f}s ({len(result)} bytes)")
            return result
        except Exception as e:
            print(f"[ERROR] Failed to download {url}: {e}")
            raise


class CachingDecorator(DownloaderDecorator):
    """添加缓存功能的装饰器"""
    
    def __init__(self, wrapped: Downloader, cache_dir: str = "./cache"):
        super().__init__(wrapped)
        self._cache_dir = cache_dir
        self._cache: dict[str, bytes] = {}
        import os
        os.makedirs(cache_dir, exist_ok=True)
    
    async def download(self, url: str) -> bytes:
        # 检查内存缓存
        if url in self._cache:
            print(f"[CACHE] Hit: {url}")
            return self._cache[url]
        
        # 检查文件缓存
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            print(f"[CACHE] Disk hit: {url}")
            with open(cache_path, "rb") as f:
                content = f.read()
            self._cache[url] = content
            return content
        
        # 下载并缓存
        print(f"[CACHE] Miss: {url}")
        result = await self._wrapped.download(url)
        
        # 写入缓存
        self._cache[url] = result
        with open(cache_path, "wb") as f:
            f.write(result)
        
        return result
    
    def _get_cache_path(self, url: str) -> str:
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        return os.path.join(self._cache_dir, f"{url_hash}.cache")


class RetryDecorator(DownloaderDecorator):
    """添加重试功能的装饰器"""
    
    def __init__(self, wrapped: Downloader, max_retries: int = 3, delay: float = 1.0):
        super().__init__(wrapped)
        self._max_retries = max_retries
        self._delay = delay
    
    async def download(self, url: str) -> bytes:
        last_error = None
        
        for attempt in range(self._max_retries + 1):
            try:
                return await self._wrapped.download(url)
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    print(f"[RETRY] Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(self._delay * (attempt + 1))
        
        raise last_error


# 使用示例：组合多个装饰器
def create_downloader(enable_logging: bool = True,
                     enable_cache: bool = True,
                     enable_retry: bool = True) -> Downloader:
    """创建带有多种功能的下载器"""
    downloader = HTTPDownloader()
    
    if enable_retry:
        downloader = RetryDecorator(downloader, max_retries=3)
    if enable_cache:
        downloader = CachingDecorator(downloader, cache_dir="./download_cache")
    if enable_logging:
        downloader = LoggingDecorator(downloader)
    
    return downloader


async def main():
    # 创建带有日志、缓存、重试功能的下载器
    downloader = create_downloader(
        enable_logging=True,
        enable_cache=True,
        enable_retry=True
    )
    
    # 首次下载（会记录日志、缓存）
    content = await downloader.download("https://example.com/image.jpg")
    
    # 第二次下载（命中缓存，跳过下载）
    content = await downloader.download("https://example.com/image.jpg")
```

## 1.4 责任链模式

责任链模式是一种行为型模式，它通过给多个对象一个处理请求的机会，使多个对象都有机会处理请求。请求沿着对象链传递，直到其中一个对象处理它。

### 1.4.1 模式结构与意图

责任链模式的核心思想是：「将请求的发送者和接收者解耦，让多个对象都有机会处理请求」。请求沿着对象链传递，每个对象可以决定是否处理请求，或者将其传递给链中的下一个对象。

该模式的主要参与者包括：处理者（Handler）定义处理请求的接口；具体处理者（ConcreteHandler）实现处理逻辑，决定是否处理请求或传递给下一个处理者；客户端（Client）创建并配置处理链。

### 1.4.2 weread-exporter 中的应用

在 weread-exporter 中，责任链模式可以用于请求处理和验证流程：

```python
from abc import ABC, abstractmethod
from typing import Optional, Protocol
from dataclasses import dataclass


@dataclass
class Request:
    """请求对象"""
    url: str
    method: str = "GET"
    headers: dict = None
    data: bytes = None
    handled: bool = False


class RequestHandler(ABC):
    """请求处理器基类"""
    
    def __init__(self, next_handler: Optional["RequestHandler"] = None):
        self._next_handler = next_handler
    
    async def handle(self, request: Request) -> Request:
        """处理请求，返回处理后的请求"""
        # 先让下一个处理器处理
        if self._next_handler:
            request = await self._next_handler.handle(request)
        
        # 如果请求已被处理，不再处理
        if request.handled:
            return request
        
        # 子类实现具体的处理逻辑
        return await self._process(request)
    
    @abstractmethod
    async def _process(self, request: Request) -> Request:
        """具体处理逻辑"""
        pass


class URLValidationHandler(RequestHandler):
    """URL 验证处理器"""
    
    async def _process(self, request: Request) -> Request:
        """验证 URL 格式"""
        if not request.url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {request.url}")
        return request


class AuthenticationHandler(RequestHandler):
    """认证处理器"""
    
    def __init__(self, token: str, next_handler: Optional[RequestHandler] = None):
        super().__init__(next_handler)
        self._token = token
    
    async def _process(self, request: Request) -> Request:
        """添加认证头"""
        headers = dict(request.headers or {})
        headers["Authorization"] = f"Bearer {self._token}"
        request.headers = headers
        return request


class LoggingHandler(RequestHandler):
    """日志处理器"""
    
    async def _process(self, request: Request) -> Request:
        """记录请求日志"""
        print(f"[REQUEST] {request.method} {request.url}")
        return request


class CachingHandler(RequestHandler):
    """缓存处理器"""
    
    def __init__(self, cache: dict, next_handler: Optional[RequestHandler] = None):
        super().__init__(next_handler)
        self._cache = cache
    
    async def _process(self, request: Request) -> Request:
        """检查缓存"""
        if request.url in self._cache:
            print(f"[CACHE] Hit: {request.url}")
            request.data = self._cache[request.url]
            request.handled = True  # 标记为已处理，跳过后续处理器
        return request


class RequestProcessor:
    """请求处理器，管理处理器链"""
    
    def __init__(self, handler: RequestHandler):
        self._handler = handler
    
    async def process(self, request: Request) -> bytes:
        """处理请求，返回响应数据"""
        # 处理请求
        await self._handler.handle(request)
        
        # 如果未被任何处理器处理，需要发送实际请求
        if not request.handled:
            # 发送请求的逻辑
            return await self._send_request(request)
        
        # 从缓存返回数据
        return request.data
    
    async def _send_request(self, request: Request) -> bytes:
        """实际发送请求（模拟）"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                request.url,
                headers=request.headers
            ) as response:
                return await response.read()


# 使用示例
async def main():
    # 创建共享缓存
    shared_cache = {}
    
    # 构建处理器链
    handler = CachingHandler(
        shared_cache,
        LoggingHandler(
            URLValidationHandler(
                AuthenticationHandler(
                    "my-token"
                )
            )
        )
    )
    
    processor = RequestProcessor(handler)
    
    # 创建请求
    request = Request(
        url="https://api.example.com/data",
        method="GET"
    )
    
    # 处理请求
    data = await processor.process(request)
    print(f"Received {len(data)} bytes")


# 责任链的动态配置
class HandlerBuilder:
    """处理器链构建器"""
    
    def __init__(self):
        self._handlers = []
    
    def add_validation(self) -> "HandlerBuilder":
        self._handlers.append(URLValidationHandler)
        return self
    
    def add_authentication(self, token: str) -> "HandlerBuilder":
        self._handlers.append(lambda nxt: AuthenticationHandler(token, nxt))
        return self
    
    def add_logging(self) -> "HandlerBuilder":
        self._handlers.append(LoggingHandler)
        return self
    
    def add_caching(self, cache: dict) -> "HandlerBuilder":
        self._handlers.append(lambda nxt: CachingHandler(cache, nxt))
        return self
    
    def build(self) -> RequestHandler:
        """构建处理器链"""
        handler = None
        # 逆序创建链（从最后一个处理器开始）
        for handler_class in reversed(self._handlers):
            if callable(handler_class) and not issubclass(handler_class, RequestHandler):
                # 这是一个工厂函数
                continue
            handler = handler_class(handler)
        
        # 添加日志处理器（始终在最后）
        return LoggingHandler(handler) if handler else LoggingHandler(None)
```

## 1.5 工厂模式

工厂模式是一种创建型模式，它提供了一种创建对象的最佳方式，而无需指定具体类。工厂模式将对象的创建逻辑集中在一个地方，便于管理和维护。

### 1.5.1 模式变体

工厂模式有两种主要变体：简单工厂（Simple Factory）和工厂方法（Factory Method）。简单工厂使用一个工厂类根据参数创建不同类型的对象；工厂方法定义了一个创建对象的接口，但由子类决定创建哪个类的实例。

### 1.5.2 weread-exporter 中的应用

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Type


class BookExporter(ABC):
    """书籍导出器基类"""
    
    @abstractmethod
    async def export(self, book_id: str, output_path: str) -> bool:
        """执行导出"""
        pass


class EPUBExporter(BookExporter):
    """EPUB 导出器"""
    
    async def export(self, book_id: str, output_path: str) -> bool:
        # EPUB 导出逻辑
        pass


class PDFExporter(BookExporter):
    """PDF 导出器"""
    
    async def export(self, book_id: str, output_path: str) -> bool:
        # PDF 导出逻辑
        pass


# 简单工厂
class ExporterFactory:
    """导出器工厂"""
    
    _exporters: dict[str, Type[BookExporter]] = {
        "epub": EPUBExporter,
        "pdf": PDFExporter,
        "mobi": MOBIExporter,
        "txt": TXTExporter,
        "md": MarkdownExporter,
    }
    
    @classmethod
    def create(cls, format_type: str, **config) -> BookExporter:
        """根据格式类型创建导出器"""
        exporter_class = cls._exporters.get(format_type.lower())
        if exporter_class is None:
            raise ValueError(f"Unknown format: {format_type}")
        return exporter_class(**config)
    
    @classmethod
    def register(cls, format_type: str, exporter_class: Type[BookExporter]):
        """注册新的导出器"""
        cls._exporters[format_type.lower()] = exporter_class


# 使用
async def main():
    factory = ExporterFactory()
    
    # 根据配置创建导出器
    epub_exporter = factory.create("epub", custom_option=True)
    pdf_exporter = factory.create("pdf", dpi=300)
    
    await epub_exporter.export("book123", "output.epub")
    await pdf_exporter.export("book123", "output.pdf")
```

## 1.6 观察者模式

观察者模式是一种行为型模式，定义对象间的一种一对多依赖关系，当一个对象状态发生改变时，所有依赖于它的对象都会得到通知并自动更新。

### 1.6.1 模式结构与意图

观察者模式的核心思想是：「建立对象间的发布-订阅关系，当发布者状态变化时，自动通知所有订阅者」。这实现了主题与观察者的解耦，主题不需要知道具体有哪些观察者。

### 1.6.2 weread-exporter 中的应用

```python
from abc import ABC, abstractmethod
from typing import Protocol, Callable
from dataclasses import dataclass
from enum import Enum, auto
import asyncio


class EventType(Enum):
    """事件类型"""
    CHAPTER_START = auto()
    CHAPTER_COMPLETE = auto()
    CHAPTER_ERROR = auto()
    EXPORT_START = auto()
    EXPORT_COMPLETE = auto()
    EXPORT_ERROR = auto()
    PROGRESS_UPDATE = auto()


@dataclass
class ExportEvent:
    """导出事件"""
    event_type: EventType
    book_id: str
    chapter_id: str = None
    progress: float = 0.0
    message: str = ""
    error: Exception = None


class EventObserver(Protocol):
    """事件观察者协议"""
    
    async def update(self, event: ExportEvent):
        """接收事件通知"""
        pass


class ConsoleEventObserver:
    """控制台事件观察者"""
    
    async def update(self, event: ExportEvent):
        """在控制台显示事件"""
        if event.event_type == EventType.PROGRESS_UPDATE:
            print(f"\r进度: {event.progress:.1%}", end="", flush=True)
        elif event.event_type == EventType.CHAPTER_COMPLETE:
            print(f"\n章节完成: {event.chapter_id}")
        elif event.event_type == EventType.EXPORT_ERROR:
            print(f"\n错误: {event.message}")


class EventSubject:
    """事件主题，管理观察者"""
    
    def __init__(self):
        self._observers: list[EventObserver] = []
    
    def attach(self, observer: EventObserver):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: EventObserver):
        """移除观察者"""
        self._observers.remove(observer)
    
    async def notify(self, event: ExportEvent):
        """通知所有观察者"""
        await asyncio.gather(
            *[observer.update(event) for observer in self._observers]
        )


class ExportNotifier:
    """导出通知器，整合事件系统"""
    
    def __init__(self):
        self._subject = EventSubject()
        self._current_progress = 0.0
    
    def add_observer(self, observer: EventObserver):
        """添加观察者"""
        self._subject.attach(observer)
    
    async def emit(self, event_type: EventType, book_id: str, 
                  chapter_id: str = None, **kwargs):
        """发送事件"""
        progress = kwargs.get("progress", self._current_progress)
        message = kwargs.get("message", "")
        error = kwargs.get("error", None)
        
        event = ExportEvent(
            event_type=event_type,
            book_id=book_id,
            chapter_id=chapter_id,
            progress=progress,
            message=message,
            error=error
        )
        
        await self._subject.notify(event)
    
    async def emit_progress(self, book_id: str, progress: float):
        """发送进度事件"""
        self._current_progress = progress
        await self.emit(EventType.PROGRESS_UPDATE, book_id, progress=progress)


# 使用示例
async def main():
    notifier = ExportNotifier()
    
    # 添加控制台观察者
    notifier.add_observer(ConsoleEventObserver())
    
    # 添加文件日志观察者
    notifier.add_observer(FileLogObserver("export.log"))
    
    # 模拟导出过程
    await notifier.emit(EventType.EXPORT_START, "book123")
    
    for i, chapter_id in enumerate(["ch1", "ch2", "ch3"]):
        await notifier.emit(EventType.CHAPTER_START, "book123", chapter_id)
        # ... 处理章节
        progress = (i + 1) / 3
        await notifier.emit_progress("book123", progress)
        await notifier.emit(EventType.CHAPTER_COMPLETE, "book123", chapter_id)
    
    await notifier.emit(EventType.EXPORT_COMPLETE, "book123")
```

## 1.7 模式组合应用

实际项目中，通常需要组合使用多种设计模式来解决复杂问题。本节将展示如何在 weread-exporter 中组合应用这些模式。

### 1.7.1 完整架构示例

```python
# 组合多种设计模式的完整示例

from abc import ABC, abstractmethod
from typing import Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import asyncio


# ===== 1. 策略模式：定义转换策略 =====
class ConversionStrategy(ABC):
    @abstractmethod
    async def convert(self, content: str, output_path: str) -> bool:
        pass


# ===== 2. 模板方法模式：定义处理流程 =====
class ContentProcessor:
    """内容处理器，使用模板方法"""
    
    def __init__(self, strategy: ConversionStrategy):
        self._strategy = strategy
    
    async def process(
        self, 
        content: str, 
        output_path: str,
        before_process: callable = None,
        after_process: callable = None
    ) -> bool:
        # 模板方法：定义处理流程
        
        # 步骤 1：预处理
        processed = content
        if before_process:
            processed = await before_process(processed)
        
        # 步骤 2：执行转换
        result = await self._strategy.convert(processed, output_path)
        
        # 步骤 3：后处理
        if after_process:
            await after_process(output_path)
        
        return result


# ===== 3. 责任链模式：处理请求 =====
class Processor(ABC):
    def __init__(self, next_handler: Optional["Processor"] = None):
        self._next_handler = next_handler
    
    async def handle(self, request: dict) -> dict:
        if self._next_handler:
            return await self._next_handler.handle(request)
        return request
    
    @abstractmethod
    async def _process(self, request: dict) -> dict:
        pass


# ===== 4. 观察者模式：进度通知 =====
class ProgressSubject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    async def notify(self, progress: float, status: str):
        for observer in self._observers:
            await observer.update(progress, status)


# ===== 5. 工厂模式：创建处理器 =====
class ProcessorFactory:
    _processors = {}
    
    @classmethod
    def create(cls, processor_type: str, **config):
        processor_class = cls._processors.get(processor_type)
        if processor_class:
            return processor_class(**config)
        raise ValueError(f"Unknown processor type: {processor_type}")
    
    @classmethod
    def register(cls, processor_type: str, processor_class):
        cls._processors[processor_type] = processor_class


# 注册处理器
ProcessorFactory.register("markdown", MarkdownProcessor)
ProcessorFactory.register("html", HTMLProcessor)
ProcessorFactory.register("pdf", PDFProcessor)


# 使用
async def main():
    # 创建观察者
    subject = ProgressSubject()
    subject.attach(ConsoleProgressObserver())
    subject.attach(FileProgressObserver("progress.log"))
    
    # 创建处理器
    processor = ProcessorFactory.create(
        "markdown",
        strategy=EPUBConversionStrategy()
    )
    
    # 执行处理
    await processor.process(content, output_path)
```

## 1.8 本章小结

本章深入介绍了 weread-exporter 中使用的六种核心设计模式：模板方法模式、策略模式、装饰器模式、责任链模式、工厂模式和观察者模式。每种模式都有其独特的应用场景和实现技巧，理解这些模式将帮助你写出更加优雅、可维护的代码。

完成本章节学习后，建议继续学习进阶路径的下一级「深度技术分析」，了解项目中关键技术的实现原理。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 模板方法 | Template Method | 在抽象类中定义算法骨架的设计模式 |
| 策略 | Strategy | 将算法封装为可互换对象的设计模式 |
| 装饰器 | Decorator | 动态添加职责的设计模式 |
| 责任链 | Chain of Responsibility | 让多个对象处理请求的设计模式 |
| 工厂 | Factory | 封装对象创建逻辑的设计模式 |
| 观察者 | Observer | 实现发布-订阅的设计模式 |
| 开闭原则 | Open/Closed Principle | 软件实体应对扩展开放，对修改关闭 |
