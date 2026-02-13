# 深度技术分析

> 本文档是进阶路径的第三篇，面向希望深入理解 weread-exporter 底层技术实现的资深开发者。通过阅读本文档，你将全面掌握 Canvas Hook 技术的工作原理、浏览器自动化的核心技术、异步 I/O 的实现细节，以及各种边界情况的处理方法。这些深度技术知识将帮助你理解系统的工作原理，并为进行高级定制和优化奠定基础。

## 学习目标

完成本章节学习后，你将能够深入理解 weread-exporter 的核心技术实现，包括 Canvas Hook 的注入机制、浏览器自动化的核心技术、异步编程的最佳实践，以及性能和稳定性优化技巧。此外，你还将具备诊断和解决复杂技术问题的能力。

### 基础目标

首先，你将掌握 Canvas Hook 技术的工作原理，理解如何拦截 Canvas 渲染过程并提取原始内容。其次，你将理解 Pyppeteer 的核心机制，包括 Chrome DevTools Protocol 的交互方式、页面生命周期管理等。第三，你将深入理解 Python 异步编程的实现细节，包括事件循环、协程调度、异步上下文管理等。

### 进阶目标

进阶目标要求你能够设计和实现类似的技术方案，为其他应用场景定制 Canvas Hook 或浏览器自动化脚本。你还将具备深度优化系统性能的能力，能够分析性能瓶颈并采取有效的优化措施。此外，你将能够诊断复杂的技术问题，从根本上理解问题的成因并提供解决方案。

## 1.1 Canvas Hook 技术深度解析

Canvas Hook 是 weread-exporter 能够突破内容保护、获取原始渲染内容的关键技术。本节将深入分析 Canvas Hook 的工作原理、实现细节，以及各种边界情况的处理。

### 1.1.1 Canvas 渲染原理概述

理解 Canvas Hook 之前，需要先了解 Canvas 渲染的基本原理。HTML5 Canvas 是一个位图画布，允许 JavaScript 通过 2D 或 WebGL 上下文绘制图形。当网页调用 Canvas API（如 `fillText`、`drawImage` 等）时，浏览器会在画布上绘制相应的像素。

微信读书将书籍内容渲染到 Canvas 上，而不是使用传统的 HTML 元素。这种方式使得传统的网页爬取方法无法直接获取内容，因为 HTML 源代码中只包含 Canvas 元素，没有实际的内容数据。

微信读书的内容渲染流程大致如下：首先，JavaScript 从服务器获取书籍内容数据；然后，将文本内容转换为渲染命令（如设置字体、绘制位置）；最后，通过 Canvas API 将内容绘制到画布上。

### 1.1.2 Canvas Hook 实现原理

Canvas Hook 的核心思想是拦截 Canvas 相关的 API，在内容被绘制之前记录原始数据。通过分析绘制命令的调用参数，可以重建完整的渲染内容。

```javascript
// hook.js - Canvas Hook 注入脚本

// 保存原始的 CanvasRenderingContext2D 方法
const originalProto = CanvasRenderingContext2D.prototype;

// 存储绘制的操作记录
window.__canvasContent = {
    operations: [],  // 记录所有绘制操作
    texts: [],       // 提取的文本内容
    images: [],      // 提取的图片引用
    metadata: {}     // 元数据（尺寸、字体等）
};

// 拦截 fillText 方法
const originalFillText = originalProto.fillText;
originalProto.fillText = function(text, x, y, maxWidth) {
    // 记录文本绘制信息
    window.__canvasContent.operations.push({
        type: 'text',
        args: Array.from(arguments),
        timestamp: Date.now()
    });
    
    // 提取文本内容（用于后续内容重建）
    if (typeof text === 'string' && text.trim()) {
        window.__canvasContent.texts.push({
            content: text,
            x: x,
            y: y,
            font: this.font,
            fillStyle: this.fillStyle
        });
    }
    
    // 调用原始方法
    return originalFillText.apply(this, arguments);
};

// 拦截 drawImage 方法
const originalDrawImage = originalProto.drawImage;
originalProto.drawImage = function(image, ...args) {
    // 记录图片绘制信息
    window.__canvasContent.operations.push({
        type: 'image',
        args: [image.src || String(image), ...args],
        timestamp: Date.now()
    });
    
    // 提取图片引用
    if (image.src) {
        const src = image.src.toString();
        if (src && !src.startsWith('data:')) {
            window.__canvasContent.images.push({
                src: src,
                args: args
            });
        }
    }
    
    // 调用原始方法
    return originalDrawImage.apply(this, arguments);
};

// 拦截 strokeText 方法
const originalStrokeText = originalProto.strokeText;
originalProto.strokeText = function(text, x, y, maxWidth) {
    window.__canvasContent.operations.push({
        type: 'strokeText',
        args: Array.from(arguments),
        timestamp: Date.now()
    });
    
    return originalStrokeText.apply(this, arguments);
};

// 拦截 rect 方法
const originalRect = originalProto.rect;
originalProto.rect = function(x, y, width, height) {
    window.__canvasContent.operations.push({
        type: 'rect',
        args: [x, y, width, height],
        timestamp: Date.now()
    });
    
    return originalRect.apply(this, arguments);
};

// 拦截 fillRect 方法
const originalFillRect = originalProto.fillRect;
originalProto.fillRect = function(x, y, width, height) {
    window.__canvasContent.operations.push({
        type: 'fillRect',
        args: [x, y, width, height],
        timestamp: Date.now()
    });
    
    return originalFillRect.apply(this, arguments);
};

// 保存测量文本尺寸的方法
const originalMeasureText = originalProto.measureText;
originalProto.measureText = function(text) {
    // 可以在这里记录文本尺寸信息
    return originalMeasureText.apply(this, arguments);
};
```

