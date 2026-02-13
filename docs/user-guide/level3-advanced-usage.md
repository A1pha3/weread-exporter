# 高级功能与自定义

> 本文档是用户路径的第三篇，面向已经熟练掌握基础导出的用户。通过阅读和实践本文档，你将学会高级配置技巧、自定义样式方法、性能调优策略，以及解决复杂导出场景的能力。这些技能将帮助你应对各种特殊需求，并优化导出效果。

## 学习目标

完成本章节学习后，你将能够充分利用 weread-exporter 的高级功能，根据特定需求进行定制化配置，并能够调优导出性能。这些进阶能力将使你从普通用户升级为高级用户，能够应对各种复杂的导出需求。

### 基础目标

首先，你将掌握高级配置参数的用法，包括自定义样式、代理配置、多线程设置等。其次，你将学会分析导出过程中的性能瓶颈，并采取相应的优化措施。第三，你将能够处理各种特殊场景，如网络受限环境、大量图片处理、特殊格式书籍等。

### 进阶目标

进阶目标要求你能够设计完整的导出方案，包括工具选择、参数配置、流程优化等。你将学会评估不同方案的效果和成本，并做出最优决策。此外，你还将具备排查复杂问题的能力，能够根据日志和错误信息定位并解决问题。

## 1.1 代理与网络配置

在某些网络环境下，你可能需要通过代理服务器访问微信读书。本节将详细介绍代理配置的方法和注意事项，帮助你在各种网络环境中顺利使用 weread-exporter。

### 1.1.1 HTTP 代理配置

weread-exporter 支持通过 `--proxy-server` 参数指定 HTTP 代理。代理服务器作为中间人，转发你的请求到目标服务器，这在网络受限时非常有用。代理配置的基本语法如下：

```bash
weread-exporter -b 书籍ID --proxy-server http://代理地址:端口
```

常见的代理地址格式包括：`http://127.0.0.1:7890`（本地代理软件如 Clash、V2Ray）、`http://proxy.company.com:8080`（企业代理）、`socks5://127.0.0.1:1080`（SOCKS5 代理）。

需要注意的是，weread-exporter 的代理参数仅影响 Python 发起的 HTTP 请求，不影响 Chrome 浏览器的网络访问。这意味着如果你需要浏览器也通过代理访问，可能需要额外的配置。对于大多数场景，工具本身的代理配置已经足够。

代理认证方面，如果代理服务器需要用户名和密码，地址格式为：`http://用户名:密码@代理地址:端口`。请注意，这种格式会在命令行中暴露密码，存在安全风险。在共享环境中建议使用其他认证方式。

### 1.1.2 系统级代理配置

除了在 weread-exporter 中指定代理，你也可以配置系统级的代理环境变量。这种方式会影响所有使用系统代理的程序，包括 weread-exporter。

Linux 和 macOS 配置方法：

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
weread-exporter -b 书籍ID
```

Windows 配置方法（PowerShell）：

```powershell
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
weread-exporter -b 书籍ID
```

系统级配置的优点是一次设置全局生效，缺点是会影响其他程序。如果只需要为 weread-exporter 使用代理，建议使用命令行参数而非系统配置。

### 1.1.3 网络问题排查

网络问题是导致导出失败的常见原因之一。本节将介绍网络问题的排查方法，帮助你快速定位并解决网络相关的故障。

首先，确认你能够正常访问微信读书网站。在浏览器中打开 https://weread.qq.com，检查是否能正常加载。如果浏览器无法访问，weread-exporter 也无法正常工作。

其次，检查代理配置是否正确。如果使用了代理，尝试关闭代理直接连接，看看问题是否解决。如果是代理引起的问题，需要检查代理服务的可用性和配置正确性。

第三，检查网络延迟和稳定性。高延迟或不稳定的网络会导致页面加载超时。可以使用以下命令测试网络连通性：

```bash
# 测试到微信读书的连接
curl -I https://weread.qq.com

