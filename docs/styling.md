# 样式定制

## 概述

微信读书导出工具支持高度自定义的样式配置，让您能够创建符合个人喜好的电子书外观。本章将详细介绍各种样式定制选项。

## 基础样式配置

### 1. 使用自定义CSS文件

#### 创建自定义CSS

```css
/* custom.css */

/* 基础样式 */
body {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333333;
    background-color: #ffffff;
    margin: 0;
    padding: 20px;
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    font-weight: 600;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3em;
}

h1 {
    font-size: 2.2em;
    border-bottom: 2px solid #eaecef;
}

h2 {
    font-size: 1.8em;
}

h3 {
    font-size: 1.5em;
}

/* 段落样式 */
p {
    margin: 1em 0;
    text-align: justify;
    text-justify: inter-ideograph;
}

/* 链接样式 */
a {
    color: #0366d6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* 代码样式 */
code {
    background-color: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 3px;
    padding: 0.2em 0.4em;
    font-family: "SFMono-Regular", "Consolas", "Liberation Mono", monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 3px;
    padding: 1em;
    overflow: auto;
}

pre code {
    background: none;
    border: none;
    padding: 0;
}

/* 引用样式 */
blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 1em;
    margin-left: 0;
    color: #6a737d;
    background-color: #fafbfc;
    padding: 0.5em 1em;
}

/* 列表样式 */
ul, ol {
    margin: 1em 0;
    padding-left: 2em;
}

li {
    margin: 0.5em 0;
}

/* 表格样式 */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
}

/* 图片样式 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

#### 应用自定义CSS

```bash
# 导出时使用自定义CSS
weread-exporter -b BOOK_ID -o epub --css-file custom.css

# 同时应用于多种格式
weread-exporter -b BOOK_ID -o epub pdf --css-file custom.css

# 使用多个CSS文件
weread-exporter -b BOOK_ID -o epub --css-file style1.css --css-file style2.css
```

### 2. 内置主题

工具提供多个内置主题：

```bash
# 使用内置主题
weread-exporter -b BOOK_ID -o epub --theme light        # 浅色主题（默认）
weread-exporter -b BOOK_ID -o epub --theme dark         # 深色主题
weread-exporter -b BOOK_ID -o epub --theme sepia        # 护眼主题
weread-exporter -b BOOK_ID -o epub --theme night        # 夜间模式
weread-exporter -b BOOK_ID -o epub --theme professional # 专业主题
```

## 高级样式定制

### 1. 响应式设计

```css
/* responsive.css */

/* 基础响应式设计 */
@media (max-width: 768px) {
    body {
        font-size: 14px;
        padding: 10px;
    }
    
    h1 {
        font-size: 1.8em;
    }
    
    h2 {
        font-size: 1.5em;
    }
    
    pre {
        font-size: 0.8em;
    }
}

@media (max-width: 480px) {
    body {
        font-size: 13px;
        padding: 5px;
    }
    
    h1 {
        font-size: 1.6em;
    }
    
    /* 移动端优化表格 */
    table {
        display: block;
        overflow-x: auto;
    }
}

/* 打印样式 */
@media print {
    body {
        font-size: 12pt;
        line-height: 1.4;
        color: #000;
        background: #fff;
    }
    
    a {
        color: #000;
        text-decoration: underline;
    }
    
    /* 隐藏不必要的元素 */
    .no-print {
        display: none !important;
    }
}
```

### 2. 字体定制

```css
/* fonts.css */

/* 中文字体栈 */
body {
    font-family: 
        "Microsoft YaHei",       /* Windows */
        "PingFang SC",            /* macOS */
        "Hiragino Sans GB",       /* macOS 备选 */
        "WenQuanYi Micro Hei",    /* Linux */
        "Noto Sans CJK SC",        /* 通用 */
        sans-serif;
}

/* 英文字体栈 */
code, pre, .code {
    font-family: 
        "SFMono-Regular",         /* macOS */
        "Consolas",               /* Windows */
        "Liberation Mono",        /* Linux */
        "Menlo",                  /* macOS 备选 */
        "Courier New",            /* 通用备选 */
        monospace;
}

