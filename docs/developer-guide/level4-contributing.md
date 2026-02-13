# 扩展与贡献指南

> 本文档是开发路径的第四篇，也是开发路径的最高级别。面向希望深度参与 weread-exporter 项目、为项目贡献代码或进行重大定制的开发者。通过阅读本文档，你将学会如何设计新功能、如何扩展现有模块、如何参与开源社区贡献，以及如何成为项目的长期维护者。

## 学习目标

完成本章节学习后，你将能够设计并实现新功能，理解项目的扩展点和设计原则，并能够为项目做出有价值的贡献。这些能力将帮助你从普通开发者成长为项目的核心贡献者。

### 基础目标

首先，你将掌握项目的扩展点分析，了解在哪些位置可以安全地进行扩展而不影响核心功能。其次，你将学会新功能的设计方法，包括需求分析、接口设计、实现规划等。第三，你将理解开源贡献的完整流程，包括 Issue 报告、PR 提交、代码审查响应等。

### 进阶目标

进阶目标要求你能够设计重大的新功能或模块扩展，能够评估设计决策的长期影响，并能够指导其他开发者参与贡献。你还将学会如何维护项目的长期健康发展，包括版本管理、技术债务处理、社区建设等。

## 1.1 扩展点分析

在不影响核心功能的前提下进行扩展，需要了解项目的扩展点和设计原则。本节将详细分析 weread-exporter 的扩展点。

### 1.1.1 导出格式扩展

weread-exporter 当前支持五种导出格式。如果需要添加新格式（如 AZW3、FBD2 等），可以按照以下步骤进行扩展：

第一步，在参数定义中添加新格式：

```python
# __main__.py
parser.add_argument(
    "-o",
    "--output-format",
    choices=["md", "epub", "pdf", "mobi", "txt", "azw3"],  # 添加新格式
    action="append"
)
```

第二步，在 WeReadExporter 类中添加新方法：

```python
async def markdown_to_azw3(self, save_path, extra_css=None):
    """将 Markdown 转换为 AZW3 格式
    
    Args:
        save_path: 输出文件路径
        extra_css: 额外的 CSS 样式
    """
    # 实现转换逻辑
    # 可以复用 markdown_to_epub 的部分代码
    
    # 保存文件
    with open(save_path, "wb") as fp:
        fp.write(content)
```

第三步，在 async_main 中添加处理逻辑：

```python
if "azw3" in args.output_format:
    save_path = os.path.join(output_dir, "%s.azw3" % title)
    await exporter.markdown_to_azw3(save_path, extra_css=extra_css)
```

### 1.1.2 下载器扩展

当前的下载器使用 aiohttp 进行 HTTP 请求。如果需要支持其他下载方式（如 requests、httpx、playwright 等），可以通过接口抽象来实现：

```python
# 新建 downloader.py

class BaseDownloader:
    """下载器基类"""
    
    async def fetch(self, url: str, **kwargs) -> bytes:
        """获取 URL 内容"""
        raise NotImplementedError


class AioHttpDownloader(BaseDownloader):
    """基于 aiohttp 的下载器"""
    
    async def fetch(self, url: str, **kwargs) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()


class PlaywrightDownloader(BaseDownloader):
    """基于 Playwright 的下载器"""
    
    def __init__(self):
        self.browser = None
    
    async def fetch(self, url: str, **kwargs) -> bytes:
        # Playwright 实现
        pass


# 在 utils.py 中使用
from .downloader import AioHttpDownloader

downloader = AioHttpDownloader()
```

### 1.1.3 存储后端扩展

当前工具将文件保存到本地文件系统。如果需要支持云存储，可以在 WeReadExporter 中添加存储抽象：

```python
# 新建 storage.py

class BaseStorage:
    """存储后端基类"""
    
    def save(self, path: str, content: bytes):
        """保存文件"""
        raise NotImplementedError
    
    def load(self, path: str) -> bytes:
        """加载文件"""
        raise NotImplementedError


class LocalStorage(BaseStorage):
    """本地文件系统存储"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def save(self, path: str, content: bytes):
        full_path = os.path.join(self.base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
    
    def load(self, path: str) -> bytes:
        full_path = os.path.join(self.base_dir, path)
        with open(full_path, "rb") as f:
            return f.read()


class S3Storage(BaseStorage):
    """AWS S3 存储"""
    
    def __init__(self, bucket: str, prefix: str = ""):
        import boto3
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix
    
    def save(self, path: str, content: bytes):
        key = os.path.join(self.prefix, path)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)
    
    def load(self, path: str) -> bytes:
        key = os.path.join(self.prefix, path)
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()
```

## 1.2 新功能设计指南

设计新功能时需要遵循一定的原则和流程。本节将介绍新功能设计的方法论和最佳实践。

### 1.2.1 需求分析

在开始编码之前，需要清晰地定义新功能的需求：

**功能描述**：用一两句话描述新功能的核心价值。例如：「添加批量导出功能，支持一次导出多个书籍」。这个描述应该能够让人快速理解功能的目的。

