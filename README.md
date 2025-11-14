# 微信读书导出工具

一个功能强大的Python工具，用于将微信读书内容高质量导出为多种电子书格式（EPUB、PDF、MOBI、TXT、Markdown）。

## ✨ 特性

- 🎯 **多格式支持**: EPUB、PDF、MOBI、TXT、Markdown
- 🔬 **Canvas Hook技术**: 突破内容保护，获取原始渲染内容
- 🚀 **高质量输出**: 完整保留样式、图片和结构
- ⚡ **异步处理**: 高性能并发导出
- 🎨 **样式定制**: 支持自定义CSS和主题
- 📚 **批量处理**: 支持书单批量导出
- 🔧 **开发者友好**: 完整的API和扩展支持

## 📖 文档

完整的文档体系已重新整理，请访问 [docs目录](./docs/) 获取详细指南：

### 快速开始
- [📚 文档中心](./docs/README.md) - 完整文档索引
- [🚀 项目介绍](./docs/introduction.md) - 技术原理和特性
- [⚡ 安装指南](./docs/installation.md) - 环境配置和安装
- [🎯 使用教程](./docs/usage.md) - 基础使用方法

### 深入使用
- [🔧 高级功能](./docs/advanced.md) - 高级配置和自定义
- [📚 批量处理](./docs/batch.md) - 批量导出指南
- [🎨 样式定制](./docs/styling.md) - 自定义样式和主题

### 开发指南
- [🏗️ 架构解析](./docs/architecture.md) - 技术架构和实现
- [💻 API文档](./docs/api.md) - 完整API接口说明
- [🔬 开发指南](./docs/development.md) - 开发环境和扩展

### 故障排除
- [🔧 故障排除](./docs/troubleshooting.md) - 问题诊断和解决

## 🚀 快速开始

### 安装

```bash
# 从PyPI安装
pip install weread-exporter

# 或从源码安装
git clone https://github.com/drunkdream/weread-exporter.git
cd weread-exporter
pip install -e .
```

### 基本使用

```bash
# 导出单本书籍
weread-exporter -b 书籍ID -o epub -o pdf

# 获取书籍ID: 从微信读书URL中提取
# 示例: https://weread.qq.com/web/bookDetail/08232ac0720befa90825d88
# 书籍ID: 08232ac0720befa90825d88
```

## 🛠️ 技术栈

- **Python 3.7+** - 核心编程语言
- **Pyppeteer** - 浏览器自动化控制
- **BeautifulSoup4** - HTML解析处理
- **EbookLib** - EPUB格式生成
- **WeasyPrint** - PDF格式渲染
- **AIOHTTP** - 异步HTTP请求
- **Markdown** - Markdown格式处理

## 📋 系统要求

- **操作系统**: Windows 10+/macOS 10.15+/Ubuntu 18.04+
- **Python**: 3.7 或更高版本
- **浏览器**: Chrome/Chromium 90+
- **内存**: 4GB RAM（推荐8GB）

## 🤝 贡献

欢迎贡献代码和改进建议！请参考：[开发指南](./docs/development.md)

## ⚖️ 免责声明

本工具仅供技术研究和学习使用，请遵守以下原则：

1. **尊重版权**: 仅用于个人学习，不得用于商业用途
2. **合理使用**: 不要对服务器造成过大压力
3. **遵守协议**: 遵守微信读书的用户协议
4. **责任自负**: 使用本工具产生的任何问题由使用者自行承担

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**开始您的微信读书导出之旅吧！** 🎉