### 1.1.3 内容提取与重建

记录了 Canvas 操作后，需要将这些操作转换为可读的文本内容。以下是内容提取和重建的逻辑：

```javascript
// 从记录的绘制操作中提取 Markdown 内容

window.__canvasExtractor = {
    // 提取所有文本内容
    extractTexts: function() {
        const texts = window.__canvasContent.texts;
        
        // 按 Y 坐标排序（模拟阅读顺序）
        const sortedTexts = texts.sort((a, b) => {
            // 首先按行分组（在一定 Y 范围内视为同一行）
            const rowThreshold = 10; // 10 像素内的视为同一行
            if (Math.abs(a.y - b.y) > rowThreshold) {
                return a.y - b.y; // 不同行，按 Y 坐标排序
            }
            return a.x - b.x; // 同一行，按 X 坐标排序
        });
        
        // 按行分组
        const lines = [];
        let currentLine = [];
        let currentY = null;
        const yThreshold = 8;
        
        for (const text of sortedTexts) {
            if (currentY === null || Math.abs(text.y - currentY) > yThreshold) {
                if (currentLine.length > 0) {
                    lines.push(currentLine);
                }
                currentLine = [text];
                currentY = text.y;
            } else {
                currentLine.push(text);
            }
        }
        if (currentLine.length > 0) {
            lines.push(currentLine);
        }
        
        // 合并同一行的文本
        return lines.map(line => {
            // 按 X 坐标排序
            line.sort((a, b) => a.x - b.x);
            // 合并相邻的文本
            let merged = '';
            for (const text of line) {
                merged += text.content;
            }
            return merged;
        }).join('\n\n');
    },
    
    // 提取所有图片引用
    extractImages: function() {
        const images = [];
        for (const img of window.__canvasContent.images) {
            images.push(img.src);
        }
        return images;
    },
    
    // 生成 Markdown 格式
    generateMarkdown: function() {
        const texts = this.extractTexts();
        const images = this.extractImages();
        
        // 构建 Markdown
        let markdown = texts;
        
        // 插入图片引用
        let imageIndex = 0;
        markdown = markdown.replace(/\[图片\]/g, () => {
            if (imageIndex < images.length) {
                return `![图片](${images[imageIndex++]})`;
            }
            return '[图片]';
        });
        
        return markdown;
    }
};
```

### 1.1.4 高级 Hook 技术

除了基本的 API 拦截，weread-exporter 还使用了更多高级技术来确保内容提取的完整性：