/* 自定义字体嵌入 */
@font-face {
    font-family: 'CustomFont';
    src: url('fonts/custom-font.woff2') format('woff2'),
         url('fonts/custom-font.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}

.custom-font {
    font-family: 'CustomFont', sans-serif;
}
```

### 3. 颜色主题系统

```css
/* theme-system.css */

:root {
    /* 浅色主题变量 */
    --bg-color: #ffffff;
    --text-color: #333333;
    --heading-color: #2c3e50;
    --link-color: #0366d6;
    --border-color: #eaecef;
    --code-bg: #f6f8fa;
    --quote-bg: #fafbfc;
}

/* 深色主题 */
[data-theme="dark"] {
    --bg-color: #1a1a1a;
    --text-color: #e0e0e0;
    --heading-color: #ffffff;
    --link-color: #58a6ff;
    --border-color: #30363d;
    --code-bg: #0d1117;
    --quote-bg: #161b22;
}

/* 护眼主题 */
[data-theme="sepia"] {
    --bg-color: #fbf0d9;
    --text-color: #5f4b32;
    --heading-color: #3e2f1f;
    --link-color: #d35400;
    --border-color: #d4c4a8;
    --code-bg: #f0e6cc;
    --quote-bg: #f5ebd4;
}

/* 应用主题变量 */
body {
    background-color: var(--bg-color);
    color: var(--text-color);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--heading-color);
    border-bottom-color: var(--border-color);
}

a {
    color: var(--link-color);
}

code, pre {
    background-color: var(--code-bg);
    border-color: var(--border-color);
}

blockquote {
    background-color: var(--quote-bg);
    border-left-color: var(--border-color);
}
```

## 格式特定样式

### 1. EPUB样式优化

```css
/* epub-specific.css */

/* EPUB特定样式 */
@namespace epub "http://www.idpf.org/2007/ops";

/* 章节标题 */
chapter title {
    display: block;
    text-align: center;
    margin: 2em 0 1em 0;
    font-size: 1.8em;
}

/* 页眉页脚 */
@page {
    margin: 1cm;
    
    @top-center {
        content: string(book-title);
        font-size: 0.8em;
        color: #666;
    }
    
    @bottom-center {
        content: counter(page);
        font-size: 0.8em;
    }
}

/* 目录样式 */
nav#toc ol {
    list-style-type: none;
    padding-left: 0;
}

nav#toc li {
    margin: 0.5em 0;
}

nav#toc a {
    text-decoration: none;
    color: inherit;
}

/* 封面样式 */
cover {
    page: cover;
}

@page cover {
    margin: 0;
}
```

### 2. PDF样式优化

```css
/* pdf-specific.css */

/* PDF特定样式 */
@page {
    size: A4;
    margin: 2cm 1.5cm;
    
    @top-left {
        content: element(heading);
        font-size: 0.8em;
        color: #666;
    }
    
    @bottom-center {
        content: "第 " counter(page) " 页";
        font-size: 0.8em;
        color: #666;
    }
}

/* 分页控制 */
h1, h2, h3 {
    page-break-after: avoid;
}

p, ul, ol {
    page-break-inside: avoid;
}

/* 避免在标题前分页 */
h1 + p, h2 + p, h3 + p {
    page-break-before: avoid;
}

/* 图片分页控制 */
img {
    page-break-inside: avoid;
    page-break-after: avoid;
}

/* 代码块分页控制 */
pre {
    page-break-inside: avoid;
}
```

### 3. MOBI样式优化

```css
/* mobi-specific.css */

/* MOBI/Kindle特定样式 */
body {
    /* Kindle设备优化 */
    margin: 0;
    padding: 1em;
    -webkit-text-size-adjust: 100%;
}

/* Kindle字体优化 */
body {
    font-family: "Bookerly", "Helvetica", "Arial", sans-serif;
}

code, pre {
    font-family: "Courier", monospace;
}

/* Kindle图片优化 */
img {
    max-width: 100%;
    height: auto;
}

/* Kindle链接样式 */
a {
    color: inherit;
    text-decoration: none;
}

/* Kindle目录优化 */
.kindle-toc {
    margin: 2em 0;
}

.kindle-toc li {
    margin: 0.5em 0;
}
```

## 高级特效和动画

### 1. 过渡动画

```css
/* animations.css */

/* 平滑过渡效果 */
* {
    transition: color 0.3s ease, background-color 0.3s ease;
}

