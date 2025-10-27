# 项目介绍

## 概述

微信读书导出工具是一个功能强大的Python命令行工具，专门用于将微信读书平台上的书籍内容高质量地导出为多种电子书格式。通过创新的Canvas Hook技术，本工具能够突破微信读书的内容保护机制，实现近乎完美的内容导出效果。

## 🎯 核心特性

### 多格式支持
- **EPUB**: 适合移动设备阅读的标准电子书格式
- **PDF**: 适合打印和桌面阅读的便携格式
- **MOBI**: Kindle设备专用格式
- **TXT**: 纯文本格式，兼容性最佳
- **Markdown**: 便于编辑和版本控制的格式

### 高质量渲染
- **文本保真**: 通过Canvas Hook技术获取原始渲染内容
- **样式保留**: 完整保留字体、颜色、大小等样式信息
- **智能解析**: 自动识别标题、代码块、图片等元素
- **结构优化**: 智能章节划分和目录生成

### 高级功能
- **批量处理**: 支持书单批量导出
- **断点续传**: 支持中断后继续导出
- **自定义样式**: 可自定义CSS样式文件
- **多语言支持**: 支持中英文内容导出

## 🔬 技术原理

### Canvas Hook技术

微信读书使用Canvas渲染文本内容以防止内容被轻易复制。本工具通过以下技术突破这一限制：

#### 1. JavaScript注入
在页面加载时注入自定义脚本，拦截Canvas的渲染过程：

```javascript
// 拦截Canvas的getContext方法
HTMLCanvasElement.prototype.getContext = function (type) {
    const ctx = originalGetContext.call(this, type);
    
    // 创建代理对象拦截Canvas操作
    return new Proxy(ctx, {
        get(target, property) {
            if (property === 'fillText') {
                return function(...args) {
                    // 在绘制文本前进行拦截
                    interceptText(args[0], this.font, this.fillStyle);
                    return target[property].apply(this, args);
                };
            }
            return target[property];
        }
    });
};
```

#### 2. 样式分析算法
通过分析Canvas的绘制参数识别文本结构：

```python
def analyze_text_style(text, font, color):
    """分析文本样式并转换为Markdown格式"""
    
    # 解析字体大小
    font_size = extract_font_size(font)
    
    # 识别标题
    if font_size >= 27:
        return f"\n\n# {text}\n"
    elif font_size >= 23:
        return f"\n\n## {text}\n"
    
    # 识别高亮文本
    if color != default_color:
        return f"`{text}`"
    
    return text
```

#### 3. 实时转换机制
在Canvas绘制过程中实时将内容转换为结构化格式：

```javascript
class CanvasInterceptor {
    constructor() {
        this.markdown = '';
        this.currentStyle = {};
    }
    
    interceptFillText(text, x, y) {
        // 根据当前样式决定Markdown格式
        const formatted = this.formatText(text);
        this.markdown += formatted;
    }
    
    formatText(text) {
        const { fontSize, fontColor } = this.currentStyle;
        
        // 标题识别
        if (fontSize >= 27) return `\n\n# ${text}\n`;
        if (fontSize >= 23) return `\n\n## ${text}\n`;
        
        // 代码块识别
        if (this.isCodeBlock(text)) return `\n\`\`\`\n${text}\n\`\`\`\n`;
        
        return text;
    }
}
```

### 异步处理架构

项目采用全异步架构确保高性能：

```python
async def export_book(book_id, formats):
    """异步导出书籍"""
    
    # 创建浏览器实例
    page = WeReadWebPage(book_id)
    await page.launch(headless=True)
    
    try:
        # 并发处理章节
        tasks = []
        for chapter in await page.get_chapters():
            task = export_chapter(page, chapter)
            tasks.append(task)
        
        # 等待所有章节完成
        chapters = await asyncio.gather(*tasks)
        
        # 格式转换
        for fmt in formats:
            if fmt == 'epub':
                await create_epub(chapters)
            elif fmt == 'pdf':
                await create_pdf(chapters)
                
    finally:
        await page.close()
```

## 🏗️ 系统架构

### 核心组件

```
weread-exporter/
├── 📁 weread_exporter/     # 核心模块
│   ├── __main__.py        # 命令行入口
│   ├── webpage.py         # 网页控制模块
│   ├── export.py          # 导出处理模块
│   ├── utils.py           # 工具函数
│   └── hook.js           # Canvas拦截脚本
├── 📁 scripts/           # 辅助脚本
├── 📁 tests/             # 测试文件
└── 📁 docs/              # 文档目录
```

### 数据流程

1. **初始化阶段**
   - 解析命令行参数
   - 启动浏览器实例
   - 注入Hook脚本

2. **内容获取阶段**
   - 导航到书籍页面
   - 拦截Canvas渲染
   - 实时转换内容

3. **格式转换阶段**
   - 生成Markdown中间格式
   - 转换为目标格式（EPUB/PDF/MOBI）
   - 应用自定义样式

4. **清理阶段**
   - 关闭浏览器实例
   - 清理临时文件
   - 生成输出文件

## 🎨 设计理念

### 用户体验优先
- **简单易用**: 一行命令完成导出
- **灵活配置**: 丰富的命令行选项
- **错误友好**: 详细的错误信息和解决方案

### 技术先进性
- **现代技术栈**: 基于Python 3.7+和最新Web技术
- **异步处理**: 充分利用现代CPU多核能力
- **模块化设计**: 易于维护和扩展

### 质量保证
- **完整测试**: 单元测试和集成测试覆盖
- **代码规范**: 遵循PEP 8编码规范
- **文档完善**: 详细的API文档和使用指南

## 📊 性能指标

### 处理速度
- **单本书籍**: 平均2-5分钟（取决于章节数量）
- **批量处理**: 支持并发处理多本书籍
- **内存使用**: 优化内存管理，避免内存泄漏

### 输出质量
- **文本准确率**: 99%+的文本识别准确率
- **样式保留**: 完整保留原始样式信息
- **格式兼容**: 兼容主流阅读器和设备

## 🔮 未来规划

### 短期目标
- 优化Hook算法提高识别准确率
- 增加更多输出格式支持
- 改进错误处理和用户反馈

### 长期愿景
- 支持更多在线阅读平台
- 开发图形界面版本
- 构建云端服务版本

## 🤝 开源精神

本项目遵循MIT开源协议，欢迎社区贡献：

- **代码贡献**: 提交Pull Request改进功能
- **文档改进**: 帮助完善文档和教程
- **问题反馈**: 报告Bug和提出功能建议
- **技术分享**: 分享使用经验和最佳实践

---

**准备好开始使用了吗？** 继续阅读[安装指南](installation.md)开始您的导出之旅！ 🚀