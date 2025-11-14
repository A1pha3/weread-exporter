# 开发指南

## 开发环境搭建

### 1. 克隆项目

```bash
# 克隆项目到本地
git clone https://github.com/drunkdream/weread-exporter.git
cd weread-exporter

# 查看项目结构
ls -la
```

### 2. 创建虚拟环境

```bash
# 使用 uv 创建项目虚拟环境（默认 .venv）
uv venv

# 同步核心依赖
uv sync
```

### 3. 安装开发依赖

```bash
# 同步开发分组依赖
uv sync --extra dev
```

### 4. 验证开发环境

```bash
# 运行测试
uv run pytest

# 检查代码风格
uv run black --check .
uv run flake8 .

# 类型检查
uv run mypy weread_exporter/
```

## 项目结构详解

### 核心模块

```
weread_exporter/
├── __init__.py          # 包初始化，定义版本和导出
├── __main__.py          # 命令行入口点
├── export.py            # 导出逻辑核心
├── webpage.py          # 网页控制和浏览器管理
├── utils.py            # 工具函数和辅助类
└── hook.js             # Canvas拦截脚本
```

### 脚本目录

```
scripts/
├── build.py            # 项目构建脚本
├── install.py          # 安装和依赖管理
├── test_runner.py      # 测试运行器
├── cleanup.py          # 项目清理
└── update_deps.py      # 依赖更新
```

### 测试目录

```
tests/
├── __init__.py         # 测试包初始化
├── test_utils.py       # 工具函数测试
└── test_export.py      # 导出功能测试（待完善）
```

## 代码架构解析

### 异步架构设计

项目采用全异步架构，基于Python的asyncio库：

```python
import asyncio
from weread_exporter import WeReadExporter

async def main():
    # 创建导出器实例
    exporter = WeReadExporter('book_id')
    
    # 异步导出
    result = await exporter.export(['epub', 'pdf'])
    
    print(f"导出完成: {result}")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())
```

### 模块职责划分

#### 1. 命令行接口 (`__main__.py`)

- 参数解析和验证
- 配置管理
- 错误处理和用户反馈
- 异步事件循环管理

#### 2. 网页控制 (`webpage.py`)

- 浏览器实例生命周期管理
- 页面导航和内容加载
- Canvas Hook脚本注入
- 网络请求拦截
- 反检测机制实现

#### 3. 导出处理 (`export.py`)

- 导出流程协调
- 章节内容处理
- 格式转换调度
- 缓存管理
- 质量控制

#### 4. 工具函数 (`utils.py`)

- 文件操作工具
- 网络请求工具
- 数据处理工具
- 配置管理工具

## 核心开发概念

### Canvas Hook技术

#### 基本原理

微信读书使用Canvas渲染文本以防止复制。我们通过JavaScript Proxy拦截Canvas操作：

```javascript
// 拦截Canvas的getContext方法
const originalGetContext = HTMLCanvasElement.prototype.getContext;

HTMLCanvasElement.prototype.getContext = function(type) {
    const ctx = originalGetContext.call(this, type);
    
    if (type === '2d') {
        // 创建代理拦截所有操作
        return new Proxy(ctx, {
            get(target, prop) {
                const value = target[prop];
                
                if (typeof value === 'function') {
                    // 拦截方法调用
                    return function(...args) {
                        return interceptOperation(prop, target, args);
                    };
                }
                
                return value;
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
        this.currentStyle = {
            fontSize: 16,
            fontColor: '#000000',
            isBold: false
        };
        this.markdown = '';
    }
    
    analyzeText(text, style) {
        // 根据样式识别文本结构
        if (style.fontSize >= 24) {
            return `\n# ${text}\n`;  // 标题
        } else if (style.fontColor !== '#000000') {
            return `\`${text}\``;    // 高亮
        } else {
            return text;              // 普通文本
        }
    }
}
```

### 异步并发处理

#### 章节并发导出

```python
async def export_chapters_concurrently(self, chapters, max_concurrent=3):
    """并发导出章节"""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def export_chapter(chapter):
        async with semaphore:
            return await self._export_single_chapter(chapter)
    
    # 创建所有章节的导出任务
    tasks = [export_chapter(chapter) for chapter in chapters]
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return self._process_results(results)
```

#### 浏览器连接池

```python
class BrowserPool:
    def __init__(self, max_browsers=5):
        self.max_browsers = max_browsers
        self.available = []
        self.in_use = set()
        self.semaphore = asyncio.Semaphore(max_browsers)
    
    async def acquire(self):
        """获取浏览器实例"""
        async with self.semaphore:
            if self.available:
                browser = self.available.pop()
            else:
                browser = await self._create_browser()
            
            self.in_use.add(browser)
            return browser
    
    async def release(self, browser):
        """释放浏览器实例"""
        self.in_use.remove(browser)
        self.available.append(browser)