/* 页面切换动画 */
.page {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 交互效果 */
a {
    transition: color 0.2s ease;
}

a:hover {
    color: #d35400;
    transform: translateY(-1px);
}

/* 代码高亮动画 */
code {
    transition: all 0.3s ease;
}

code:hover {
    background-color: #e8f4fd;
    transform: scale(1.02);
}
```

### 2. 高级排版特性

```css
/* typography.css */

/* 高级排版特性 */
body {
    /* 连字符支持 */
    hyphens: auto;
    hyphenate-limit-chars: 6 3 2;
    hyphenate-limit-lines: 2;
    
    /* 文本渲染优化 */
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    
    /* 字距和行距优化 */
    letter-spacing: 0.01em;
    word-spacing: 0.05em;
}

/* 首字下沉 */
p:first-of-type::first-letter {
    initial-letter: 3;
    font-weight: bold;
    margin-right: 0.5em;
    color: #2c3e50;
}

/* 段落首行缩进 */
p {
    text-indent: 2em;
}

/* 避免孤行和寡行 */
p {
    orphans: 3;
    widows: 3;
}

/* 文本对齐优化 */
p {
    text-align: justify;
    text-justify: inter-ideograph;
}
```

## 样式配置管理

### 1. 样式配置文件

创建样式配置文件管理多个主题：

```yaml
# styles/config.yaml

themes:
  light:
    name: "浅色主题"
    description: "默认浅色主题"
    css_files:
      - "themes/light/base.css"
      - "themes/light/typography.css"
    variables:
      primary-color: "#0366d6"
      bg-color: "#ffffff"
  
  dark:
    name: "深色主题"
    description: "夜间阅读主题"
    css_files:
      - "themes/dark/base.css"
      - "themes/dark/typography.css"
    variables:
      primary-color: "#58a6ff"
      bg-color: "#1a1a1a"
  
  professional:
    name: "专业主题"
    description: "商务文档风格"
    css_files:
      - "themes/professional/base.css"
      - "themes/professional/typography.css"
    variables:
      primary-color: "#2c3e50"
      bg-color: "#f8f9fa"

formats:
  epub:
    base_styles:
      - "formats/epub/base.css"
    themes:
      light: "formats/epub/light.css"
      dark: "formats/epub/dark.css"
  
  pdf:
    base_styles:
      - "formats/pdf/base.css"
    themes:
      light: "formats/pdf/light.css"
      dark: "formats/pdf/dark.css"
```

### 2. 样式构建系统

创建样式构建脚本：

```python
#!/usr/bin/env python3
# build_styles.py

import yaml
import os
from pathlib import Path

class StyleBuilder:
    def __init__(self, config_file="styles/config.yaml"):
        self.config = self.load_config(config_file)
        self.output_dir = Path("dist/styles")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def build_theme(self, theme_name, format_name=None):
        """构建主题样式"""
        theme_config = self.config['themes'][theme_name]
        
        css_content = []
        
        # 添加基础样式
        for css_file in theme_config['css_files']:
            if os.path.exists(css_file):
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content.append(f.read())
        
        # 添加格式特定样式
        if format_name and format_name in self.config['formats']:
            format_config = self.config['formats'][format_name]
            if theme_name in format_config['themes']:
                theme_file = format_config['themes'][theme_name]
                if os.path.exists(theme_file):
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        css_content.append(f.read())
        
        # 应用主题变量
        css_content.append(self.generate_css_variables(theme_config['variables']))
        
        # 保存构建结果
        output_file = self.output_dir / f"{theme_name}.css"
        if format_name:
            output_file = self.output_dir / f"{format_name}_{theme_name}.css"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(css_content))
        
        return output_file
    
    def generate_css_variables(self, variables):
        """生成CSS变量"""
        css_vars = [":root {"]
        for key, value in variables.items():
            css_vars.append(f"  --{key}: {value};")
        css_vars.append("}")
        return '\n'.join(css_vars)
    
    def build_all(self):
        """构建所有主题"""
        built_files = []
        
        for theme_name in self.config['themes']:
            # 构建通用主题
            built_files.append(self.build_theme(theme_name))
            
            # 构建格式特定主题
            for format_name in self.config['formats']:
                built_files.append(self.build_theme(theme_name, format_name))
        
        return built_files

if __name__ == "__main__":
    builder = StyleBuilder()
    files = builder.build_all()
    print(f"构建完成: {len(files)} 个样式文件")
```

## 实用样式模板

### 1. 学术论文样式

```css
/* academic.css */

body {
    font-family: "Times New Roman", "SimSun", serif;
    font-size: 12pt;
    line-height: 1.5;
    max-width: 21cm;
    margin: 0 auto;
    padding: 2.5cm;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Arial", "SimHei", sans-serif;
    font-weight: bold;
}

h1 {
    font-size: 16pt;
    text-align: center;
    margin: 2em 0 1em 0;
}

h2 {
    font-size: 14pt;
    border-bottom: 1px solid #000;
    padding-bottom: 0.3em;
}

p {
    text-align: justify;
    text-indent: 2em;
    margin: 1em 0;
}

