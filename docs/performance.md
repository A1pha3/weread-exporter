# 性能优化指南

## 概述

微信读书导出工具的性能优化涉及多个方面，包括内存管理、网络请求优化、并发处理等。本指南提供详细的性能调优策略和最佳实践。

## 性能指标

### 1. 关键性能指标

- **导出速度**: 单本书籍导出时间
- **内存使用**: 峰值内存消耗
- **CPU使用率**: 处理过程中的CPU负载
- **网络延迟**: 页面加载和资源下载时间
- **并发能力**: 同时处理多个任务的能力

### 2. 性能基准

```python
# 性能基准测试示例
import time
import psutil
import asyncio
from weread_exporter.export import WeReadExporter

async def benchmark_export(book_id):
    """性能基准测试"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    exporter = WeReadExporter(book_id)
    result = await exporter.export()
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    print(f"导出时间: {end_time - start_time:.2f}秒")
    print(f"内存使用: {end_memory - start_memory:.2f}MB")
    
    return result
```

## 内存优化

### 1. 内存泄漏检测

使用内存分析工具检测潜在的内存泄漏：

```python
import tracemalloc

# 启用内存跟踪
tracemalloc.start()

# 执行导出操作
exporter = WeReadExporter(book_id)
result = await exporter.export()

# 获取内存快照
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

# 显示内存使用情况
for stat in top_stats[:10]:
    print(stat)

tracemalloc.stop()
```

### 2. 大文件处理优化

对于大文件导出，采用流式处理：

```python
import io
from ebooklib import epub

class OptimizedEPUBExporter:
    """优化的EPUB导出器"""
    
    def __init__(self):
        self.buffer_size = 8192  # 8KB缓冲区
    
    async def export_large_book(self, book_data):
        """导出大文件书籍"""
        # 使用内存映射文件
        with io.BytesIO() as buffer:
            book = epub.EpubBook()
            
            # 分块处理章节
            for chapter in book_data['chapters']:
                # 处理章节内容
                epub_chapter = await self.process_chapter(chapter)
                book.add_item(epub_chapter)
                
                # 定期清理内存
                if len(book.items) % 10 == 0:
                    await self.cleanup_memory()
            
            # 写入文件
            epub.write_epub(buffer, book, {})
            
            return buffer.getvalue()
    
    async def cleanup_memory(self):
        """清理内存"""
        import gc
        gc.collect()
```

### 3. 图片优化

优化图片处理以减少内存使用：

```python
from PIL import Image
import io

class ImageOptimizer:
    """图片优化器"""
    
    def __init__(self, max_width=1200, quality=85):
        self.max_width = max_width
        self.quality = quality
    
    async def optimize_image(self, image_data):
        """优化图片"""
        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            
            # 调整大小
            if image.width > self.max_width:
                ratio = self.max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为RGB模式（如果需要）
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # 保存优化后的图片
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=self.quality, optimize=True)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"图片优化失败: {e}")
            return image_data  # 返回原始数据
```

## 网络优化

### 1. 请求并发控制

使用信号量控制并发请求数量：

```python
import asyncio
from aiohttp import ClientSession, TCPConnector

class OptimizedDownloader:
    """优化的下载器"""
    
    def __init__(self, max_concurrent=5, timeout=30):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.connector = TCPConnector(limit=max_concurrent, limit_per_host=2)
    
    async def download_resources(self, urls):
        """并发下载资源"""
        async with ClientSession(connector=self.connector) as session:
            tasks = [self.download_with_semaphore(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤成功的结果
            successful_results = [r for r in results if not isinstance(r, Exception)]
            return successful_results
    
    async def download_with_semaphore(self, session, url):
        """使用信号量控制的下载"""
        async with self.semaphore:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        raise Exception(f"HTTP {response.status}: {url}")
            except asyncio.TimeoutError:
                raise Exception(f"Timeout: {url}")
```

### 2. 缓存策略

实现智能缓存减少重复请求：

```python
import hashlib
import os
from datetime import datetime, timedelta

class SmartCache:
    """智能缓存系统"""
    
    def __init__(self, cache_dir=".cache", ttl_hours=24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, url):
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_cache_path(self, key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    async def get_cached_content(self, url):
        """获取缓存内容"""
        key = self.get_cache_key(url)
        cache_path = self.get_cache_path(key)
        
        if os.path.exists(cache_path):
            # 检查缓存是否过期
            mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - mtime < self.ttl:
                with open(cache_path, 'rb') as f:
                    return f.read()
        
        return None
    
    async def set_cached_content(self, url, content):
        """设置缓存内容"""
        key = self.get_cache_key(url)
        cache_path = self.get_cache_path(key)
        
        with open(cache_path, 'wb') as f:
            f.write(content)
```

## 并发优化

### 1. 异步任务调度