```javascript
// 高级 Hook 技术示例

// 1. 拦截 WebGL 上下文（如果有的话）
const originalGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, ...args) {
    const context = originalGetContext.apply(this, [type, ...args]);
    
    if (type === 'webgl' || type === 'experimental-webgl') {
        // WebGL 上下文 Hook
        this.__webglContent = {
            programs: [],
            textures: [],
            buffers: []
        };
        
        // 拦截 shader 相关操作
        const originalShaderSource = context.shaderSource;
        context.shaderSource = function(shader, source) {
            this.__webglContent.shaders = this.__webglContent.shaders || [];
            this.__webglContent.shaders.push(source);
            return originalShaderSource.apply(this, arguments);
        };
    }
    
    return context;
};

// 2. 拦截 ImageData 操作（用于精确像素内容）
const originalPutImageData = originalProto.putImageData;
originalProto.putImageData = function(imageData, dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight) {
    // 记录 ImageData 的内容
    window.__canvasContent = window.__canvasContent || {};
    window.__canvasContent.imageDataOperations = window.__canvasContent.imageDataOperations || [];
    window.__canvasContent.imageDataOperations.push({
        type: 'putImageData',
        data: Array.from(imageData.data),  // 保存像素数据
        dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight,
        width: imageData.width,
        height: imageData.height
    });
    
    return originalPutImageData.apply(this, arguments);
};

// 3. 拦截 requestAnimationFrame（用于捕获动画内容）
const originalRequestAnimationFrame = window.requestAnimationFrame;
window.requestAnimationFrame = function(callback) {
    return originalRequestAnimationFrame.call(window, (timestamp) => {
        // 在动画帧回调中检查是否有新内容
        if (window.__canvasContent.operations && 
            window.__canvasContent.operations.length > 0) {
            // 有新内容，可以触发更新
            callback(timestamp);
        }
    });
};

// 4. 拦截 MutationObserver（监控 DOM 变化）
const originalObserve = MutationObserver.prototype.observe;
MutationObserver.prototype.observe = function(target, config) {
    // 可以记录 DOM 变化，辅助内容重建
    console.log('Canvas element observed:', target);
    return originalObserve.apply(this, arguments);
};

// 5. 拦截字体加载（确保文本内容完整）
document.fonts.ready.then(() => {
    // 所有字体已加载完成，可以提取最终内容
    window.__canvasContent.fontReady = true;
    window.__canvasContent.allFonts = Array.from(document.fonts.entries()).map(
        ([key, value]) => value.family
    );
});
```

## 1.2 Pyppeteer 核心机制解析

Pyppeteer 是 weread-exporter 控制 Chrome 浏览器的核心库。本节将深入分析 Pyppeteer 的实现原理，包括 Chrome DevTools Protocol 交互、页面生命周期管理、请求拦截机制等。

### 1.2.1 Chrome DevTools Protocol 概述

Chrome DevTools Protocol（CDP）是 Chrome 浏览器提供的调试协议，允许外部程序与浏览器进行通信。通过 CDP，可以执行 JavaScript、操作 DOM、拦截网络请求、获取性能数据等。

CDP 基于 JSON-RPC 协议，使用 WebSocket 进行双向通信。客户端发送请求到浏览器，浏览器执行相应操作后返回结果。CDP 支持多种域（Domain），每个域包含多个命令（Command）和事件（Event）。

weread-exporter 主要使用以下 CDP 域：`Page` 域用于页面导航、生命周期管理；`Runtime` 域用于 JavaScript 执行；`Network` 域用于网络请求拦截；`DOM` 域用于 DOM 操作；`Log` 域用于日志捕获。

### 1.2.2 Pyppeteer 架构分析

Pyppeteer 是 Puppeteer 的 Python 移植版，其架构设计如下：