/* 参考文献样式 */
.references {
    font-size: 10pt;
    line-height: 1.3;
}

.references li {
    margin: 0.5em 0;
    text-indent: -2em;
    padding-left: 2em;
}
```

### 2. 技术文档样式

```css
/* technical.css */

body {
    font-family: "Helvetica Neue", "PingFang SC", sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #24292e;
    background-color: #ffffff;
}

code, pre {
    font-family: "SFMono-Regular", "Consolas", monospace;
    background-color: #f6f8fa;
    border-radius: 3px;
}

pre {
    padding: 1em;
    overflow: auto;
    border-left: 4px solid #0366d6;
}

/* API文档样式 */
.api-method {
    background-color: #f1f8ff;
    border: 1px solid #c8e1ff;
    border-radius: 3px;
    padding: 1em;
    margin: 1em 0;
}

.api-method .method {
    font-weight: bold;
    color: #0366d6;
}

/* 代码示例样式 */
.code-example {
    border: 1px solid #e1e4e8;
    border-radius: 3px;
    margin: 1em 0;
}

.code-example .example-header {
    background-color: #f6f8fa;
    padding: 0.5em 1em;
    border-bottom: 1px solid #e1e4e8;
    font-weight: bold;
}

.code-example .example-content {
    padding: 1em;
}
```

### 3. 小说阅读样式

```css
/* novel.css */

body {
    font-family: "楷体", "KaiTi", "SimKai", serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    background-color: #fefefe;
    padding: 2em;
}

h1 {
    font-family: "黑体", "SimHei", sans-serif;
    font-size: 2em;
    text-align: center;
    margin: 2em 0 1em 0;
}

h2 {
    font-family: "黑体", "SimHei", sans-serif;
    font-size: 1.5em;
    text-align: center;
    margin: 2em 0 1em 0;
}

p {
    text-indent: 2em;
    margin: 1em 0;
}

/* 章节开头样式 */
.chapter-start::first-letter {
    initial-letter: 3;
    font-weight: bold;
    color: #8b0000;
    margin-right: 0.5em;
}

/* 对话样式 */
.dialogue {
    margin: 1em 2em;
    font-style: italic;
}

.dialogue::before {
    content: "\201C"; /* 左引号 */
    font-size: 2em;
    color: #666;
    margin-right: 0.2em;
}

.dialogue::after {
    content: "\201D"; /* 右引号 */
    font-size: 2em;
    color: #666;
    margin-left: 0.2em;
}
```

## 样式调试和优化

### 1. 样式调试工具

创建样式调试助手：

```python
#!/usr/bin/env python3
# style_debugger.py

import cssutils
from pathlib import Path

class StyleDebugger:
    def __init__(self):
        self.parser = cssutils.CSSParser()
    
    def analyze_css(self, css_file):
        """分析CSS文件"""
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        sheet = self.parser.parseString(css_content)
        
        analysis = {
            'file': css_file,
            'rules': len(sheet.cssRules),
            'selectors': [],
            'properties': {},
            'errors': []
        }
        
        for rule in sheet.cssRules:
            if rule.type == rule.STYLE_RULE:
                analysis['selectors'].append(rule.selectorText)
                
                for property in rule.style:
                    prop_name = property.name
                    prop_value = property.value
                    
                    if prop_name not in analysis['properties']:
                        analysis['properties'][prop_name] = []
                    analysis['properties'][prop_name].append(prop_value)
            
            elif rule.type == rule.UNKNOWN_RULE:
                analysis['errors'].append(f"未知规则: {rule.cssText}")
        
        return analysis
    
    def compare_styles(self, file1, file2):
        """比较两个样式文件"""
        analysis1 = self.analyze_css(file1)
        analysis2 = self.analyze_css(file2)
        
        comparison = {
            'file1': analysis1,
            'file2': analysis2,
            'differences': {}
        }
        
        # 比较选择器
        selectors1 = set(analysis1['selectors'])
        selectors2 = set(analysis2['selectors'])
        
        comparison['differences']['added_selectors'] = selectors2 - selectors1
        comparison['differences']['removed_selectors'] = selectors1 - selectors2
        
        return comparison

if __name__ == "__main__":
    debugger = StyleDebugger()
    
    # 分析样式文件
    analysis = debugger.analyze_css('custom.css')
    print(f"规则数量: {analysis['rules']}")
    print(f"选择器数量: {len(analysis['selectors'])}")
```

---

**样式定制指南到此结束。** 这些样式配置选项让您能够创建完全个性化的阅读体验。继续探索其他文档了解更多功能！ 🎨