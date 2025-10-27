# API文档

## 概述

微信读书导出工具提供完整的Python API接口，支持程序化调用和自定义扩展。所有核心功能都通过模块化的类和方法暴露给开发者。

## 核心类

### WeReadExporter类

主导出器类，负责协调整个导出流程。

#### 构造函数

```python
class WeReadExporter:
    def __init__(self, book_id: str, config: Optional[Dict] = None):
        """
        初始化导出器
        
        Args:
            book_id: 书籍ID
            config: 配置字典，可选
        """
```

**参数说明**:
- `book_id`: 微信读书书籍ID，必填
- `config`: 配置选项字典，可选

**配置选项**:
```python
config = {
    'output_dir': 'output',           # 输出目录
    'cache_dir': '.weread/cache',     # 缓存目录
    'headless': True,                 # 无头模式
    'timeout': 60,                    # 超时时间（秒）
    'load_interval': 30,              # 加载间隔（秒）
    'proxy_server': None,             # 代理服务器
    'user_agent': None,               # 自定义User-Agent
    'force_login': False,             # 强制登录
}
```

#### 主要方法

##### export()

```python
async def export(self, 
                formats: List[str] = ['epub'],
                callback: Optional[Callable] = None) -> ExportResult:
    """
    导出书籍
    
    Args:
        formats: 输出格式列表，支持['epub', 'pdf', 'mobi', 'txt', 'md']
        callback: 进度回调函数
    
    Returns:
        ExportResult: 导出结果对象
    """
```

**使用示例**:
```python
import asyncio
from weread_exporter import WeReadExporter

async def main():
    exporter = WeReadExporter('08232ac0720befa90825d88')
    result = await exporter.export(['epub', 'pdf'])
    print(f"导出完成: {result.output_files}")

asyncio.run(main())
```

##### export_chapter()

```python
async def export_chapter(self, 
                        chapter_id: str,
                        formats: List[str] = ['epub']) -> ExportResult:
    """
    导出单个章节
    
    Args:
        chapter_id: 章节ID
        formats: 输出格式列表
    
    Returns:
        ExportResult: 导出结果
    """
```

##### get_book_info()

```python
async def get_book_info(self) -> BookInfo:
    """
    获取书籍信息
    
    Returns:
        BookInfo: 书籍信息对象
    """
```

**BookInfo结构**:
```python
class BookInfo:
    title: str           # 书籍标题
    author: str          # 作者
    cover_url: str       # 封面URL
    chapter_count: int  # 章节数量
    total_pages: int     # 总页数
    isbn: Optional[str]  # ISBN号
    publisher: str      # 出版社
    publish_date: str   # 出版日期
```

### WeReadWebPage类

网页控制类，负责浏览器操作和内容获取。

#### 构造函数

```python
class WeReadWebPage:
    def __init__(self, 
                 book_id: str,
                 browser_config: Optional[Dict] = None):
        """
        初始化网页控制器
        
        Args:
            book_id: 书籍ID
            browser_config: 浏览器配置
        """
```

**浏览器配置**:
```python
browser_config = {
    'headless': True,                    # 无头模式
    'viewport': {'width': 1920, 'height': 1080},  # 视口大小
    'user_agent': 'custom agent',       # 用户代理
    'proxy': 'http://proxy:8080',        # 代理设置
    'ignore_https_errors': False,        # 忽略HTTPS错误
    'slow_mo': 0,                        # 操作延迟（毫秒）
}
```

#### 主要方法

##### launch()

```python
async def launch(self, 
                headless: bool = True,
                force_login: bool = False) -> None:
    """
    启动浏览器并准备导出环境
    
    Args:
        headless: 是否无头模式
        force_login: 是否强制登录
    """
```

##### get_chapters()

```python
async def get_chapters(self) -> List[ChapterInfo]:
    """
    获取章节列表
    
    Returns:
        List[ChapterInfo]: 章节信息列表
    """
```

**ChapterInfo结构**:
```python
class ChapterInfo:
    id: str              # 章节ID
    title: str           # 章节标题
    url: str             # 章节URL
    page_count: int      # 页数
    order: int           # 章节顺序
```

##### extract_content()

```python
async def extract_content(self, 
                         chapter: ChapterInfo,
                         timeout: int = 60) -> ChapterContent:
    """
    提取章节内容
    
    Args:
        chapter: 章节信息
        timeout: 超时时间
    
    Returns:
        ChapterContent: 章节内容
    """
```

