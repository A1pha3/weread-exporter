# 使用教程

## 快速开始

### 1. 获取书籍ID

在开始导出之前，您需要获取目标书籍的ID：

1. 打开微信读书网页版：https://weread.qq.com/
2. 搜索或找到您想要导出的书籍
3. 进入书籍详情页
4. 从URL中提取书籍ID

**示例URL**:
```
https://weread.qq.com/web/bookDetail/08232ac0720befa90825d88
```

**书籍ID**: `08232ac0720befa90825d88`

### 2. 基本导出命令

使用最简单的命令导出书籍：

> **注意**: 如果您使用 `uv` 管理项目，请在命令前加上 `uv run`。

```bash
# 导出为EPUB格式
weread-exporter --book-id 08232ac0720befa90825d88 --output-format epub
# 使用 uv 运行:
# uv run weread-exporter --book-id 08232ac0720befa90825d88 --output-format epub

# 或使用简写参数
weread-exporter -b 08232ac0720befa90825d88 -o epub
```

### 3. 查看导出结果

导出完成后，文件将保存在当前目录的 `output` 文件夹中：

```bash
# 查看输出目录
ls output/
# 输出: 书籍名称.epub

# 打开导出的文件
open output/书籍名称.epub
```

## 命令行参数详解

### 基本参数

| 参数 | 简写 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `--book-id` | `-b` | 书籍ID（当不使用 `--list-booklists` 时必填） | 无 | `-b 08232ac0720befa90825d88` |
| `--output-format` | `-o` | 输出格式（可重复） | epub | `-o epub -o pdf` |
| `--load-timeout` | 无 | 章节加载超时时间（秒） | 60 | `--load-timeout 120` |
| `--load-interval` | 无 | 章节加载间隔时间（秒） | 30 | `--load-interval 10` |
| `--css-file` | 无 | 自定义CSS样式文件 | 无 | `--css-file custom.css` |
| `--headless` | 无 | 无头模式（不显示浏览器） | False | `--headless` |
| `--force-login` | 无 | 强制登录微信读书 | False | `--force-login` |
| `--use-default-profile` | 无 | 使用默认浏览器配置 | False | `--use-default-profile` |
| `--mock-user-agent` | 无 | 模拟用户代理 | False | `--mock-user-agent` |
| `--proxy-server` | 无 | 代理服务器 | 无 | `--proxy-server http://proxy:8080` |
| `--list-ids` | 无 | 从书单打印全部书籍ID（书名/原始ID/哈希ID） | 无 | `-b <booklistId> --list-ids` |
| `--list-booklists` | 无 | 自动列出当前账号的书单（书单名/书单ID/URL） | 无 | `--list-booklists` |
| `--help` | `-h` | 显示帮助信息 | 无 | `-h` |


## 使用示例

### 示例1：导出单本书籍为多种格式

```bash
# 同时导出EPUB、PDF和MOBI格式
weread-exporter -b 08232ac0720befa90825d88 -o epub -o pdf -o mobi

# 使用无头模式导出
weread-exporter -b 08232ac0720befa90825d88 -o epub --headless
```

### 示例2：使用高级配置

```bash
# 使用无头模式，加快导出速度
weread-exporter -b 08232ac0720befa90825d88 -o epub --headless

# 自定义加载参数，适合网络较慢的情况
weread-exporter -b 08232ac0720befa90825d88 -o epub --load-timeout 180 --load-interval 5

# 使用代理服务器
weread-exporter -b 08232ac0720befa90825d88 -o epub --proxy-server http://127.0.0.1:8080
```

### 示例3：批量导出书单

如果您有多个书籍需要导出，可以创建批处理脚本：

```bash
# 创建书籍ID列表文件 books.txt
cat > books.txt << EOF
08232ac0720befa90825d88
1a2b3c4d5e6f7g8h9i0j1k
book_id_3_here
EOF

# 批量导出脚本
while read book_id; do
    echo "正在导出书籍: $book_id"
    weread-exporter -b "$book_id" -o epub -o pdf --headless
    echo "导出完成: $book_id"
    echo "---"
done < books.txt
```

## 输出格式说明

### EPUB格式
- **优点**: 标准电子书格式，支持重排和字体调整
- **适用场景**: 移动设备阅读（手机、平板）
- **文件大小**: 中等，包含图片和样式

### PDF格式
- **优点**: 固定排版，打印效果好
- **适用场景**: 桌面阅读、打印、归档
- **文件大小**: 较大，包含高分辨率图片

### MOBI格式
- **优点**: Kindle设备专用格式
- **适用场景**: Kindle阅读器
- **文件大小**: 中等，需要额外转换

### TXT格式
- **优点**: 纯文本，兼容性最好
- **适用场景**: 快速查看、文本处理
- **文件大小**: 最小，仅包含文本

### Markdown格式
- **优点**: 便于编辑和版本控制
- **适用场景**: 内容编辑、博客发布
- **文件大小**: 较小，结构化文本

## 自定义样式

### 使用自定义CSS

创建自定义CSS文件来调整导出样式：

```css
/* custom.css */
body {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f8f9fa;
}

h1, h2, h3 {
    color: #2c3e50;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3em;
}

code {
    background: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 3px;
    padding: 0.2em 0.4em;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 1em;
    margin-left: 0;
    color: #6a737d;
}
```