优化异步任务调度策略：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedScheduler:
    """优化的任务调度器"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def process_batch_async(self, tasks, batch_size=10):
        """批量异步处理"""
        results = []
        
        # 分批处理
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            
            # 并发处理批次
            batch_results = await asyncio.gather(
                *[self.process_single_task(task) for task in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
            
            # 批次间延迟，避免过载
            await asyncio.sleep(0.1)
        
        return results
    
    async def process_single_task(self, task):
        """处理单个任务"""
        # 异步任务处理逻辑
        pass
```

### 2. 资源池管理

管理浏览器实例等资源：

```python
import asyncio
from pyppeteer import launch

class BrowserPool:
    """浏览器实例池"""
    
    def __init__(self, pool_size=3):
        self.pool_size = pool_size
        self.pool = asyncio.Queue(maxsize=pool_size)
        self._initialized = False
    
    async def initialize(self):
        """初始化浏览器池"""
        if not self._initialized:
            for _ in range(self.pool_size):
                browser = await launch({
                    'headless': True,
                    'args': ['--no-sandbox', '--disable-setuid-sandbox']
                })
                await self.pool.put(browser)
            self._initialized = True
    
    async def get_browser(self):
        """获取浏览器实例"""
        await self.initialize()
        return await self.pool.get()
    
    async def return_browser(self, browser):
        """归还浏览器实例"""
        await self.pool.put(browser)
    
    async def close(self):
        """关闭浏览器池"""
        while not self.pool.empty():
            browser = await self.pool.get()
            await browser.close()
```

## 磁盘I/O优化

### 1. 文件写入优化

优化文件写入操作：

```python
import aiofiles
import os

class OptimizedFileWriter:
    """优化的文件写入器"""
    
    def __init__(self, chunk_size=8192):
        self.chunk_size = chunk_size
    
    async def write_large_file(self, file_path, data):
        """写入大文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            # 分块写入
            for i in range(0, len(data), self.chunk_size):
                chunk = data[i:i + self.chunk_size]
                await f.write(chunk)
```

### 2. 临时文件管理

优化临时文件使用：

```python
import tempfile
import shutil

class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self):
        self.temp_dir = None
        self.files = []
    
    async def create_temp_file(self, suffix='.tmp'):
        """创建临时文件"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
        
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        os.close(fd)
        self.files.append(path)
        return path
    
    async def cleanup(self):
        """清理临时文件"""
        for file_path in self.files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except OSError:
                pass  # 忽略删除错误
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except OSError:
                pass
```

## 监控和诊断

### 1. 性能监控

实现性能监控系统：

```python
import time
import psutil
import asyncio
from datetime import datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
    
    async def start_monitoring(self, operation_name):
        """开始监控"""
        self.start_time = time.time()
        self.metrics[operation_name] = {
            'start_time': datetime.now(),
            'start_memory': psutil.Process().memory_info().rss,
            'start_cpu': psutil.cpu_percent(interval=None)
        }
    
    async def stop_monitoring(self, operation_name):
        """停止监控"""
        if operation_name in self.metrics:
            end_time = time.time()
            metrics = self.metrics[operation_name]
            
            metrics.update({
                'end_time': datetime.now(),
                'duration': end_time - self.start_time,
                'end_memory': psutil.Process().memory_info().rss,
                'end_cpu': psutil.cpu_percent(interval=None),
                'memory_used': (psutil.Process().memory_info().rss - metrics['start_memory']) / 1024 / 1024
            })
    
    def get_report(self):
        """生成性能报告"""
        report = {}
        for op_name, metrics in self.metrics.items():
            report[op_name] = {
                'duration_seconds': metrics.get('duration', 0),
                'memory_used_mb': metrics.get('memory_used', 0),
                'cpu_usage': metrics.get('end_cpu', 0)
            }
        return report
```

### 2. 日志优化

优化日志记录性能：

```python
import logging
import logging.handlers

class OptimizedLogger:
    """优化的日志记录器"""
    
    @staticmethod
    def setup_logging(log_level=logging.INFO, max_file_size=10*1024*1024):  # 10MB
        """设置优化的日志配置"""
        logger = logging.getLogger('weread_exporter')
        logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 文件处理器（带轮转）
            file_handler = logging.handlers.RotatingFileHandler(
                'weread_exporter.log',
                maxBytes=max_file_size,
                backupCount=5
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
```

## 最佳实践总结

### 1. 常规优化
- 使用异步编程避免阻塞
- 合理设置并发限制
- 定期清理内存和资源
- 实现智能缓存策略

### 2. 监控和维护
- 建立性能基准
- 定期进行性能测试
- 监控资源使用情况
- 优化瓶颈环节

### 3. 配置调优
- 根据硬件配置调整参数
- 测试不同配置的性能影响
- 提供配置文档和指导

通过实施这些性能优化策略，可以显著提升微信读书导出工具的执行效率和资源利用率。