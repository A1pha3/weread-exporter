# weread_exporter/

**核心包** - 8个文件, 4个主要模块

## OVERVIEW

微信读书导出的4层架构。每层对应一个文件。

## STRUCTURE

```
weread_exporter/
├── __init__.py          # VERSION = "1.0.0"
├── __main__.py          # CLI 入口, 252行
├── export.py            # 导出工作流, 377行
├── webpage.py           # 浏览器自动化, 679行
├── utils.py             # 工具函数, 156行
├── hook.js              # Canvas Hook 注入
├── style.css            # PDF 样式
└── epub.css             # EPUB 样式
```

## MODULES

### `__main__.py` - CLI 层
- **入口**: `main()` → `async_main()` 循环
- **解析器**: argparse 带 `--book-id`, `--output-format`, `--headless`, `--proxy-server` 等
- **书籍检测**: ID中包含 `_` = 书单, 否则为单本书籍
- **导出循环**: launch → export_markdown → pre_process → 格式转换

### `export.py` - 业务层
**WeReadExporter** 类, 377行
- **异步方法**: `export_markdown()`, `pre_process_markdown()`, `markdown_to_*()`
- **文件结构**: `save_dir/{meta.json, chapters/, images/, cover.jpg}`
- **格式转换**:
  - `markdown_to_epub()` → ebooklib, 带锚点的TOC
  - `markdown_to_pdf()` → weasyprint, CSS样式
  - `epub_to_mobi()` → kindlegen (仅Linux)
  - `markdown_to_txt()` → BeautifulSoup 文本提取
- **重试逻辑**: 每章3次尝试, `LoadChapterFailedError`

### `webpage.py` - 浏览器层
**WeReadWebPage** 类, 679行
- **启动**: pyppeteer.launch 带反检测参数
- **注入的反检测**:
  - `navigator.webdriver` 设为 undefined
  - `Object.prototype.hasOwnProperty` 打补丁
  - `navigator.plugins` 伪装 (5个假插件)
  - `navigator.languages` = `['en-US', 'en']`
- **请求拦截**: `setRequestInterception(True)`, 模拟端点:
  - `/web/book/read` → 模拟 synckey
  - `/hera/logkv` → 204 No Content
  - `/sentry_key=` → `{}`
  - `/web/1.392ec47a.js` → 注入 `hook.js`
- **内容提取**: `canvasContextHandler.data.markdown`
- **分页**: `readerFooter_button` 导航

### `utils.py` - 工具层
- **自定义异常**: ChromeNotInstalledError, LoginRequiredError, LoadChapterFailedError, InvalidUserError
- **HTTP**: `fetch()` 带3次重试, aiohttp
- **书单**: `get_book_list()`, `get_book_list_full()` - 解析Nuxt `__INITIAL_STATE__`
- **哈希**: `wr_hash()` - 微信读书特定的书籍ID哈希
- **图片**: `save_to_png()` - Windows PDF 的 PIL 转换

## CONVENTIONS (本目录)

- **全程异步**: export/webpage/utils 中无阻塞I/O
- **异常层次**: 都继承自 `RuntimeError` 或自定义基类
- **导入模式**: `from . import export, utils, webpage` (相对导入)
- **类方法**: 优先使用 `__class__.root_url` 而非硬编码
- **日志前缀**: `[%s] %s` 配合 `self.__class__.__name__`

## ANTI-PATTERNS (本目录)

- `export.py:318-319` - 异步上下文外的同步 `asyncio.sleep()` 调用
- `webpage.py:678` - 已注释的 `clear_cache()` 方法未使用
- webpage.py 中混合关注点 - 请求处理、DOM交互、认证

## ASSETS

| 文件 | 用途 |
|------|------|
| `hook.js` | Canvas Hook - 拦截渲染, 提取markdown |
| `style.css` | PDF样式 - 边距, 字体, 分页 |
| `epub.css` | EPUB样式 - 读者兼容CSS |
| `bin/{linux,win32}/kindlegen` | KindleGen 用于MOBI转换 |