```python
# Pyppeteer 核心架构分析

class Browser:
    """浏览器实例"""
    def __init__(self, options):
        self._connection = None  # 与浏览器的 WebSocket 连接
        self._targets = {}      # 目标（页面、Service Worker 等）
        self._default_page = None
    
    async def create(self, options):
        # 1. 启动 Chrome 进程
        self._process = await asyncio.create_subprocess_exec(
            *self._get_chrome_args(options),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 2. 建立 WebSocket 连接
        ws_url = await self._get_ws_url()
        self._connection = await websocket_connect(ws_url)
        
        # 3. 创建消息循环
        asyncio.create_task(self._message_loop())
        
        # 4. 获取页面目标
        await self._init_targets()
    
    async def _message_loop(self):
        """消息循环，处理来自浏览器的消息"""
        while True:
            message = await self._connection.recv()
            data = json.loads(message)
            
            if data["method"] == "Target.targetCreated":
                # 新目标创建
                target_id = data["params"]["targetInfo"]["targetId"]
                self._targets[target_id] = data["params"]["targetInfo"]
            
            elif data["method"] == "Log.entryAdded":
                # 日志条目
                self._handle_log(data["params"])
            
            # 处理其他消息...
    
    async def newPage(self):
        """创建新页面"""
        # 发送 CDP 命令
        response = await self._send_command("Target.createTarget", {
            "url": "about:blank"
        })
        target_id = response["result"]["targetId"]
        
        # 获取页面
        page = Page(self._connection, target_id)
        await page.init()
        
        return page


class Page:
    """页面实例"""
    def __init__(self, connection, target_id):
        self._connection = connection
        self._target_id = target_id
        self._execution_context_id = None
        self._document = None
    
    async def init(self):
        # 获取页面的执行上下文
        response = await self._send_command("Runtime.enable")
        self._execution_context_id = response["result"]["contextId"]
        
        # 启用页面相关域
        await self._send_command("Page.enable")
        await self._send_command("Network.enable")
    
    async def evaluate(self, js):
        """执行 JavaScript"""
        response = await self._send_command("Runtime.evaluate", {
            "expression": js,
            "contextId": self._execution_context_id
        })
        return response["result"]
    
    async def goto(self, url):
        """导航到 URL"""
        response = await self._send_command("Page.navigate", {
            "url": url
        })
        # 等待页面加载完成
        await self.wait_for_load()
    
    async def setContent(self, html):
        """设置页面内容"""
        await self._send_command("Page.setDocumentContent", {
            "html": html
        })
    
    async def screenshot(self, options=None):
        """截屏"""
        response = await self._send_command("Page.captureScreenshot")
        return base64.b64decode(response["result"]["data"])
```

### 1.2.3 请求拦截机制

weread-exporter 使用请求拦截来实现 Canvas Hook 注入和 API 模拟：

```python
# 请求拦截实现分析

class WeReadWebPage:
    async def pre_load_page(self):
        """启用请求拦截"""
        # 1. 启用请求拦截
        await self._page.setRequestInterception(True)
        
        # 2. 设置请求处理回调
        self._page.on("request", self._handle_request)
    
    async def _handle_request(self, request):
        """处理拦截到的请求"""
        url = request.url
        
        # 2.1 注入 Canvas Hook
        if "/web/1.392ec47a.js" in url:
            # 读取 hook.js 内容
            with open("hook.js", "rb") as f:
                hook_script = f.read()
            
            # 返回自定义响应
            response = {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": hook_script,
            }
            return await request.respond(response)
        
        # 2.2 模拟 API 响应
        if "/web/book/read" in url:
            # 生成模拟响应
            body = b'{"succ":1,"synckey":%d}' % random.randint(10000000, 100000000)
            response = {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": body,
            }
            return await request.respond(response)
        
        # 2.3 静默处理日志请求
        if "/hera/logkv" in url or "/hera/osslog" in url:
            return {
                "status": 204,  # No Content
            }
        
        # 2.4 其他请求继续正常处理
        await request.continue_()
```

### 1.2.4 页面生命周期管理

理解页面生命周期对于正确处理内容提取至关重要：

```python
# 页面生命周期管理

class WeReadWebPage:
    async def goto_chapter(self, chapter_id, timeout=120):
        """导航到章节页面"""
        url = self._get_chapter_url(chapter_id)
        
        # 1. 开始导航
        await self._page.goto(url, timeout=1000 * timeout)
        
        # 2. 等待页面加载
        try:
            await self._page.waitForSelector(
                "canvas",
                timeout=30 * 1000
            )
        except pyppeteer.errors.TimeoutError:
            raise LoadChapterFailedError("Canvas not found")
        
        # 3. 等待内容渲染完成
        await self._wait_for_content()
        
        # 4. 检查是否需要下一页
        await self._check_next_page()
    
    async def _wait_for_content(self):
        """等待 Canvas 内容渲染完成"""
        # 方法 1：检查 Canvas 数据
        content_complete = False
        for _ in range(10):  # 最多等待 10 秒
            result = await self._page.evaluate("""
                () => {
                    return window.canvasContentHandler && 
                           window.canvasContentHandler.data &&
                           window.canvasContentHandler.data.complete;
                }
            """)
            if result:
                content_complete = True
                break
            await asyncio.sleep(1)
        
        if not content_complete:
            raise RuntimeError("Content rendering timeout")
    
    async def _check_next_page(self):
        """检查并处理分页"""
        try:
            await self._page.waitForSelector(
                "button.readerFooter_button",
                timeout=60 * 1000
            )
        except pyppeteer.errors.TimeoutError:
            return  # 没有分页按钮，可能是最后一页
        
        # 获取按钮文字
        button_text = await self._page.evaluate("""
            () => {
                const btn = document.querySelector('button.readerFooter_button');
                return btn ? btn.innerText : '';
            }
        """)
        
        if button_text == "下一页":
            # 点击下一页
            await self._page.click("button.readerFooter_button")
            await asyncio.sleep(1)  # 等待页面加载
            await self._wait_for_content()  # 等待内容渲染
    
    async def get_markdown(self):
        """提取 Markdown 内容"""
        return await self._page.evaluate("""
            () => {
                if (window.canvasContentHandler && 
                    window.canvasContentHandler.data &&
                    window.canvasContentHandler.data.markdown) {
                    return window.canvasContentHandler.data.markdown;
                }
                return null;
            }
        """)
```