**用户场景**：描述功能的使用场景和目标用户。例如：「当用户有大量书籍需要导出时，可以使用批量功能节省时间」。明确的用户场景有助于验证功能的必要性。

**输入输出**：定义功能的输入参数和输出结果。例如：「输入是书籍 ID 列表，输出是多个 EPUB 文件保存在指定目录」。

**约束条件**：说明功能的限制和边界条件。例如：「批量导出时，每个书籍独立处理，错误不影响其他书籍」。

### 1.2.2 接口设计

良好的接口设计应该满足以下原则：

**简洁性**：接口应该尽可能简洁，只暴露必要的方法和参数。例如，不要设计一个包含 20 个参数的方法，而是将其拆分为多个方法。

**一致性**：新接口应该与现有接口保持一致的风格。例如，如果现有方法使用 snake_case，新方法也应该使用 snake_case。

**可扩展性**：接口设计应该考虑未来的扩展需求。例如，使用配置对象而非多个参数，便于未来添加新配置。

**向后兼容性**：尽量不要修改现有接口的签名，而是在需要时添加新方法。

```python
# 良好接口设计示例

# 不好：参数过多，难以使用
def export_book(book_id, output_format, timeout, interval, 
                proxy, user_agent, css_file, callback, 
                retry_count, retry_interval, **kwargs):
    pass

# 好：使用配置对象
@dataclass
class ExportConfig:
    book_id: str
    output_format: str = "epub"
    timeout: int = 60
    interval: int = 30
    proxy: str | None = None
    user_agent: str | None = None
    css_file: str | None = None
    retry_count: int = 3
    retry_interval: int = 5

async def export_book(config: ExportConfig, callback=None):
    """导出书籍
    
    Args:
        config: 导出配置
        callback: 进度回调函数 (progress: float, status: str)
    """
    pass
```

### 1.2.3 实现规划

实现新功能时，建议按照以下步骤进行：

第一步，实现最小可行版本（MVP），只包含核心功能。MVP 应该能够正常工作，但不一定是完美的。

第二步，添加错误处理和边界情况处理。确保功能在各种异常情况下都能优雅地处理。

第三步，优化性能和用户体验。例如，添加进度显示、缓存支持等。

第四步，编写文档和测试。确保功能有清晰的文档说明和完整的测试覆盖。

### 1.2.4 设计文档模板

新功能的设计应该写成文档，便于审查和后续维护：

```markdown
# 功能设计文档：[功能名称]

## 概述
[功能的一到两句话描述]

## 动机
- [为什么需要这个功能]
- [解决了什么问题]
- [用户需求来源]

## 设计方案

### 架构图
[如果有复杂的架构变化，添加架构图]

### API 设计
```python
# 接口定义示例
```

### 数据流
[描述数据如何流动]

### 边界情况
- [边界情况 1]
- [边界情况 2]

## 实现计划

### 第一阶段：MVP
- [ ] 任务 1
- [ ] 任务 2

### 第二阶段：完善
- [ ] 任务 3
- [ ] 任务 4

## 测试计划
- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试用例

## 风险与应对
| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 风险 1 | 影响范围 | 应对方法 |

## 开放问题
- [ ] 待解决问题 1
- [ ] 待解决问题 2
```

## 1.3 开源社区参与

参与开源社区是提升技术能力的好方法。本节将介绍如何积极参与 weread-exporter 项目的开源社区。

### 1.3.1 Issue 报告

高质量的 Issue 报告能够帮助维护者快速理解和解决问题。报告 Issue 时应该包含：

**问题描述**：清晰描述遇到的问题，包括预期行为和实际行为。例如：「导出 EPUB 时，章节顺序错乱，期望按照章节编号排序，实际输出随机排序」。

**复现步骤**：详细的步骤说明，让维护者能够复现问题。例如：「1. 登录微信读书；2. 打开书籍 X；3. 点击导出 EPUB；4. 检查章节顺序」。

**环境信息**：操作系统、Python 版本、Chrome 版本等。例如：「macOS 13.0，Python 3.11.4，Chrome 116.0.5845.96」。

**日志信息**：如果可能，附上错误日志。例如，添加 `--verbose` 参数获取详细输出。

**截图**：如果问题涉及界面或输出格式，添加截图说明。

```markdown
## Issue 报告模板

### 问题类型
- [ ] Bug 报告
- [ ] 功能请求
- [ ] 问题咨询
- [ ] 文档改进

### 问题描述
[详细描述问题]

### 复现步骤
1. [步骤 1]
2. [步骤 2]
3. [...]

### 预期行为
[描述期望的正确行为]

### 实际行为
[描述实际发生的行为]

### 环境信息
- 操作系统：[如 Windows 11/macOS 13/Ubuntu 22.04]
- Python 版本：[如 3.11.4]
- weread-exporter 版本：[如 1.0.0]
- Chrome 版本：[如 116.0.5845.96]

### 日志输出
```
[粘贴日志内容]
```

### 截图
[如果适用，添加截图]

### 其他信息
[任何其他可能有用的信息]
```