# 测试代理连通性
curl -I --proxy http://代理地址:端口 https://weread.qq.com
```

如果发现网络问题，需要先解决网络问题再进行导出。在网络较差的环境中，建议增加 `--load-timeout` 参数的值，给页面更多加载时间。

## 1.2 自定义 CSS 样式

weread-exporter 允许通过自定义 CSS 样式来控制导出文件的外观。本节将详细介绍 CSS 自定义的方法和常用样式配置，帮助你打造个性化的导出效果。

### 1.2.1 CSS 自定义基础

自定义 CSS 通过 `--css-file` 参数指定，工具会将自定义样式与默认样式合并应用。自定义 CSS 主要影响 PDF 和 EPUB 导出的视觉效果。

```bash
weread-exporter -b 书籍ID -o pdf --css-file custom.css
```

自定义 CSS 的优先级高于默认样式，这意味着你可以覆盖任何默认样式。但为了获得最佳效果，建议只修改必要的样式，避免意外破坏整体布局。

CSS 文件应该包含有效的 CSS 规则。以下是一个简单的自定义 CSS 示例：

```css
/* 自定义字体设置 */
body {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333333;
}

/* 标题样式 */
h1 {
    font-size: 24px;
    font-weight: bold;
    color: #1a1a1a;
    margin-top: 24px;
    margin-bottom: 16px;
}

h2 {
    font-size: 20px;
    font-weight: bold;
    color: #333333;
    margin-top: 20px;
    margin-bottom: 12px;
}

h3 {
    font-size: 18px;
    font-weight: bold;
    color: #444444;
    margin-top: 16px;
    margin-bottom: 10px;
}

/* 代码块样式 */
pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: "SF Mono", "Consolas", "Monaco", monospace;
    font-size: 14px;
    line-height: 1.5;
}

code {
    font-family: "SF Mono", "Consolas", "Monaco", monospace;
    font-size: 14px;
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
}

/* 图片样式 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 16px auto;
}

/* 引用块样式 */
blockquote {
    border-left: 4px solid #dfe2e5;
    color: #6a737d;
    margin: 16px 0;
    padding: 0 16px;
}
```

### 1.2.2 针对不同格式的样式优化

不同的输出格式对 CSS 的支持程度不同，需要针对性地调整样式策略。

PDF 格式支持最完整的 CSS 2.1 和部分 CSS 3 特性。WeasyPrint 引擎能够很好地渲染大多数 CSS 属性，包括页面分页、页眉页脚、字体嵌入等。你可以为 PDF 创建专门的优化样式。

EPUB 格式对 CSS 的支持较为有限，某些高级属性可能不被所有阅读器支持。建议使用基本的 CSS 属性，避免依赖特定的阅读器扩展。

Markdown 格式不使用 CSS 样式，自定义 CSS 对其没有影响。如果你需要调整 Markdown 的显示效果，需要在渲染工具中单独配置。

针对 PDF 的特殊样式配置：

```css
/* PDF 页面设置 */
@page {
    size: A4;
    margin: 2cm 1.5cm;
    @top-center {
        content: string(chapter-title);
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #666;
    }
}

/* 封面页样式 */
div.cover {
    page-break-after: always;
}

/* 章节标题 */
.chapter-title {
    string-set: chapter-title content();
}

/* 分页控制 */
.chapter {
    page-break-before: always;
}

/* 表格样式 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: bold;
}
```

### 1.2.3 品牌定制示例

如果你需要为企业或个人品牌定制导出样式，以下是一个完整的品牌定制示例：

```css
/* 品牌定制 CSS */

/* 基础设置 */
body {
    font-family: "BrandFont", "PingFang SC", sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: #2c3e50;
    text-align: justify;
}

/* 品牌颜色 */
:root {
    --brand-primary: #3498db;
    --brand-secondary: #2ecc71;
    --brand-accent: #e74c3c;
    --text-primary: #2c3e50;
    --text-secondary: #7f8c8d;
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
}

/* 标题系统 */
h1 {
    font-size: 28px;
    font-weight: 700;
    color: var(--brand-primary);
    border-bottom: 3px solid var(--brand-primary);
    padding-bottom: 12px;
    margin: 32px 0 24px 0;
}