## 1.3 异步编程深度分析

weread-exporter 使用 Python 的 asyncio 库实现异步编程。本节将深入分析异步编程的关键技术，包括事件循环、协程调度、异步上下文管理等。

### 1.3.1 事件循环机制

事件循环是异步编程的核心：

```python
# 事件循环机制深度分析

class CustomEventLoop(asyncio.AbstractEventLoop):
    """自定义事件循环示例"""
    
    def __init__(self):
        self._running = False
        self._ready = collections.deque()  # 准备运行的协程
        self._scheduled = []  # 定时任务
        self._selector = selectors.DefaultSelector()
    
    def run_until_complete(self, future):
        """运行直到完成"""
        self._running = True
        
        try:
            while not future.done():
                # 1. 运行准备好的协程
                while self._ready:
                    coro = self._ready.popleft()
                    try:
                        coro.send(None)
                    except StopIteration as e:
                        # 协程完成
                        result = e.value
                        if isinstance(result, asyncio.Future):
                            # 如果结果是 Future，设置结果
                            result.set_result(None)
                    except Exception as e:
                        # 协程出错
                        if hasattr(coro, '_exception'):
                            coro._exception = e
                
                # 2. 处理 I/O 就绪事件
                events = self._selector.select(timeout=0.1)
                for key, mask in events:
                    callback = key.data
                    callback(key, mask)
                
                # 3. 执行定时任务
                now = self.time()
                while self._scheduled and self._scheduled[0][0] <= now:
                    _, callback, args = heapq.heappop(self._scheduled)
                    self._ready.append(callback(*args))
            
        finally:
            self._running = False
    
    def create_task(self, coro):
        """创建任务"""
        task = asyncio.Task(coro, loop=self)
        return task
    
    def call_later(self, delay, callback, *args):
        """安排延迟回调"""
        when = self.time() + delay
        heapq.heappush(self._scheduled, (when, callback, args))
        return handle  # 返回句柄，可用于取消
```

### 1.3.2 协程调度原理

协程的调度是由事件循环控制的：

```python
# 协程调度原理

async def my_coroutine():
    """示例协程"""
    print("Step 1")
    await asyncio.sleep(1)  # 让出控制权
    print("Step 2")


# 等价的状态机转换

class MyCoroutine:
    """协程编译后的状态机"""
    
    def __init__(self):
        self._state = 0  # 初始状态
    
    def send(self, value):
        """发送值到协程"""
        if self._state == 0:
            print("Step 1")
            self._state = 1
            # 返回一个 Future，表示需要等待
            future = asyncio.Future()
            
            def sleep_done(f):
                # 睡眠完成后恢复协程
                self.send(None)
            
            asyncio.get_event_loop().call_later(
                1, lambda: future.set_result(None)
            )
            return future
        
        elif self._state == 1:
            print("Step 2")
            raise StopIteration()  # 协程完成
```

### 1.3.3 异步上下文管理

异步上下文管理器用于处理异步资源的获取和释放：