```

## 开发工作流

### 1. 功能开发流程

#### 步骤1: 需求分析

```python
# 创建功能规格文档
FEATURE_SPEC = {
    'name': '批量导出功能',
    'description': '支持同时导出多本书籍',
    'requirements': [
        '支持书籍ID列表输入',
        '并发控制机制',
        '进度报告功能',
        '错误处理和重试'
    ],
    'api_changes': ['新增BatchExporter类'],
    'test_cases': ['测试并发导出', '测试错误处理']
}
```

#### 步骤2: 代码实现

```python
# 在适当模块中实现功能
class BatchExporter:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def export_books(self, book_ids, formats):
        """批量导出书籍"""
        tasks = []
        
        for book_id in book_ids:
            task = self._export_single_book(book_id, formats)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
```

#### 步骤3: 单元测试

```python
# tests/test_batch.py
import pytest
from weread_exporter import BatchExporter

class TestBatchExporter:
    @pytest.mark.asyncio
    async def test_concurrent_export(self):
        """测试并发导出"""
        exporter = BatchExporter(max_concurrent=2)
        book_ids = ['id1', 'id2', 'id3']
        
        results = await exporter.export_books(book_ids, ['epub'])
        
        assert len(results) == 3
        assert all(r.success for r in results)
```

#### 步骤4: 集成测试

```python
# tests/integration/test_batch_integration.py
class TestBatchIntegration:
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_real_books_export(self):
        """真实书籍批量导出测试"""
        # 使用测试用的书籍ID
        book_ids = ['test_book_1', 'test_book_2']
        
        exporter = BatchExporter()
        results = await exporter.export_books(book_ids, ['epub'])
        
        # 验证输出文件存在
        for result in results:
            assert result.output_files
            for file_path in result.output_files:
                assert os.path.exists(file_path)
```

### 2. 代码质量保证

#### 代码风格检查

```bash
# 使用black格式化代码
black weread_exporter/ tests/

# 使用flake8检查代码风格
flake8 weread_exporter/ tests/

# 使用mypy进行类型检查
mypy weread_exporter/
```

#### 自动化测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_export.py -v

# 生成测试覆盖率报告
pytest --cov=weread_exporter --cov-report=html
```

#### 持续集成配置

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install uv and sync deps
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        uv sync --extra dev
    - name: Run tests
      run: uv run pytest
    - name: Check code style
      run: uv run flake8 weread_exporter/
```

## 高级开发技巧

### 1. 性能优化

#### 内存优化

```python
import gc
from memory_profiler import profile

class MemoryOptimizer:
    def __init__(self, threshold_mb=500):
        self.threshold = threshold_mb * 1024 * 1024
    
    @profile
    async def optimize_memory(self):
        """内存优化"""
        current_memory = self.get_memory_usage()
        
        if current_memory > self.threshold:
            # 触发垃圾回收
            gc.collect()
            
            # 清理缓存
            await self.clear_caches()
            
            # 重启高内存消耗组件
            await self.restart_heavy_components()
```

#### 网络优化

```python
import aiohttp
from aiohttp import TCPConnector

class OptimizedHttpClient:
    def __init__(self):
        self.connector = TCPConnector(
            limit=100,           # 最大连接数
            limit_per_host=10,    # 每主机最大连接数
            ttl_dns_cache=300    # DNS缓存时间
        )
    
    async def fetch(self, url, timeout=30):
        """优化的HTTP请求"""
        timeout = aiohttp.ClientTimeout(total=timeout)
        
        async with aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout
        ) as session:
            async with session.get(url) as response:
                return await response.text()
```

### 2. 错误处理和恢复

#### 智能重试机制

```python
import asyncio
from typing import Type, Tuple

class RetryManager:
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(self, coro, *args, 
                               retry_exceptions: Tuple[Type[Exception]] = (Exception,)):
        """带重试的执行"""
        
        for attempt in range(self.max_retries + 1):
            try:
                return await coro(*args)
            except retry_exceptions as e:
                if attempt == self.max_retries:
                    raise  # 最后一次尝试仍然失败
                
                # 指数退避
                delay = self.base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
```

#### 断点续传

```python
import json
import os
from datetime import datetime

