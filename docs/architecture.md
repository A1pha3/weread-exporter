# 架构解析

## 系统架构概述

微信读书导出工具采用模块化设计，核心架构基于异步事件驱动模型。整个系统分为四个主要层次：命令行接口层、业务逻辑层、浏览器控制层和格式转换层。

### 架构层次图

```
┌─────────────────────────────────────────────────────────────┐
│                   命令行接口层 (CLI Layer)                   │
├─────────────────────────────────────────────────────────────┤
│ 参数解析 │ 配置管理 │ 日志记录 │ 错误处理 │ 用户交互          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   业务逻辑层 (Business Layer)               │
├─────────────────────────────────────────────────────────────┤
│ 导出流程控制 │ 章节管理 │ 缓存管理 │ 状态管理 │ 质量控制      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  浏览器控制层 (Browser Layer)               │
├─────────────────────────────────────────────────────────────┤
│ 页面导航 │ Canvas Hook │ 内容拦截 │ 登录管理 │ 反检测机制    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   格式转换层 (Format Layer)                  │
├─────────────────────────────────────────────────────────────┤
│ Markdown处理 │ EPUB生成 │ PDF渲染 │ MOBI转换 │ 样式应用      │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块详解

### 1. 命令行接口模块 (`__main__.py`)

#### 功能职责
- 命令行参数解析和验证
- 配置文件的加载和管理
- 日志系统的初始化和配置
- 错误处理和用户友好的错误信息展示
- 异步事件循环的管理

#### 关键代码结构

```python
class CommandLineInterface:
    def __init__(self):
        self.parser = self._create_parser()
        self.config = self._load_config()
    
    def _create_parser(self):
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog="weread-exporter",
            description="微信读书书籍导出工具"
        )
        
        # 必需参数
        parser.add_argument("-b", "--book-id", required=True,
                           help="书籍ID")
        
        # 可选参数
        parser.add_argument("-o", "--output-format", 
                           action="append", choices=["epub", "pdf", "mobi"])
        
        return parser
    
    async def run(self):
        """主运行逻辑"""
        try:
            # 参数验证
            self._validate_args()
            
            # 创建导出器实例
            exporter = WeReadExporter(self.args.book_id)
            
            # 执行导出流程
            await exporter.export()
            
        except Exception as e:
            self._handle_error(e)
