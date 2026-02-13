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

**📚 完整文档体系**：请访问 [docs/README.md](./docs/README.md) 获取三层学习路径的完整指南。

### 快速开始（推荐）
- [📚 文档中心](./docs/README.md) - 三条学习路径完整索引
- [🚀 快速开始指南](./docs/user-guide/level1-getting-started.md) - 30分钟完成第一个导出

### 用户路径
| 级别 | 内容 | 预计时间 |
|------|------|----------|
| ⭐ | [安装与配置](./docs/user-guide/level1-getting-started.md) | 30分钟 |
| ⭐⭐ | [核心功能](./docs/user-guide/level2-core-features.md) | 1-2小时 |
| ⭐⭐⭐ | [高级使用](./docs/user-guide/level3-advanced-usage.md) | 2-3小时 |
| ⭐⭐⭐⭐ | [批量与自动化](./docs/user-guide/level4-automation.md) | 3-4小时 |

### 开发者路径
| 级别 | 内容 | 预计时间 |
|------|------|----------|
| ⭐ | [项目概览](./docs/developer-guide/level1-overview.md) | 1小时 |
| ⭐⭐ | [模块详解](./docs/developer-guide/level2-modules.md) | 2-3小时 |
| ⭐⭐⭐ | [开发指南](./docs/developer-guide/level3-development.md) | 2-3小时 |
| ⭐⭐⭐⭐ | [贡献指南](./docs/developer-guide/level4-contributing.md) | 3-4小时 |

### 进阶路径
| 级别 | 内容 | 预计时间 |
|------|------|----------|
| ⭐ | [架构设计](./docs/mastery-guide/level1-architecture.md) | 1-2小时 |
| ⭐⭐ | [设计模式](./docs/mastery-guide/level2-patterns.md) | 2-3小时 |
| ⭐⭐⭐ | [深度技术](./docs/mastery-guide/level3-deep-dive.md) | 3-4小时 |
| ⭐⭐⭐⭐ | [架构决策](./docs/mastery-guide/level4-decisions.md) | 4-5小时 |

### 辅助资源
- [📖 术语表](./docs/glossary.md) - 技术术语中英对照
- [🔧 快速参考文档](./docs/introduction.md) - 旧版简要介绍

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