使用自定义CSS文件：

```bash
weread-exporter -b 08232ac0720befa90825d88 -o epub --css-file custom.css
```

### 内置样式主题

工具提供多个内置主题：

```bash
# 使用内置主题（未来版本支持）
weread-exporter -b 08232ac0720befa90825d88 -o epub --theme dark
```

## 登录和认证

### 自动登录

首次使用时，工具会自动处理登录：

```bash
# 自动检测登录状态（默认行为）
weread-exporter -b 08232ac0720befa90825d88 -o epub
```

### 强制登录

如果需要重新登录：

```bash
# 强制重新登录
weread-exporter -b 08232ac0720befa90825d88 -o epub --force-login
```

### 登录状态管理

登录信息会保存在本地：

```bash
# 查看登录状态文件（通常位置）
ls ~/.weread/cookies.json

# 清除登录状态
rm ~/.weread/cookies.json
```

## 性能优化技巧

### 1. 使用无头模式

```bash
# 显著提高导出速度
weread-exporter -b 08232ac0720befa90825d88 -o epub --headless
```

### 2. 调整加载参数

```bash
# 网络较慢时增加超时时间
weread-exporter -b 08232ac0720befa90825d88 -o epub --load-timeout 180

# 减少加载间隔加快速度（可能增加被封风险）
weread-exporter -b 08232ac0720befa90825d88 -o epub --load-interval 10
```

### 3. 批量处理优化

```bash
# 使用并发处理（未来版本支持）
weread-exporter --batch books.txt --concurrency 3 -o epub
```

## 常见使用场景

### 场景1：个人阅读备份

```bash
# 备份个人书库中的所有书籍
for book_id in $(cat my_books.txt); do
    weread-exporter -b "$book_id" -o epub -o pdf --headless
    sleep 60  # 避免频繁请求
done
```

### 场景2：学术研究引用

```bash
# 导出参考文献为PDF格式，便于打印和标注
weread-exporter -b research_book_id -o pdf --css-file academic.css
```

### 场景3：内容创作素材

```bash
# 导出为Markdown格式，便于内容编辑
weread-exporter -b source_book_id -o md
```

## 输出文件结构

### 单个书籍导出

```
output/
└── 书籍名称_书籍ID/
    ├── 书籍名称.epub
    ├── 书籍名称.pdf
    ├── 书籍名称.mobi
    ├── images/           # 图片资源
    │   ├── cover.jpg
    │   └── chapter_*.jpg
    └── metadata.json    # 书籍元数据
```

### 批量导出结构

```
output/
├── 2024-10-27_export/
│   ├── book1/
│   ├── book2/
│   └── summary.json     # 批量导出摘要
└── 2024-10-28_export/
    ├── book3/
    └── book4/
```

## 高级功能

### 1. 断点续传

如果导出过程中中断，可以恢复导出：

```bash
# 自动检测缓存并继续导出
weread-exporter -b 08232ac0720befa90825d88 -o epub --resume
```

### 2. 增量导出

只导出新增或修改的章节：

```bash
# 仅导出上次导出后的新内容
weread-exporter -b 08232ac0720befa90825d88 -o epub --incremental
```

### 3. 质量设置

调整导出质量：

```bash
# 高质量模式（文件更大）
weread-exporter -b 08232ac0720befa90825d88 -o pdf --quality high

# 标准质量（默认）
weread-exporter -b 08232ac0720befa90825d88 -o pdf --quality standard

# 压缩模式（文件更小）
weread-exporter -b 08232ac0720befa90825d88 -o pdf --quality compressed
```

## 实用技巧

### 1. 命令行自动补全

设置命令行自动补全（bash/zsh）：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
complete -C 'weread-exporter --complete' weread-exporter
```

### 2. 别名设置

创建命令别名简化使用：

```bash
# 添加到 shell 配置文件
alias wexport='weread-exporter'
alias wex='weread-exporter --headless -o epub -o pdf'
```

### 3. 日志和调试

启用详细日志输出：

```bash
# 显示详细日志
weread-exporter -b 08232ac0720befa90825d88 -o epub --verbose

# 保存日志到文件
weread-exporter -b 08232ac0720befa90825d88 -o epub --log-file export.log
```

## 下一步

掌握了基本用法后，您可以：

1. 🔧 学习[高级功能](advanced.md)实现更复杂的导出需求
2. 📚 了解[批量处理](batch.md)提高工作效率
3. 🎨 探索[样式定制](styling.md)创建个性化输出
4. 🔬 深入[架构解析](architecture.md)理解技术原理

---

**遇到使用问题？** 查看[故障排除指南](troubleshooting.md)获取解决方案！ 🔧
### 示例4：从书单获取全部书籍ID

```bash
# 打印书单内所有书籍的 书名、原始ID、哈希ID
python -m weread_exporter -b my_booklist_123 --list-ids
```

更多说明见 `docs/get-book-ids.md`。

### 示例5：自动获取书单ID

```bash
# 列出当前账号的所有书单（书单名、书单ID、URL）
python -m weread_exporter --list-booklists

# 选择某个书单，打印其中所有书籍ID
python -m weread_exporter -b <booklistId> --list-ids
```