```

#### 设计模式应用
- **命令模式**: 封装导出操作的具体实现
- **工厂模式**: 根据参数创建不同的导出器实例
- **策略模式**: 支持多种输出格式的灵活切换

### 2. 网页控制模块 (`webpage.py`)

#### 功能职责
- 浏览器实例的生命周期管理
- 页面导航和内容加载控制
- Canvas Hook脚本的注入和执行
- 网络请求的拦截和模拟
- 反检测机制的实现

#### 核心实现原理

```python
class WeReadWebPage:
    def __init__(self, book_id):
        self.book_id = book_id
        self.browser = None
        self.page = None
        self.hook_script = self._load_hook_script()
    
    async def launch(self, headless=False):
        """启动浏览器并配置反检测机制"""
        # 浏览器启动参数
        launch_args = [
            "--no-first-run",
            "--remote-allow-origins=*",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor"
        ]
        
        if headless:
            launch_args.append("--headless")
        
        self.browser = await pyppeteer.launch({
            'args': launch_args,
            'headless': headless
        })
        
        self.page = await self.browser.newPage()
        
        # 设置反检测机制
        await self._setup_anti_detection()
        
        # 注入Hook脚本
        await self._inject_hook_script()
    
    async def _setup_anti_detection(self):
        """配置反检测机制"""
        # 隐藏webdriver属性
        await self.page.evaluateOnNewDocument('''
            () => {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                
                // 修改插件列表
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                })
                
                // 修改语言设置
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                })
            }
        ''')
        
        # 设置用户代理
        await self.page.setUserAgent(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
```

#### 网络请求拦截机制

```python
async def _setup_request_interception(self):
    """设置请求拦截"""
    await self.page.setRequestInterception(True)
    
    async def intercept_request(request):
        # 拦截Canvas相关脚本
        if "/web/1.392ec47a.js" in request.url:
            await request.respond({
                'status': 200,
                'contentType': 'application/javascript',
                'body': self.hook_script
            })
            return
        
        # 拦截API请求并模拟响应
        if "/web/book/read" in request.url:
            await request.respond({
                'status': 200,
                'contentType': 'application/json',
                'body': '{"succ":1,"synckey":12345678}'
            })
            return
        
        # 允许其他请求继续
        await request.continue_()
    
    self.page.on('request', intercept_request)
```

### 3. Canvas Hook模块 (`hook.js`)

#### 技术原理

Canvas Hook是项目的核心技术，通过JavaScript Proxy对象拦截Canvas的绘制操作：

```javascript
// 拦截Canvas的getContext方法
const originalGetContext = HTMLCanvasElement.prototype.getContext;

HTMLCanvasElement.prototype.getContext = function(type, options) {
    const ctx = originalGetContext.call(this, type, options);
    
    if (type === '2d') {
        // 创建代理拦截Canvas操作
        return new Proxy(ctx, {
            get(target, property) {
                const value = target[property];
                
                if (typeof value === 'function') {
                    // 拦截方法调用
                    return function(...args) {
                        return interceptCanvasOperation(
                            property, target, args, this
                        );
                    };
                }
                
                return value;
            },
            
            set(target, property, value) {
                // 拦截属性设置
                if (property === 'font') {
                    analyzeFont(value);
                } else if (property === 'fillStyle') {
                    analyzeColor(value);
                }
                
                target[property] = value;
                return true;
            }
        });
    }
    
    return ctx;
};
```

#### 文本识别算法

```javascript
class TextAnalyzer {
    constructor() {
        this.markdown = '';
        this.currentStyle = {
            fontSize: 16,
            fontColor: '#000000',
            isBold: false,
            isItalic: false
        };
        this.contextStack = [];
    }
    
    analyzeFillText(text, x, y) {
        const formattedText = this.formatText(text);
        
        // 根据位置和样式判断文本结构
        if (this.isTitle()) {
            this.markdown += `\n\n# ${formattedText}\n`;
        } else if (this.isHighlight()) {
            this.markdown += `\`${formattedText}\``;
        } else if (this.isCodeBlock()) {
            this.markdown += `\n\`\`\`\n${formattedText}\n\`\`\`\n`;
        } else {
            this.markdown += formattedText;
        }
    }
    
    isTitle() {
        return this.currentStyle.fontSize >= 24;
    }
    
    isHighlight() {
        return this.currentStyle.fontColor !== '#000000';
    }
    
    isCodeBlock() {
        // 通过字体族和背景色识别代码块
        return this.currentStyle.fontFamily.includes('monospace') ||
               this.contextStack.includes('code');
    }
}
```

### 4. 导出处理模块 (`export.py`)

#### 导出流程控制

```python
class WeReadExporter:
    def __init__(self, page, save_path):
        self.page = page
        self.save_path = save_path
        self.meta_data = {}
        self.chapters = []
    
    async def export_markdown(self, load_timeout=60, load_interval=30):
        """导出Markdown格式内容"""
        
        # 1. 获取书籍元数据
        await self._fetch_metadata()
        
        # 2. 获取章节列表
        chapters = await self._get_chapters()
        
        # 3. 并发处理章节
        tasks = []
        for chapter in chapters:
            task = self._process_chapter(chapter, load_timeout, load_interval)
            tasks.append(task)
        
        # 等待所有章节完成
        await asyncio.gather(*tasks)
        
        # 4. 生成Markdown文件
        await self._generate_markdown()
    
    async def _process_chapter(self, chapter, timeout, interval):
        """处理单个章节"""
        
        # 导航到章节页面
        await self.page.goto(chapter['url'])
        
        # 等待内容加载
        await asyncio.sleep(interval)
        
        # 获取Canvas渲染内容
        content = await self.page.evaluate('''
            () => {
                return window.canvasInterceptor.getMarkdown();
            }
        ''')
        
        # 处理图片下载
        await self._download_images(content)
        
        # 保存章节内容
        chapter['content'] = content
        self.chapters.append(chapter)
```

#### 格式转换引擎

```python
class FormatConverter:
    def __init__(self, meta_data, chapters):
        self.meta_data = meta_data
        self.chapters = chapters
    
    async def to_epub(self, output_path, css_file=None):
        """转换为EPUB格式"""
        book = epub.EpubBook()
        
        # 设置书籍元数据
        book.set_title(self.meta_data['title'])
        book.set_language('zh-CN')
        book.add_author(self.meta_data['author'])
        
        # 创建章节
        spine = ['nav']
        for i, chapter in enumerate(self.chapters):
            epub_chapter = self._create_epub_chapter(chapter, i)
            book.add_item(epub_chapter)
            spine.append(epub_chapter)
        
        # 设置书籍结构
        book.spine = spine
        book.toc = self._create_toc()
        
        # 生成EPUB文件
        epub.write_epub(output_path, book, {})
    
    async def to_pdf(self, output_path, css_file=None):
        """转换为PDF格式"""
        # 生成HTML内容
        html_content = self._generate_html()
        
        # 应用CSS样式
        if css_file:
            css_content = self._load_css(css_file)
        else:
            css_content = self._default_css()
        
        # 使用WeasyPrint生成PDF
        html = HTML(string=html_content)
        html.write_pdf(output_path, stylesheets=[CSS(string=css_content)])
```

## 异步架构设计

### 事件循环管理

项目采用asyncio实现全异步架构：

```python
class AsyncExportManager:
    def __init__(self, max_concurrent=3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks = []
    
    async def export_books(self, book_ids, formats):
        """并发导出多本书籍"""
        
        # 创建导出任务
        for book_id in book_ids:
            task = asyncio.create_task(
                self._export_single_book(book_id, formats)
            )
            self.tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # 处理结果
        return self._process_results(results)
    
    async def _export_single_book(self, book_id, formats):
        """导出单本书籍"""
        async with self.semaphore:
            # 限制并发数量
            exporter = WeReadExporter(book_id)
            return await exporter.export(formats)
```

### 资源管理

```python
class ResourceManager:
    def __init__(self):
        self.browser_pool = BrowserPool(max_browsers=5)
        self.cache_manager = CacheManager()
        self.memory_monitor = MemoryMonitor()
    
    async def get_browser(self):
        """从池中获取浏览器实例"""
        return await self.browser_pool.acquire()
    
    async def release_browser(self, browser):
        """释放浏览器实例"""
        await self.browser_pool.release(browser)
    
    async def cleanup(self):
        """清理资源"""
        await self.browser_pool.cleanup()
        await self.cache_manager.cleanup()
```

## 缓存系统设计

### 多级缓存架构

```python
class MultiLevelCache:
    def __init__(self):
        self.memory_cache = LRUCache(maxsize=1000)
        self.disk_cache = DiskCache(cache_dir='.weread/cache')
        self.network_cache = NetworkCache()
    
    async def get(self, key, fetch_func):
        """获取缓存数据"""
        
        # 1. 检查内存缓存
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # 2. 检查磁盘缓存
        cached = await self.disk_cache.get(key)
        if cached:
            self.memory_cache[key] = cached
            return cached
        
        # 3. 从网络获取
        data = await fetch_func()
        
        # 4. 更新缓存
        self.memory_cache[key] = data
        await self.disk_cache.set(key, data)
        
        return data
```

### 智能缓存策略

```python
class SmartCacheStrategy:
    def should_cache(self, url, data):
        """判断是否应该缓存"""
        
        # 根据内容类型决定缓存策略
        content_type = self._get_content_type(url, data)
        
        if content_type == 'text':
            return len(data) < 100 * 1024  # 文本小于100KB
        elif content_type == 'image':
            return len(data) < 5 * 1024 * 1024  # 图片小于5MB
        elif content_type == 'script':
            return True  # 脚本总是缓存
        
        return False
```

## 错误处理和恢复

### 错误分类和处理

```python
class ErrorHandler:
    def __init__(self):
        self.retry_strategies = {
            'network_error': ExponentialBackoffRetry(),
            'browser_crash': BrowserRestartRetry(),
            'content_parsing': ContentReprocessRetry()
        }
    
    async def handle_error(self, error, context):
        """处理错误"""
        error_type = self._classify_error(error)
        
        if error_type in self.retry_strategies:
            strategy = self.retry_strategies[error_type]
            return await strategy.retry(context)
        else:
            # 无法恢复的错误
            raise error
```

### 断点续传机制

```python
class ResumeManager:
    def __init__(self, checkpoint_file):
        self.checkpoint_file = checkpoint_file
        self.checkpoints = self._load_checkpoints()
    
    async def save_checkpoint(self, book_id, progress):
        """保存检查点"""
        self.checkpoints[book_id] = {
            'progress': progress,
            'timestamp': time.time()
        }
        await self._save_checkpoints()
    
    async def resume_export(self, book_id):
        """恢复导出"""
        if book_id in self.checkpoints:
            checkpoint = self.checkpoints[book_id]
            return checkpoint['progress']
        return None
```

## 性能优化策略

### 1. 内存优化

```python
class MemoryOptimizer:
    def __init__(self, memory_limit=512):  # 512MB
        self.memory_limit = memory_limit * 1024 * 1024
    
    async def optimize_memory(self):
        """优化内存使用"""
        current_memory = self._get_memory_usage()
        
        if current_memory > self.memory_limit:
            # 触发垃圾回收
            import gc
            gc.collect()
            
            # 清理缓存
            await self._clear_caches()
            
            # 重启浏览器实例
            await self._restart_browsers()
```

### 2. 网络优化

```python
class NetworkOptimizer:
    def __init__(self):
        self.connection_pool = ConnectionPool()
        self.request_throttler = RequestThrottler()
    
    async def optimize_requests(self, requests):
        """优化网络请求"""
        # 合并重复请求
        merged = self._merge_requests(requests)
        
        # 应用限流
        throttled = await self.request_throttler.throttle(merged)
        
        # 使用连接池
        return await self.connection_pool.execute(throttled)
```

## 安全考虑

### 1. 数据安全

```python
class SecurityManager:
    def __init__(self):
        self.encryption = AESEncryption()
        self.sanitizer = HTMLSanitizer()
    
    async def secure_data(self, data):
        """保护敏感数据"""
        # 加密存储
        encrypted = self.encryption.encrypt(data)
        
        # 清理HTML内容
        sanitized = self.sanitizer.sanitize(encrypted)
        
        return sanitized
```

### 2. 隐私保护

```python
class PrivacyProtector:
    def __init__(self):
        self.anonymizer = DataAnonymizer()
    
    async def protect_privacy(self, user_data):
        """保护用户隐私"""
        # 匿名化处理
        anonymized = self.anonymizer.anonymize(user_data)
        
        # 删除敏感信息
        cleaned = self._remove_sensitive_info(anonymized)
        
        return cleaned
```

## 扩展性设计

### 插件系统架构

```python
class PluginSystem:
    def __init__(self):
        self.plugins = {}
        self.hooks = {}
    
    def register_plugin(self, name, plugin):
        """注册插件"""
        self.plugins[name] = plugin
        
        # 注册插件钩子
        for hook_name in plugin.get_hooks():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(plugin)
    
    async def execute_hook(self, hook_name, data):
        """执行钩子"""
        if hook_name in self.hooks:
            for plugin in self.hooks[hook_name]:
                data = await plugin.execute_hook(hook_name, data)
        return data
```

## 监控和日志

### 性能监控

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    async def track_metric(self, name, value):
        """跟踪性能指标"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            'value': value,
            'timestamp': time.time()
        })
    
    async def generate_report(self):
        """生成性能报告"""
        return {
            'total_time': time.time() - self.start_time,
            'metrics': self.metrics,
            'summary': self._generate_summary()
        }
```

---

**架构解析到此结束。** 这个架构设计确保了工具的高性能、可扩展性和稳定性。继续阅读[API文档](api.md)了解具体的接口使用方法。 🏗️