h2 {
    font-size: 22px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 28px 0 16px 0;
    padding-left: 12px;
    border-left: 4px solid var(--brand-secondary);
}

h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 24px 0 12px 0;
}

/* 强调样式 */
strong, b {
    font-weight: 700;
    color: var(--brand-primary);
}

em, i {
    font-style: italic;
    color: var(--text-secondary);
}

/* 链接样式 */
a {
    color: var(--brand-primary);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* 代码块 */
pre {
    background-color: var(--bg-secondary);
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    font-family: "Source Code Pro", "Consolas", monospace;
    font-size: 13px;
    line-height: 1.6;
}

code {
    font-family: "Source Code Pro", "Consolas", monospace;
    font-size: 0.9em;
    background-color: var(--bg-secondary);
    padding: 2px 5px;
    border-radius: 3px;
}

/* 图片 */
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

figure {
    margin: 24px 0;
    text-align: center;
}

figcaption {
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 8px;
    font-style: italic;
}

/* 引用 */
blockquote {
    margin: 20px 0;
    padding: 12px 20px;
    background-color: var(--bg-secondary);
    border-left: 4px solid var(--brand-accent);
    color: var(--text-secondary);
    font-style: italic;
}

/* 表格 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}

thead {
    background-color: var(--brand-primary);
    color: white;
}

th, td {
    padding: 12px 16px;
    border: 1px solid #ddd;
    text-align: left;
}

tr:nth-child(even) {
    background-color: var(--bg-secondary);
}

/* 水平分隔线 */
hr {
    border: none;
    border-top: 2px solid #e1e4e8;
    margin: 32px 0;
}
```

## 1.3 性能调优

导出大型书籍或批量处理时，性能优化变得尤为重要。本节将介绍各种性能优化技巧，帮助你提高导出效率，减少等待时间。

### 1.3.1 网络性能优化

网络请求是导出过程中最耗时的部分之一。优化网络性能可以从以下几个方面入手。

减少请求间隔是最直接的优化方法。默认的 `--load-interval` 是 30 秒，这在网络较好时可以适当减少：

```bash
# 快速导出（网络好时使用）
weread-exporter -b 书籍ID --load-interval 5
```

但要注意，过短的间隔可能触发服务器的防爬虫机制，导致 IP 被封禁。在不确定的情况下，建议保持较长的间隔。

并行处理方面，weread-exporter 本身是单线程的，但你可以同时运行多个实例来并行导出不同的书籍：

```bash
# 终端 1
weread-exporter -b 书籍ID1 -o epub &
# 终端 2
weread-exporter -b 书籍ID2 -o epub &
# 终端 3
weread-exporter -b 书籍ID3 -o epub &
```

### 1.3.2 缓存利用

weread-exporter 的缓存机制可以显著减少重复工作。理解并善用缓存，是性能优化的重要手段。

如果之前已经导出过某本书，只需要修改样式重新生成，缓存可以避免重新抓取内容：

```bash
# 先完整导出
weread-exporter -b 书籍ID -o epub
# 然后修改 custom.css
# 重新生成（跳过已缓存的章节）
weread-exporter -b 书籍ID -o pdf --css-file custom.css
```

缓存目录的结构设计也便于手动干预。如果某章节导出失败，你可以手动修复后重新运行，工具会跳过已成功的章节。

### 1.3.3 内存与资源优化

在资源受限的环境中，需要注意内存和系统资源的使用。

Chrome 浏览器是资源消耗的大头。减少 Chrome 的资源使用可以：

1. 使用 `--headless` 参数减少窗口渲染开销
2. 减少同时运行的实例数量
3. 在导出完成后及时清理缓存

Python 层面的优化包括：

1. 及时清理 large 字符串
2. 避免在内存中保留不需要的数据
3. 使用生成器处理大文件

### 1.3.4 不同场景的参数配置

不同场景需要不同的参数配置策略。以下是几个典型场景的推荐配置：

**场景一：网络稳定，单本书快速导出**

```bash
weread-exporter -b 书籍ID \
    -o epub \
    -o pdf \
    --load-timeout 60 \
    --load-interval 10 \
    --headless
```

**场景二：网络较慢，需要稳定导出**

```bash
weread-exporter -b 书籍ID \
    -o epub \
    --load-timeout 180 \
    --load-interval 60 \
    --headless
```

**场景三：图片密集的书籍**

```bash
weread-exporter -b 书籍ID \
    -o pdf \
    --load-timeout 120 \
    --load-interval 45 \
    --css-file high-quality-images.css \
    --headless
```

其中 `high-quality-images.css` 可以包含图片优化样式：

```css
img {
    max-width: 100%;
    image-rendering: -webkit-optimize-contrast;
}
```

## 1.4 特殊场景处理

本节将介绍几种特殊场景的处理方法，帮助你应对各种非标准的导出需求。

### 1.4.1 大型书籍处理

对于章节数量很多的大型书籍（如长篇小说、系列丛书），需要特别注意以下几个方面。

首先是超时设置。大型书籍意味着更多的章节，需要更长的总处理时间。建议增加 `--load-timeout`：

```bash
weread-exporter -b 书籍ID \
    --load-timeout 120 \
    --load-interval 30 \
    -o epub
```

其次是分段处理。如果书籍极其庞大（如数千章节），可以考虑分批导出。获取所有章节 ID 后，分多次导出：

```bash
# 假设书籍有章节 ID 列表
# 分三批导出
weread-exporter -b 书籍ID_批次1 -o epub
weread-exporter -b 书籍ID_批次2 -o epub
weread-exporter -b 书籍ID_批次3 -o epub
```

第三是磁盘空间。大型书籍的缓存可能占用数 GB 空间，请确保有足够的磁盘空间。

### 1.4.2 敏感网络环境

在某些网络环境中，访问微信读书可能受到限制。以下是几种应对方法。

使用代理是最常见的解决方案：

```bash
weread-exporter -b 书籍ID \
    --proxy-server http://你的代理地址:端口 \
    --headless
```

如果代理也不能完全解决问题，可能需要考虑网络架构层面的解决方案，如 VPN、企业专线等。这些超出了 weread-exporter 的范畴，需要咨询网络管理员。

### 1.4.3 多账号处理

如果你有多个微信读书账号，需要分别为每个账号导出内容。

每个账号使用独立的 cookie 文件：

```bash
# 账号 A 导出
weread-exporter -b 书籍IDA \
    --cookie cache/cookie_a.txt

# 账号 B 导出
weread-exporter -b 书籍IDB \
    --cookie cache/cookie_b.txt
```

也可以手动复制 cookie 文件来实现账号切换：

```bash
# 复制账号 A 的 cookie
cp cache/cookie_a.txt cache/cookie.txt
weread-exporter -b 书籍IDA

# 切换到账号 B
cp cache/cookie_b.txt cache/cookie.txt
weread-exporter -b 书籍IDB
```

### 1.4.4 书籍格式兼容性

某些特殊格式的书籍可能需要额外处理。

**漫画类书籍**：图片为主，文字为辅。建议使用 PDF 格式导出以保持图片质量：

```bash
weread-exporter -b 漫画ID -o pdf --load-interval 20
```

**技术书籍**：代码块较多，建议使用支持代码高亮的阅读器。EPUB 和 PDF 都能较好地保留代码格式。

**古籍类书籍**：可能包含特殊字符。确保你的阅读器支持 Unicode 字符集，否则可能出现乱码。

**外文书籍**：如果阅读器不支持中文字体，可能需要单独配置字体。

## 1.5 故障深度排查

当遇到复杂问题时，需要进行系统性的排查。本节将介绍故障排查的方法论和实用技巧。

### 1.5.1 日志分析

weread-exporter 的日志包含了丰富的调试信息。学会阅读日志是排查问题的基础。

INFO 级别日志显示正常的执行流程：章节加载进度、文件保存提示等。WARNING 级别日志表示遇到了问题但程序可以继续。ERROR 级别日志表示发生了错误，可能导致功能异常。

```bash
# 显示详细日志
weread-exporter -b 书籍ID -v
weread-exporter -b 书籍ID --verbose

# 最大日志级别
weread-exporter -b 书籍ID -vv
```

分析日志时，重点关注：ERROR 级别的错误信息、异常的堆栈跟踪、超时相关的警告、章节加载失败的位置。

### 1.5.2 常见复杂问题处理

**问题一：部分章节导出失败**

症状：大部分章节正常，个别章节显示错误或缺失。

排查步骤：首先查看日志确定是哪些章节失败；然后检查该章节是否有特殊内容（如视频、互动元素）；尝试单独导出该章节或跳过它。

```bash
# 尝试跳过失败章节继续导出
weread-exporter -b 书籍ID \
    --load-timeout 180 \
    --load-interval 60 \
    -o epub
```

**问题二：图片显示异常**

症状：导出的电子书中有图片缺失、显示错误或位置错乱。

排查步骤：检查 `cache/书籍ID/images/` 目录中的图片文件；确认图片下载成功且格式正确；验证 Markdown 文件中的图片引用路径是否正确。

如果图片缺失，可以手动下载后放入 images 目录，修改 Markdown 文件中的引用路径。

**问题三：格式化错误**

症状：导出文件格式混乱，标题层级错误，段落丢失等。

排查步骤：检查原书是否有特殊结构；尝试不同输出格式看是否问题一致；对比 Markdown 源文件和最终输出。

某些复杂格式（如分栏、嵌套列表）在不同格式中的表现可能不一致，这是正常的技术限制。

### 1.5.3 调试模式

在排查复杂问题时，可以启用调试模式获取更多细节：

```bash
# 显示 Chrome 的开发者工具日志
weread-exporter -b 书籍ID \
    --headless=false \
    --log-level debug
```

调试模式下 Chrome 窗口会显示，你可以直接观察页面加载过程。这对于理解页面行为和定位问题很有帮助。

## 1.6 实践任务

### 任务一：自定义样式创建

**任务目标**：创建一套符合个人审美或品牌需求的自定义样式。

**具体步骤**：分析你的阅读偏好或品牌需求；编写不少于 50 行的自定义 CSS；应用到实际导出中并验证效果。

**验收标准**：自定义 CSS 成功应用，视觉效果符合预期，无布局错乱。

**推荐样式方向**：极简风格、高对比度阅读、深色模式、企业品牌等。

### 任务二：性能优化对比

**任务目标**：对比不同参数配置下的导出性能。

**具体步骤**：选择一本 100 章以上的书籍；使用默认参数记录导出时间；使用优化参数记录导出时间；对比分析差异。

**测试配置**：
```bash
# 默认配置
weread-exporter -b 书籍ID --load-interval 30

# 优化配置
weread-exporter -b 书籍ID --load-interval 5 --headless
```

**验收标准**：记录两次导出的时间、成功率、输出质量，形成对比分析报告。

### 任务三：复杂场景处理

**任务目标**：处理一本特殊类型的书籍（漫画、技术书、古籍等）。

**具体步骤**：选择一本特殊类型的书籍；分析其特殊需求；配置适当的参数和样式；完成导出并验证质量。

**验收标准**：成功处理特殊书籍，导出质量可接受，形成该类型书籍的处理经验总结。

## 1.7 本章小结

本章深入介绍了 weread-exporter 的高级功能，包括网络配置优化、自定义样式方法、性能调优策略、特殊场景处理，以及故障深度排查技术。掌握这些技能后，你应该能够应对各种复杂的导出需求，并能够根据实际情况进行针对性的优化和调整。

完成本章节学习后，考虑以下方向继续深入：如果你对批量处理和自动化更感兴趣，请继续阅读用户路径第四级「批量处理与自动化」；如果你想了解工具的内部实现，请转入开发路径学习；如果你对架构设计和技术原理感兴趣，请阅读进阶路径的相关内容。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 代理服务器 | Proxy Server | 转发网络请求的中间服务器 |
| CSS | Cascading Style Sheets | 层叠样式表，用于描述文档外观 |
| WeasyPrint | WeasyPrint | Python PDF 渲染库 |
| 缓存 | Cache | 存储临时数据以加速重复访问 |
| 超时 | Timeout | 等待响应的最长时间限制 |