**ChapterContent结构**:
```python
class ChapterContent:
    html: str                    # HTML内容
    markdown: str               # Markdown内容
    images: List[ImageInfo]     # 图片信息
    styles: Dict[str, str]      # 样式信息
    metadata: Dict[str, Any]    # 元数据
```

### FormatConverter类

格式转换器类，支持多种输出格式。

#### 主要方法

##### to_epub()

```python
async def to_epub(self,
                 content: BookContent,
                 output_path: str,
                 css_file: Optional[str] = None) -> None:
    """
    转换为EPUB格式
    
    Args:
        content: 书籍内容
        output_path: 输出路径
        css_file: 自定义CSS文件
    """
```

##### to_pdf()

```python
async def to_pdf(self,
                 content: BookContent,
                 output_path: str,
                 css_file: Optional[str] = None,
                 quality: str = 'standard') -> None:
    """
    转换为PDF格式
    
    Args:
        content: 书籍内容
        output_path: 输出路径
        css_file: 自定义CSS文件
        quality: 输出质量 ['low', 'standard', 'high']
    """
```

##### to_mobi()

```python
async def to_mobi(self,
                  content: BookContent,
                  output_path: str) -> None:
    """
    转换为MOBI格式
    
    Args:
        content: 书籍内容
        output_path: 输出路径
    """
```

## 工具函数

### 文件操作

#### ensure_directory()

```python
def ensure_directory(path: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    
    Returns:
        str: 标准化后的路径
    """
```

#### sanitize_filename()

```python
def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
```

### 网络工具

#### download_file()

```python
async def download_file(url: str, 
                       save_path: str,
                       timeout: int = 30) -> bool:
    """
    下载文件
    
    Args:
        url: 文件URL
        save_path: 保存路径
        timeout: 超时时间
    
    Returns:
        bool: 是否下载成功
    """
```

#### fetch_with_retry()

```python
async def fetch_with_retry(url: str,
                          max_retries: int = 3,
                          delay: float = 1.0) -> Optional[bytes]:
    """
    带重试的HTTP请求
    
    Args:
        url: 请求URL
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    
    Returns:
        Optional[bytes]: 响应内容
    """
```

## 回调接口

### 进度回调

```python
class ProgressCallback:
    """进度回调接口"""
    
    async def on_start(self, total: int) -> None:
        """导出开始"""
        pass
    
    async def on_progress(self, current: int, total: int) -> None:
        """进度更新"""
        pass
    
    async def on_chapter_complete(self, chapter: ChapterInfo) -> None:
        """章节完成"""
        pass
    
    async def on_format_complete(self, format: str, path: str) -> None:
        """格式转换完成"""
        pass
    
    async def on_complete(self, result: ExportResult) -> None:
        """导出完成"""
        pass
    
    async def on_error(self, error: Exception) -> None:
        """发生错误"""
        pass
```

**使用示例**:
```python
class MyProgressCallback(ProgressCallback):
    async def on_progress(self, current: int, total: int):
        percentage = (current / total) * 100
        print(f"进度: {percentage:.1f}% ({current}/{total})")
    
    async def on_complete(self, result: ExportResult):
        print(f"导出完成! 文件保存在: {result.output_dir}")

# 使用自定义回调
exporter = WeReadExporter(book_id)
result = await exporter.export(['epub'], callback=MyProgressCallback())
```

## 配置管理

### Config类

```python
class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass
    
    def save(self) -> None:
        """保存配置到文件"""
        pass
    
    def load(self) -> None:
        """从文件加载配置"""
        pass
```

**配置文件格式** (YAML):
```yaml
# ~/.weread/config.yaml

general:
  output_dir: ~/Documents/books
  cache_dir: ~/.weread/cache
  timeout: 60
  headless: true

browser:
  viewport:
    width: 1920
    height: 1080
  user_agent: "Mozilla/5.0..."

format:
  epub:
    css_file: ~/.weread/custom.css
  pdf:
    quality: high
```

## 错误处理

### 自定义异常

```python
class WeReadError(Exception):
    """基础异常类"""
    pass

class BrowserError(WeReadError):
    """浏览器相关错误"""
    pass

class NetworkError(WeReadError):
    """网络相关错误"""
    pass

class ContentError(WeReadError):
    """内容处理错误"""
    pass

class FormatError(WeReadError):
    """格式转换错误"""
    pass
```

### 错误处理示例