class ResumeManager:
    def __init__(self, checkpoint_dir='.checkpoints'):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(self, book_id, progress_data):
        """保存检查点"""
        checkpoint_file = os.path.join(
            self.checkpoint_dir, f"{book_id}.json"
        )
        
        data = {
            'book_id': book_id,
            'progress': progress_data,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_checkpoint(self, book_id):
        """加载检查点"""
        checkpoint_file = os.path.join(
            self.checkpoint_dir, f"{book_id}.json"
        )
        
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        return None
```

### 3. 安全考虑

#### 输入验证

```python
import re
from typing import Any

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_book_id(book_id: Any) -> str:
        """验证书籍ID格式"""
        if not isinstance(book_id, str):
            raise ValueError("书籍ID必须是字符串")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', book_id):
            raise ValueError("无效的书籍ID格式")
        
        return book_id.strip()
    
    @staticmethod
    def validate_output_formats(formats: Any) -> List[str]:
        """验证输出格式"""
        if not isinstance(formats, list):
            raise ValueError("输出格式必须是列表")
        
        valid_formats = {'epub', 'pdf', 'mobi', 'txt', 'md'}
        
        for fmt in formats:
            if fmt not in valid_formats:
                raise ValueError(f"不支持的输出格式: {fmt}")
        
        return formats
```

#### 安全的数据处理

```python
import html
from urllib.parse import urlparse

class SecuritySanitizer:
    """安全清理器"""
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """清理HTML内容"""
        # 移除危险标签和属性
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        cleaned = re.sub(r'on\w+=".*?"', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL安全性"""
        parsed = urlparse(url)
        
        # 只允许HTTP/HTTPS协议
        if parsed.scheme not in {'http', 'https'}:
            return False
        
        # 验证域名
        if not parsed.netloc:
            return False
        
        return True
```

## 插件开发

### 创建自定义插件

```python
from weread_exporter import BasePlugin

class CustomCSSPlugin(BasePlugin):
    """自定义CSS插件"""
    
    def __init__(self, css_file_path: str):
        super().__init__('custom_css')
        self.css_file_path = css_file_path
    
    async def before_export(self, exporter):
        """导出前应用自定义CSS"""
        if os.path.exists(self.css_file_path):
            with open(self.css_file_path, 'r') as f:
                custom_css = f.read()
            exporter.config['custom_css'] = custom_css
    
    async def process_content(self, content):
        """处理内容时应用CSS"""
        if hasattr(content, 'html') and hasattr(self, 'custom_css'):
            # 在HTML中注入自定义CSS
            content.html = content.html.replace(
                '</head>',
                f'<style>{self.custom_css}</style></head>'
            )
        return content
```

### 注册和使用插件

```python
from weread_exporter import WeReadExporter, PluginManager

# 创建插件管理器
plugin_manager = PluginManager()

# 注册自定义插件
css_plugin = CustomCSSPlugin('my_styles.css')
plugin_manager.register_plugin(css_plugin)

# 使用带插件的导出器
exporter = WeReadExporter('book_id', plugin_manager=plugin_manager)
result = await exporter.export(['epub'])
```

## 调试和诊断

### 调试模式启用

```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# 在代码中添加调试信息
logger = logging.getLogger(__name__)

async def debug_export():
    logger.debug("开始导出流程")
    
    try:
        # 导出逻辑
        result = await exporter.export(['epub'])
        logger.info("导出成功: %s", result)
    except Exception as e:
        logger.error("导出失败: %s", e, exc_info=True)
```

### 性能分析

```python
import cProfile
import pstats
from io import StringIO

async def profile_export():
    """性能分析导出过程"""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        result = await exporter.export(['epub'])
    finally:
        profiler.disable()
    
    # 生成分析报告
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats()
    
    print("性能分析报告:")
    print(stream.getvalue())
```

## 贡献指南

### 代码提交规范

1. **功能分支**: 从main分支创建功能分支
2. **提交信息**: 使用约定式提交格式
3. **测试覆盖**: 新功能必须包含测试
4. **文档更新**: 更新相关文档

### 提交信息格式

```bash
feat: 添加批量导出功能

- 新增BatchExporter类
- 支持并发书籍导出
- 添加进度报告功能

Closes #123
```

### Pull Request流程

1. **创建PR**: 从功能分支到main分支
2. **CI检查**: 确保所有测试通过
3. **代码审查**: 至少需要一名审查者
4. **合并策略**: 使用Squash Merge

## 发布流程

### 版本管理

```python
# weread_exporter/__init__.py
VERSION = "1.0.0"

# 版本号规范: MAJOR.MINOR.PATCH
# MAJOR: 不兼容的API修改
# MINOR: 向下兼容的功能性新增
# PATCH: 向下兼容的问题修正
```

### 发布检查清单

- [ ] 更新版本号
- [ ] 更新CHANGELOG.md
- [ ] 运行完整测试套件
- [ ] 构建发布包
- [ ] 上传到PyPI
- [ ] 创建GitHub Release

---

**开发指南到此结束。** 这些内容将帮助您深入理解项目架构并参与开发工作。继续探索其他文档了解更多高级功能！ 🚀