```python
# 异步上下文管理器

import asyncio
from contextlib import asynccontextmanager


class BrowserPool:
    """浏览器连接池"""
    
    def __init__(self, max_size=5):
        self._pool = asyncio.Queue(max_size)
        self._max_size = max_size
    
    async def get(self):
        """获取浏览器连接"""
        if self._pool.empty():
            # 创建新连接
            browser = await self._create_browser()
            return browser
        return await self._pool.get()
    
    async def release(self, browser):
        """释放浏览器连接"""
        await self._pool.put(browser)
    
    async def _create_browser(self):
        """创建新浏览器"""
        # 实现创建逻辑
        pass


@asynccontextmanager
async def use_browser(pool):
    """浏览器上下文管理器"""
    browser = await pool.get()
    try:
        yield browser
    finally:
        await pool.release(browser)


# 使用示例
async def main():
    pool = BrowserPool(max_size=5)
    
    async with use_browser(pool) as browser:
        await browser.goto("https://weread.qq.com")
        # ... 使用浏览器
    # 自动释放回池中
```

## 1.4 性能优化技术

weread-exporter 的性能优化涉及多个层面：网络请求、并发处理、内存管理、缓存策略等。本节将详细分析这些优化技术。

### 1.4.1 并发控制

```python
# 并发控制实现

import asyncio
from asyncio import Semaphore
from typing import List
import time


class ConcurrencyController:
    """并发控制器"""
    
    def __init__(self, max_concurrent: int = 3, timeout: float = 30.0):
        self._semaphore = Semaphore(max_concurrent)
        self._timeout = timeout
        self._active_count = 0
        self._total_executed = 0
        self._total_time = 0.0
    
    async def execute(self, coro):
        """执行协程，带并发控制"""
        async with self._semaphore:
            start = time.time()
            try:
                result = await asyncio.wait_for(
                    coro,
                    timeout=self._timeout
                )
                self._total_executed += 1
                self._total_time += time.time() - start
                return result
            except asyncio.TimeoutError:
                raise TimeoutError(f"Task timeout after {self._timeout}s")
            except Exception as e:
                raise
    
    async def execute_all(self, coros: List[coro]) -> List[result]:
        """并发执行所有协程"""
        tasks = [self.execute(coro) for coro in coros]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        avg_time = self._total_time / self._total_executed if self._total_executed > 0 else 0
        return {
            "active": self._active_count,
            "total_executed": self._total_executed,
            "average_time": avg_time,
            "available": self._semaphore._value,
        }


# 使用示例
controller = ConcurrencyController(max_concurrent=3, timeout=60)

async def fetch_chapter(chapter_id: str) -> str:
    """获取单个章节"""
    await controller.execute(fetch_single_chapter(chapter_id))


async def fetch_all_chapters(book_id: str, chapter_ids: List[str]):
    """并行获取所有章节"""
    coros = [fetch_chapter(cid) for cid in chapter_ids]
    results = await controller.execute_all(coros)
    return results
```

### 1.4.2 内存优化

```python
# 内存优化技术

import asyncio
import gc
from typing import AsyncGenerator


class MemoryOptimizedProcessor:
    """内存优化的处理器"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB
        self._chunk_size = chunk_size
        self._large_objects = []
    
    async def process_large_data(self, data_generator: AsyncGenerator[bytes]):
        """流式处理大数据，避免一次性加载"""
        buffer = b""
        async for chunk in data_generator:
            buffer += chunk
            
            # 当缓冲区达到阈值时处理
            while len(buffer) >= self._chunk_size:
                # 处理完整块
                chunk_to_process = buffer[:self._chunk_size]
                buffer = buffer[self._chunk_size:]
                await self._process_chunk(chunk_to_process)
        
        # 处理剩余数据
        if buffer:
            await self._process_chunk(buffer)
    
    async def _process_chunk(self, chunk: bytes):
        """处理数据块"""
        # 处理逻辑
        pass
    
    async def cleanup_large_objects(self):
       大对象"""
        self._large_objects.clear """清理()
        gc.collect()  # 强制垃圾回收
    
    async def batched_iteration(self, items: List, batch_size: int = 100):
        """分批迭代，避免内存峰值"""
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            yield batch
            # 每批处理后强制垃圾回收
            gc.collect()


# 使用流式处理避免内存峰值
async def process_book_streaming(book_id: str):
    """流式处理书籍，避免内存问题"""
    processor = MemoryOptimizedProcessor()
    
    async def chapter_generator():
        """章节生成器"""
        for chapter_id in await get_chapter_ids(book_id):
            chapter_data = await fetch_chapter_data(chapter_id)
            yield chapter_data
    
    await processor.process_large_data(chapter_generator())
```

