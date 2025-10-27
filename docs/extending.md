# 扩展开发指南

## 概述

微信读书导出工具提供了灵活的扩展机制，允许开发者自定义导出功能、添加新的格式支持或修改现有行为。

## 扩展类型

### 1. 自定义导出器

创建新的导出器类来支持额外的格式：

```python
from weread_exporter.export import BaseExporter
from ebooklib import epub

class CustomExporter(BaseExporter):
    """自定义导出器示例"""
    
    def __init__(self, book_data, config=None):
        super().__init__(book_data, config)
        self.format_name = "custom"
    
    async def export(self):
        """实现自定义导出逻辑"""
        # 处理书籍数据
        processed_content = await self.process_content()
        
        # 生成自定义格式文件
        output_file = await self.generate_custom_format(processed_content)
        
        return output_file
    
    async def generate_custom_format(self, content):
        """生成自定义格式"""
        # 实现具体格式生成逻辑
        pass
```

### 2. 样式处理器

自定义样式处理逻辑：

```python
from weread_exporter.export import StyleProcessor

class CustomStyleProcessor(StyleProcessor):
    """自定义样式处理器"""
    
    def process_css(self, css_content):
        """处理CSS样式"""
        # 添加自定义CSS规则
        custom_css = """
        .custom-class {
            font-family: 'Custom Font', serif;
            line-height: 1.8;
        }
        """
        return css_content + custom_css
    
    def process_html_styles(self, html_content):
        """处理HTML内联样式"""
        # 实现样式转换逻辑
        return html_content
```

### 3. 内容过滤器

添加内容过滤和修改功能：

```python
from weread_exporter.export import ContentFilter

class CustomContentFilter(ContentFilter):
    """自定义内容过滤器"""
    
    def filter_chapter_content(self, chapter_html):
        """过滤章节内容"""
        # 移除不需要的元素
        cleaned_html = self.remove_ads(chapter_html)
        cleaned_html = self.optimize_images(cleaned_html)
        
        return cleaned_html
    
    def remove_ads(self, html_content):
        """移除广告内容"""
        # 实现广告移除逻辑
        return html_content
    
    def optimize_images(self, html_content):
        """优化图片"""
        # 实现图片优化逻辑
        return html_content
```

## 插件系统

### 1. 插件注册

创建插件注册机制：

```python
# plugins/__init__.py
PLUGINS = {}

def register_plugin(name, plugin_class):
    """注册插件"""
    PLUGINS[name] = plugin_class

def get_plugin(name):
    """获取插件"""
    return PLUGINS.get(name)
```

### 2. 插件实现示例

```python
# plugins/custom_exporter.py
from weread_exporter.plugins import register_plugin
from weread_exporter.export import BaseExporter

class CustomExporterPlugin(BaseExporter):
    """自定义导出器插件"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def export(self):
        # 插件特定的导出逻辑
        pass

# 注册插件
register_plugin("custom_exporter", CustomExporterPlugin)
```

## 配置扩展

### 1. 自定义配置

扩展配置系统：

```python
# config/custom_config.py
from dataclasses import dataclass
from weread_exporter.config import BaseConfig

@dataclass
class CustomConfig(BaseConfig):
    """自定义配置"""
    custom_option: str = "default_value"
    enable_feature: bool = False
    
    def validate(self):
        """验证配置"""
        super().validate()
        # 添加自定义验证逻辑
        if len(self.custom_option) > 100:
            raise ValueError("custom_option too long")
```

### 2. 配置加载

```python
from weread_exporter.config import load_config
from config.custom_config import CustomConfig

# 加载自定义配置
config = load_config(CustomConfig, "custom_config.yaml")
```

## 钩子系统

### 1. 事件钩子

添加事件处理钩子：

```python
from weread_exporter.hooks import EventHook

class ExportHook(EventHook):
    """导出事件钩子"""
    
    async def before_export(self, book_data):
        """导出前处理"""
        # 预处理书籍数据
        return book_data
    
    async def after_export(self, export_result):
        """导出后处理"""
        # 后处理导出结果
        return export_result
```

### 2. 钩子注册

```python
# 注册钩子
from weread_exporter.hooks import register_hook

hook = ExportHook()
register_hook("export", hook)
```

## 测试扩展

### 1. 单元测试

为扩展功能编写测试：

```python
# tests/test_custom_exporter.py
import pytest
from weread_exporter.export import CustomExporter

class TestCustomExporter:
    """自定义导出器测试"""
    
    @pytest.mark.asyncio
    async def test_custom_export(self):
        """测试自定义导出"""
        exporter = CustomExporter(mock_book_data)
        result = await exporter.export()
        
        assert result is not None
        assert isinstance(result, str)
```

### 2. 集成测试

```python
# tests/integration/test_plugins.py
import pytest
from weread_exporter.plugins import get_plugin

class TestPlugins:
    """插件集成测试"""
    
    def test_plugin_registration(self):
        """测试插件注册"""
        plugin = get_plugin("custom_exporter")
        assert plugin is not None
```

## 最佳实践

### 1. 代码规范
- 遵循PEP 8代码风格
- 使用类型注解
- 编写完整的文档字符串

### 2. 错误处理
- 实现适当的异常处理
- 提供清晰的错误信息
- 记录详细的日志

### 3. 性能考虑
- 避免阻塞操作
- 使用异步编程
- 优化内存使用

## 发布扩展

### 1. 打包扩展

创建独立的扩展包：

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="weread-exporter-custom",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "weread-exporter>=1.0.0",
    ],
    entry_points={
        'weread_exporter.plugins': [
            'custom = custom_plugin:CustomPlugin',
        ],
    },
)
```

### 2. 分发扩展

- 发布到PyPI
- 提供安装说明
- 维护更新日志

通过以上扩展机制，您可以灵活地定制微信读书导出工具的功能，满足特定的使用需求。