### 1.3.2 功能请求

除了报告问题，你也可以提出新功能请求。好的功能请求应该：

**解释价值**：说明功能为什么有价值，帮助了哪些用户场景。

**提供使用场景**：给出具体的使用案例，让维护者理解需求。

**考虑实现复杂度**：评估实现复杂度，可能的话提供初步的实现思路。

```markdown
## 功能请求模板

### 功能名称
[简洁的功能名称]

### 功能描述
[一到两句话描述功能]

### 使用场景
[描述具体的使用场景]

- 场景 1：[描述]
- 场景 2：[描述]

### 期望的行为
[描述功能的预期行为]

### 实现思路
[可选：如果你有实现想法，描述实现方案]

### 参考
[可选：参考其他项目的实现]
```

### 1.3.3 代码贡献

贡献代码时，除了遵循前面章节的贡献流程外，还应该：

**保持 PR 规模小**：将大型功能拆分为多个小型 PR，每个 PR 只做一件事。这便于审查和降低引入错误的风险。

**及时响应审查意见**：在代码审查过程中，及时响应维护者的意见，解释你的设计决策或进行修改。

**保持耐心**：开源维护者通常是志愿者，他们可能很忙。保持耐心，给他们足够的时间进行审查。

### 1.3.4 社区参与

除了代码贡献，还有其他参与社区的方式：

**回答其他用户的问题**：在 Issue 讨论中帮助其他用户解决问题。

**改进文档**：发现文档中的错误或遗漏，提交 PR 进行改进。

**分享使用经验**：在博客、社交媒体上分享使用 weread-exporter 的经验，帮助更多人使用这个工具。

**反馈使用体验**：向维护者反馈使用体验，帮助改进工具。

## 1.4 项目维护指南

如果你想成为项目的长期维护者，需要了解项目维护的各个方面。

### 1.4.1 版本管理

weread-exporter 使用语义化版本号（Semantic Versioning）：

- **主版本号（MAJOR）**：不兼容的 API 变更
- **次版本号（MINOR）：**：向后兼容的新功能
- **修订号（PATCH）**：向后兼容的 bug 修复

版本发布流程：

```bash
# 1. 更新版本号（在 weread_exporter/__init__.py 中）
VERSION = "1.1.0"

# 2. 更新 CHANGELOG.md

# 3. 创建发布标签
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 4. GitHub Release 会自动创建
```

### 1.4.2 依赖管理

管理项目依赖是维护工作的重要部分：

**定期更新依赖**：使用 `pip list --outdated` 检查过时依赖，并定期更新。

**锁定依赖版本**：在 `requirements.txt` 中锁定关键依赖的版本，确保构建可重复。

**安全更新**：关注依赖的安全漏洞，及时更新受影响的依赖。

```bash
# 检查过时依赖
pip list --outdated

# 使用 pip-tools 管理依赖
pip-compile requirements.in  # 生成 requirements.txt
```

### 1.4.3 技术债务处理

随着项目发展，会积累技术债务。维护者需要：

**识别技术债务**：定期审查代码，识别潜在的技术债务。

**制定偿还计划**：为重要的技术债务制定偿还计划，分配到各个版本中。

**平衡功能开发与债务偿还**：在开发新功能的同时，分配一定比例的时间偿还技术债务。

常见的技术债务：

- 缺失的测试覆盖
- 过时的依赖
- 代码风格不一致
- 过时的文档
- 未处理的弃用警告

### 1.4.4 社区治理

健康的社区是开源项目成功的关键：

**制定行为准则**：明确社区的行为期望，如尊重、包容、友善等。

**建立沟通渠道**：提供多种沟通渠道，如 GitHub Issue、Discourse 论坛、Discord 服务器等。

**认可贡献者**：定期认可活跃贡献者，让社区感受到被重视。

**处理冲突**：当社区出现冲突时，及时介入调解，维护健康的社区氛围。

## 1.5 本章小结

本章介绍了 weread-exporter 的扩展与贡献指南，包括扩展点分析、新功能设计方法、开源社区参与和项目维护指南。掌握这些知识后，你已经具备了深度参与项目开发的能力。

完成开发路径的全部四级学习后，你已经建立了从使用到开发再到贡献的完整知识体系。如果你对项目的架构设计和技术原理更感兴趣，建议继续学习进阶路径的相关文档。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| MVP | Minimum Viable Product | 最小可行产品，只包含核心功能 |
| 技术债务 | Technical Debt | 为了快速完成而采取的次优方案 |
| 代码审查 | Code Review | 在合并代码前对代码进行检查和讨论 |
| 语义化版本 | Semantic Versioning | 使用 MAJOR.MINOR.PATCH 格式的版本号 |
| 行为准则 | Code of Conduct | 社区成员应遵守的行为规范 |
| 维护者 | Maintainer | 负责项目日常维护和管理的贡献者 |