### 1.4.3 缓存策略

```python
# 高级缓存策略

import asyncio
import hashlib
import pickle
from typing import Any, Optional
from pathlib import Path
import json
import time


class CacheManager:
    """高级缓存管理器"""
    
    def __init__(self, cache_dir: str = "./cache", 
                 max_size_mb: int = 1024,
                 ttl_seconds: int = 86400):  # 24小时
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_size = max_size_mb * 1024 * 1024
        self._ttl = ttl_seconds
        self._memory_cache = {}
        self._memory_cache_size = 0
        self._max_memory_size = 100 * 1024 * 1024  # 100MB
    
    def _get_cache_path(self, key: str) -> Path:
        """生成缓存文件路径"""
        key_hash = hashlib.md5(key.encode()).hexdigest()[:16]
        return self._cache_dir / f"{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 1. 检查内存缓存
        if key in self._memory_cache:
            cached = self._memory_cache[key]
            if time.time() - cached["time"] < self._ttl:
                return cached["data"]
            del self._memory_cache[key]
        
        # 2. 检查磁盘缓存
        path = self._get_cache_path(key)
        if path.exists():
            mtime = path.stat().st_mtime
            if time.time() - mtime < self._ttl:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                # 恢复内存缓存
                await self._add_to_memory(key, data)
                return data
            else:
                path.unlink()  # 过期缓存
        
        return None
    
    async def set(self, key: str, data: Any):
        """设置缓存"""
        # 1. 添加内存缓存
        await self._add_to_memory(key, data)
        
        # 2. 添加磁盘缓存
        path = self._get_cache_path(key)
        with open(path, "wb") as f:
            pickle.dump(data, f)
        
        # 3. 清理过期和超量缓存
        await self._cleanup()
    
    async def _add_to_memory(self, key: str, data: Any):
        """添加到内存缓存"""
        import sys
        data_size = sys.getsizeof(pickle.dumps(data))
        
        # 如果超出内存限制，清理最旧的缓存
        while self._memory_cache_size + data_size > self._max_memory_size:
            if not self._memory_cache:
                break
            oldest_key = next(iter(self._memory_cache))
            self._memory_cache_size -= sys.getsizeof(
                pickle.dumps(self._memory_cache[oldest_key]["data"])
            del self._memory_cache[oldest_key]
        
        self._memory_cache[key] = {
            "data": data,
            "time": time.time()
        }
        self._memory_cache_size += data_size
    
    async def cleanup(self):
        """清理缓存"""
        # 清理过期缓存
        now = time.time()
        for path in self._cache_dir.glob("*.cache"):
            try:
                if now - path.stat().st_mtime > self._ttl:
                    path.unlink()
            except OSError:
                pass
        
        # 清理超量缓存
        total_size = sum(p.stat().st_size for p in self._cache_dir.glob("*.cache"))
        if total_size > self._max_size:
            # 删除最旧的缓存
            for path in sorted(
                self._cache_dir.glob("*.cache"),
                key=lambda p: p.stat().st_mtime
            ):
                if total_size <= self._max_size * 0.8:
                    break
                total_size -= path.stat().st_size
                path.unlink()
```

## 1.5 本章小结

本章深入分析了 weread-exporter 的核心技术实现，包括 Canvas Hook 技术原理、Pyppeteer 核心机制、异步编程深度分析，以及性能优化技术。理解这些底层技术将帮助你从根本上把握系统的工作原理，并为进行高级定制和优化奠定基础。

完成本章节学习后，建议继续学习进阶路径的最后一级「架构决策与最佳实践」，了解项目的设计权衡和最佳实践总结。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| Canvas Hook | Canvas Hook | 拦截 Canvas 渲染 API 以提取内容的技术 |
| CDP | Chrome DevTools Protocol | Chrome 浏览器的调试协议 |
| Pyppeteer | Pyppeteer | Python 实现的浏览器自动化库 |
| 事件循环 | Event Loop | 管理异步任务执行的循环机制 |
| 协程 | Coroutine | 可以暂停和恢复执行的异步函数 |
| WebSocket | WebSocket | 浏览器与服务器之间的双向通信协议 |
| 请求拦截 | Request Interception | 拦截并修改 HTTP 请求的技术 |