```python
from weread_exporter import WeReadExporter, WeReadError

async def safe_export(book_id: str):
    try:
        exporter = WeReadExporter(book_id)
        result = await exporter.export(['epub'])
        return result
    except WeReadError as e:
        print(f"导出失败: {e}")
        # 重试逻辑或错误处理
        return None
```

## 批量处理API

### BatchExporter类

```python
class BatchExporter:
    """批量导出器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化批量导出器"""
    
    async def export_books(self,
                         book_ids: List[str],
                         formats: List[str] = ['epub'],
                         concurrency: int = 3) -> BatchResult:
        """
        批量导出书籍
        
        Args:
            book_ids: 书籍ID列表
            formats: 输出格式列表
            concurrency: 并发数量
        
        Returns:
            BatchResult: 批量导出结果
        """
    
    async def export_from_file(self,
                              file_path: str,
                              formats: List[str] = ['epub'],
                              concurrency: int = 3) -> BatchResult:
        """
        从文件批量导出
        
        Args:
            file_path: 包含书籍ID的文件路径
            formats: 输出格式列表
            concurrency: 并发数量
        """
```

**使用示例**:
```python
from weread_exporter import BatchExporter

async def batch_export():
    exporter = BatchExporter()
    
    # 从列表导出
    book_ids = ['id1', 'id2', 'id3']
    result = await exporter.export_books(book_ids, ['epub', 'pdf'], concurrency=2)
    
    # 从文件导出
    result = await exporter.export_from_file('books.txt', ['epub'])
    
    print(f"成功: {result.success_count}, 失败: {result.failure_count}")
```

## 插件系统API

### 插件基类

```python
class BasePlugin:
    """插件基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def before_export(self, exporter: WeReadExporter) -> None:
        """导出前钩子"""
        pass
    
    async def after_export(self, exporter: WeReadExporter, result: ExportResult) -> None:
        """导出后钩子"""
        pass
    
    async def process_content(self, content: ChapterContent) -> ChapterContent:
        """内容处理钩子"""
        return content
```

### 插件管理器

```python
class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """注册插件"""
        pass
    
    def unregister_plugin(self, name: str) -> None:
        """注销插件"""
        pass
    
    async def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """执行钩子"""
        pass
```

## 性能监控API

### 监控器类

```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name: str) -> None:
        """开始计时"""
        pass
    
    def stop_timer(self, name: str) -> float:
        """停止计时并返回耗时"""
        pass
    
    def track_memory(self) -> float:
        """跟踪内存使用"""
        pass
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        pass
```

## 实用工具函数

### 日期时间工具

```python
def format_timestamp(timestamp: float) -> str:
    """格式化时间戳"""
    pass

def humanize_duration(seconds: float) -> str:
    """人性化显示时长"""
    pass
```

### 文件大小工具

```python
def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    pass

def get_file_info(file_path: str) -> Dict[str, Any]:
    """获取文件信息"""
    pass
```

## 扩展开发示例

### 自定义导出器

```python
from weread_exporter import WeReadExporter, ProgressCallback

class CustomExporter(WeReadExporter):
    async def export_with_custom_processing(self, formats):
        """自定义导出流程"""
        
        # 自定义预处理
        await self.custom_preprocess()
        
        # 使用父类导出逻辑
        result = await super().export(formats)
        
        # 自定义后处理
        await self.custom_postprocess(result)
        
        return result
    
    async def custom_preprocess(self):
        """自定义预处理逻辑"""
        # 例如：下载额外资源、验证内容等
        pass
    
    async def custom_postprocess(self, result):
        """自定义后处理逻辑"""
        # 例如：生成额外文件、发送通知等
        pass
```

### 集成到其他应用

```python
import asyncio
from weread_exporter import WeReadExporter

class MyReadingApp:
    def __init__(self):
        self.exporter = None
    
    async def export_book_for_reading(self, book_id: str):
        """为阅读应用导出书籍"""
        
        self.exporter = WeReadExporter(book_id, {
            'output_dir': './my_reading_app/books',
            'headless': True
        })
        
        # 导出为EPUB格式
        result = await self.exporter.export(['epub'])
        
        # 集成到阅读应用
        await self.integrate_to_app(result)
        
        return result
    
    async def integrate_to_app(self, result):
        """将导出结果集成到应用"""
        # 例如：更新数据库、发送推送通知等
        pass
```

---

**API文档到此结束。** 这些接口提供了完整的程序化访问能力，支持各种自定义和扩展需求。继续阅读[开发指南](development.md)了解更深入的开发技巧。 💻