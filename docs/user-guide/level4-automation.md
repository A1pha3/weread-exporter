# 批量处理与自动化

> 本文档是用户路径的第四篇，也是用户路径的最高级别。通过阅读和实践本文档，你将掌握批量处理大量书籍的方法，学会编写自动化脚本，并能够将 weread-exporter 集成到你的工作流程中。这些技能将帮助你高效管理大量书籍的导出需求。

## 学习目标

完成本章节学习后，你将能够设计并执行批量导出方案，编写自动化脚本实现定时或触发式导出，并将 weread-exporter 集成到更复杂的工作流程中。这些能力对于需要处理大量书籍的用户来说至关重要。

### 基础目标

首先，你将理解批量处理的需求分析和方案设计，包括如何组织书籍列表、如何处理不同类型的书籍、如何设计导出流程等。其次，你将掌握脚本编写的基础知识，能够使用 Shell 脚本和 Python 脚本实现自动化任务。第三，你将学会监控和管理批量任务，包括进度跟踪、错误处理、日志记录等。

### 进阶目标

进阶目标要求你能够设计完整的自动化工作流程，包括定时执行、触发式执行、失败重试等机制。你还将学会将 weread-exporter 与其他工具集成，如版本控制系统、云存储服务、通知系统等。此外，你还将掌握性能优化和资源管理的高级技巧。

## 1.1 批量处理方案设计

在开始批量导出之前，需要进行周密的方案设计。良好的设计可以避免中途出错、提高效率、便于管理。本节将介绍批量处理的完整方案设计方法。

### 1.1.1 需求分析

批量处理的需求分析是方案设计的第一步。需要明确以下问题：导出哪些书籍、导出什么格式、导出到哪里、如何处理结果。

书籍来源分析：你的书籍可能来自不同的来源，包括个人书单、他人分享的书单、关注的公众号推荐等。不同来源的书籍管理方式可能不同，需要考虑如何组织和维护书籍列表。

```markdown
# 示例书籍列表格式
# 每行一个书籍 ID，可以添加注释

# 我的书单
08232ac0720befa90825d88  # 编程入门
a1b2c3d4e5f6            # Python 进阶
...

# 待导出书单
12345_67890              # 朋友分享的技术书单
98765_43210              # 豆瓣高分书单
```

格式需求分析：根据最终用途确定导出格式。不同用途需要不同格式：Kindle 阅读需要 MOBI 或 EPUB，个人备份需要 Markdown 或 PDF，笔记整理需要 Markdown。分析格式需求后，可以为不同用途设计不同的导出流程。

```bash
# 多种格式导出脚本
for book_id in $(cat book_ids.txt); do
    weread-exporter -b "$book_id" -o epub -o md
done
```

### 1.1.2 流程设计

批量处理的流程设计需要考虑顺序、依赖、错误处理等因素。常见的流程模式包括顺序执行、并行执行、分批执行等。

顺序执行是最简单的方式，按照列表顺序逐个处理。优点是易于理解和调试，缺点是速度最慢。

```bash
#!/bin/bash
# 顺序执行批量导出

INPUT_FILE="book_ids.txt"
OUTPUT_DIR="output"
LOG_FILE="export.log"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 逐个处理
while IFS= read -r book_id || [[ -n "$book_id" ]]; do
    echo "[$(date)] 开始导出: $book_id" >> "$LOG_FILE"
    weread-exporter -b "$book_id" -o epub -o md >> "$LOG_FILE" 2>&1
    result=$?
    if [ $result -eq 0 ]; then
        echo "[$(date)] 导出成功: $book_id" >> "$LOG_FILE"
    else
        echo "[$(date)] 导出失败: $book_id (退出码: $result)" >> "$LOG_FILE"
    fi
done < "$INPUT_FILE"
```

并行执行可以显著提高速度，但需要考虑资源限制和错误处理。

```bash
#!/bin/bash
# 并行执行批量导出（限制并发数）

INPUT_FILE="book_ids.txt"
MAX_JOBS=4  # 最大并发数

# 创建命名管道用于收集结果
result_pipe=$(mktemp -u)
mkfifo "$result_pipe"

# 后台进程收集结果
(
    while read -r line; do
        echo "$line"
    done < "$result_pipe"
) > results.log &

# 导出函数
export_book() {
    book_id=$1
    weread-exporter -b "$book_id" -o epub
    echo "完成: $book_id" > "$result_pipe"
}

# 导出工作者
worker() {
    while read -r book_id; do
        export_book "$book_id"
    done
}

# 限制并发数
export -f worker
cat "$INPUT_FILE" | xargs -P "$MAX_JOBS" -I {} bash -c 'export_book "{}"'
```

分批执行结合了顺序和并行的优点。将任务分成若干批次，每批内部并行执行。

```bash
#!/bin/bash
# 分批执行批量导出

INPUT_FILE="book_ids.txt"
BATCH_SIZE=5  # 每批数量
BATCH_DELAY=300  # 批次间隔（秒）

# 分割书籍列表
split -l "$BATCH_SIZE" "$INPUT_FILE" batch_

# 逐批处理
for batch in batch_*; do
    echo "[$(date)] 开始批次: $batch" >> batch.log
    # 并行处理当前批次
    cat "$batch" | xargs -P 3 -I {} weread-exporter -b {} -o epub -o pdf
    echo "[$(date)] 完成批次: $batch" >> batch.log
    # 批次间等待
    sleep "$BATCH_DELAY"
done

# 清理临时文件
rm -f batch_*
```

### 1.1.3 数据管理

批量处理会生成大量数据，需要良好的数据管理策略。

文件命名规范：使用一致的命名格式便于管理和检索。推荐格式：`[作者] 书籍标题.扩展名`。

```python
# Python 脚本：规范化文件命名
import os
import re

def sanitize_filename(name):
    # 移除非法字符
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name.strip()

def rename_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.epub'):
            new_name = sanitize_filename(filename)
            if new_name != filename:
                os.rename(
                    os.path.join(directory, filename),
                    os.path.join(directory, new_name)
                )
```

版本控制：导出文件应该版本化，特别是当书籍有更新时。

```python
# Python 脚本：版本化导出
import os
import hashlib
from datetime import datetime

def get_file_hash(filepath):
    """计算文件哈希"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def export_with_version(book_id, output_dir):
    """导出并版本化管理"""
    weread-exporter -b book_id -o epub
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"{book_id}_{timestamp}.epub"
    # 重命名为版本化名称
```

## 1.2 自动化脚本编写

自动化脚本是实现批量处理的关键工具。本节将介绍各种脚本编写技巧，帮助你创建灵活、高效的自动化方案。

### 1.2.1 Shell 脚本基础

Shell 脚本是 Unix/Linux 系统上最常用的自动化工具。weread-exporter 可以很好地集成到 Shell 脚本中。

基础结构：

```bash
#!/bin/bash
# weread-exporter 批量导出脚本

set -e  # 遇错即停
set -u  # 变量未定义时报错

# 配置变量
BOOK_IDS_FILE="book_ids.txt"
OUTPUT_DIR="${HOME}/weread-export"
LOG_DIR="${HOME}/weread-export/logs"
DATE=$(date +%Y%m%d)
LOG_FILE="${LOG_DIR}/export_${DATE}.log"

# 创建必要目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 导出函数
export_book() {
    local book_id=$1
    local book_dir="${OUTPUT_DIR}/${book_id}"
    
    log "开始导出: $book_id"
    
    # 创建书籍目录
    mkdir -p "$book_dir"
    
    # 执行导出
    weread-exporter -b "$book_id" \
        -o epub \
        -o pdf \
        -o md \
        --headless \
        2>&1 | tee -a "$LOG_FILE"
    
    # 验证结果
    if [ $? -eq 0 ]; then
        log "导出成功: $book_id"
    else
        log "导出失败: $book_id"
        return 1
    fi
}

# 主流程
log "========== 开始批量导出 =========="

# 检查输入文件
if [ ! -f "$BOOK_IDS_FILE" ]; then
    log "错误: 找不到书籍 ID 文件: $BOOK_IDS_FILE"
    exit 1
fi

# 读取并处理每本书
failed=0
success=0
while IFS= read -r book_id || [[ -n "$book_id" ]]; do
    # 跳过空行和注释
    [[ -z "$book_id" || "$book_id" =~ ^# ]] && continue
    
    if export_book "$book_id"; then
        ((success++))
    else
        ((failed++))
    fi
done < "$BOOK_IDS_FILE"

log "========== 导出完成 =========="
log "成功: $success 本, 失败: $failed 本"
```

### 1.2.2 Python 脚本高级自动化

Python 提供了更强大的自动化能力，适合复杂的任务需求。

异步并行导出：

```python
#!/usr/bin/env python3
"""
weread-exporter 异步批量导出脚本
使用 asyncio 实现高效的并行导出
"""

import asyncio
import aiofiles
import aiohttp
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

class BatchExporter:
    def __init__(
        self,
        book_ids: List[str],
        output_dir: str = "output",
        max_concurrent: int = 3,
        formats: List[str] = ["epub", "pdf", "md"]
    ):
        self.book_ids = book_ids
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.formats = formats
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results = []
        
    async def export_single(self, book_id: str) -> dict:
        """导出单本书籍"""
        async with self.semaphore:
            result = {
                "book_id": book_id,
                "success": False,
                "error": None,
                "files": []
            }
            
            try:
                # 构建命令
                cmd = [
                    "weread-exporter",
                    "-b", book_id,
                    "--headless"
                ]
                for fmt in self.formats:
                    cmd.extend(["-o", fmt])
                
                # 执行导出
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    result["success"] = True
                    # 记录生成的文件
                    book_output = self.output_dir / book_id
                    if book_output.exists():
                        for f in book_output.glob("*"):
                            result["files"].append(f.name)
                else:
                    result["error"] = stderr.decode()
                    
            except Exception as e:
                result["error"] = str(e)
            
            self.results.append(result)
            return result
    
    async def export_all(self) -> List[dict]:
        """导出所有书籍"""
        tasks = [self.export_single(bid) for bid in self.book_ids]
        await asyncio.gather(*tasks)
        return self.results
    
    def save_report(self, filepath: str = "export_report.json"):
        """保存导出报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.book_ids),
            "success": sum(1 for r in self.results if r["success"]),
            "failed": sum(1 for r in self.results if not r["success"]),
            "results": self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report


async def main():
    # 从文件读取书籍 ID
    book_ids_file = "book_ids.txt"
    if not os.path.exists(book_ids_file):
        print(f"错误: 找不到 {book_ids_file}")
        sys.exit(1)
    
    with open(book_ids_file, 'r') as f:
        book_ids = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    # 创建导出器
    exporter = BatchExporter(
        book_ids=book_ids,
        output_dir="batch_output",
        max_concurrent=2,
        formats=["epub", "pdf"]
    )
    
    # 执行导出
    print(f"开始导出 {len(book_ids)} 本书籍...")
    results = await exporter.export_all()
    
    # 保存报告
    report = exporter.save_report()
    
    # 输出摘要
    print(f"\n导出完成!")
    print(f"成功: {report['success']} 本")
    print(f"失败: {report['failed']} 本")
    print(f"报告已保存至: export_report.json")


if __name__ == "__main__":
    asyncio.run(main())
```

### 1.2.3 定时任务配置

使用系统定时任务实现自动定期导出。

Cron 定时任务配置：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 3 点执行导出
0 3 * * * /path/to/export script.sh >> /path/to/export.log 2>&1

# 每周日凌晨 2 点执行导出（包含 PDF）
0 2 * * 0 /path/to/export_all.sh >> /path/to/weekly_export.log 2>&1

# 每月第一天凌晨 1 点执行全面导出
0 1 1 * * /path/to/monthly_backup.sh >> /path/to/monthly.log 2>&1
```

系统服务配置（systemd）：

```ini
# /etc/systemd/system/weread-exporter.service
[Unit]
Description=WeRead Book Exporter Service
After=network.target

[Service]
Type=oneshot
User=weread
WorkingDirectory=/home/weread
ExecStart=/usr/local/bin/export script.py
StandardOutput=append:/var/log/weread-exporter/output.log
StandardError=append:/var/log/weread-exporter/error.log

[Install]
WantedBy=multi-user.target
```

## 1.3 工作流程集成

将 weread-exporter 集成到更大的工作流程中，可以实现更高级的自动化。本节介绍几种常见的集成场景。

### 1.3.1 版本控制系统集成

将导出的内容纳入版本控制，便于追踪变化。

```bash
#!/bin/bash
# 导出并提交到 Git

REPO_DIR="/path/to/knowledge-base"
BOOK_IDS_FILE="book_ids.txt"

cd "$REPO_DIR"

# 拉取最新
git pull

# 导出每本书
while IFS= read -r book_id || [[ -n "$book_id" ]]; do
    [[ -z "$book_id" || "$book_id" =~ ^# ]] && continue
    
    weread-exporter -b "$book_id" -o md --headless
done < "$BOOK_IDS_FILE"

# 添加新文件
git add .

# 提交更改
if git diff --cached --quiet; then
    echo "没有新内容需要提交"
else
    git add -A
    git commit -m "更新: $(date '+%Y-%m-%d %H:%M')"
    git push
fi
```

### 1.3.2 云存储同步

导出后自动上传到云存储服务。

```python
#!/usr/bin/env python3
"""
导出并同步到云存储
支持: Dropbox, Google Drive, OneDrive, S3 等
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False


class CloudSyncExporter:
    def __init__(
        self,
        book_ids: list,
        output_dir: str = "output",
        cloud_provider: str = "dropbox",
        token_file: str = ".dropbox_token"
    ):
        self.book_ids = book_ids
        self.output_dir = Path(output_dir)
        self.cloud_provider = cloud_provider
        self.token_file = token_file
        self.uploaded_files = []
    
    def run_export(self):
        """执行导出"""
        for book_id in self.book_ids:
            subprocess.run([
                "weread-exporter",
                "-b", book_id,
                "-o", "epub",
                "-o", "md",
                "--headless"
            ])
    
    def sync_to_cloud(self):
        """同步到云存储"""
        if self.cloud_provider == "dropbox":
            self._sync_dropbox()
        elif self.cloud_provider == "s3":
            self._sync_s3()
        # 可以扩展其他云存储服务
    
    def _sync_dropbox(self):
        """同步到 Dropbox"""
        if not DROPBOX_AVAILABLE:
            print("Dropbox SDK 未安装")
            return
        
        with open(self.token_file, 'r') as f:
            token = f.read().strip()
        
        dbx = dropbox.Dropbox(token)
        
        for filepath in self.output_dir.rglob("*"):
            if filepath.is_file():
                relative_path = filepath.relative_to(self.output_dir)
                cloud_path = f"/weread-exports/{relative_path}"
                
                with open(filepath, 'rb') as f:
                    dbx.files_upload(
                        f.read(),
                        cloud_path,
                        mode=dropbox.files.WriteMode.overwrite
                    )
                self.uploaded_files.append(str(relative_path))
        
        print(f"已同步 {len(self.uploaded_files)} 个文件到 Dropbox")


def main():
    # 示例：读取书单并导出同步
    with open('book_ids.txt') as f:
        book_ids = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
    
    exporter = CloudSyncExporter(book_ids)
    exporter.run_export()
    exporter.sync_to_cloud()


if __name__ == "__main__":
    main()
```

### 1.3.3 通知系统集成

导出完成后发送通知。

```python
#!/usr/bin/env python3
"""
带通知的导出脚本
支持: 邮件, Slack, 微信, Telegram 等
"""

import smtplib
import subprocess
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
from typing import List, Optional

try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class Notifier:
    def __init__(
        self,
        email_config: Optional[dict] = None,
        telegram_config: Optional[dict] = None
    ):
        self.email_config = email_config
        self.telegram_config = telegram_config
    
    def send_email(self, subject: str, body: str):
        """发送邮件通知"""
        if not self.email_config:
            return
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        with smtplib.SMTP_SSL(
            self.email_config['smtp_server'],
            self.email_config['smtp_port']
        ) as server:
            server.login(
                self.email_config['username'],
                self.email_config['password']
            )
            server.send_message(msg)
    
    def send_telegram(self, message: str):
        """发送 Telegram 通知"""
        if not TELEGRAM_AVAILABLE or not self.telegram_config:
            return
        
        bot = Bot(token=self.telegram_config['token'])
        bot.send_message(
            chat_id=self.telegram_config['chat_id'],
            text=message
        )
    
    def send_all(self, subject: str, body: str):
        """发送所有类型的通知"""
        self.send_email(subject, body)
        self.send_telegram(body)


class ExportWithNotification:
    def __init__(self, book_ids: List[str], notifier: Notifier):
        self.book_ids = book_ids
        self.notifier = notifier
        self.results = []
    
    def run(self):
        """执行导出并通知"""
        total = len(self.book_ids)
        
        for i, book_id in enumerate(self.book_ids, 1):
            print(f"[{i}/{total}] 导出: {book_id}")
            
            result = subprocess.run(
                ["weread-exporter", "-b", book_id, "-o", "epub", "--headless"],
                capture_output=True,
                text=True
            )
            
            self.results.append({
                "book_id": book_id,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            })
        
        # 发送通知
        success_count = sum(1 for r in self.results if r["success"])
        failed_count = total - success_count
        
        message = f"""
导出完成！

总计: {total} 本
成功: {success_count} 本
失败: {failed_count} 本

详情:
"""
        for r in self.results:
            status = "✅" if r["success"] else "❌"
            message += f"{status} {r['book_id']}\n"
        
        self.notifier.send_all("weread-exporter 导出报告", message)
        
        return self.results


def main():
    # 配置通知
    notifier = Notifier(
        email_config={
            'smtp_server': 'smtp.example.com',
            'smtp_port': 465,
            'username': 'your-email@example.com',
            'password': 'your-password',
            'from': 'your-email@example.com',
            'to': 'your-email@example.com'
        },
        telegram_config={
            'token': 'your-telegram-bot-token',
            'chat_id': 'your-chat-id'
        }
    )
    
    # 读取书单
    with open('book_ids.txt') as f:
        book_ids = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
    
    # 执行导出
    exporter = ExportWithNotification(book_ids, notifier)
    exporter.run()


if __name__ == "__main__":
    main()
```

## 1.4 监控与报告

批量处理需要良好的监控和报告机制。本节介绍如何实现进度跟踪、性能监控和结果报告。

### 1.4.1 进度跟踪

实时进度显示：

```bash
#!/bin/bash
# 带进度显示的批量导出

INPUT_FILE="book_ids.txt"
TOTAL=$(grep -c -v '^#' "$INPUT_FILE")
CURRENT=0

while IFS= read -r book_id || [[ -n "$book_id" ]]; do
    [[ -z "$book_id" || "$book_id" =~ ^# ]] && continue
    
    ((CURRENT++))
    PERCENT=$((CURRENT * 100 / TOTAL))
    
    printf "\r进度: [%3d%%] %d/%d | %s" "$PERCENT" "$CURRENT" "$TOTAL" "$book_id"
    
    weread-exporter -b "$book_id" -o epub --headless > /dev/null 2>&1
done < "$INPUT_FILE"

printf "\n完成!\n"
```

Web 进度面板：

```python
#!/usr/bin/env python3
"""
带 Web 进度面板的导出服务
使用 Flask 提供实时进度更新
"""

from flask import Flask, jsonify, render_template_string
import threading
import time
from pathlib import Path

app = Flask(__name__)

# 全局状态
export_state = {
    "running": False,
    "total": 0,
    "current": 0,
    "current_book": "",
    "success": 0,
    "failed": 0,
    "start_time": None,
    "logs": []
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>weread-exporter 进度</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .progress-bar { background: #eee; height: 30px; border-radius: 15px; overflow: hidden; }
        .progress-fill { background: #4CAF50; height: 100%; width: 0%; transition: width 0.3s; }
        .stats { display: flex; justify-content: space-between; margin: 20px 0; }
        .stat { text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; }
        .stat-label { color: #666; }
        #log { background: #1e1e1e; color: #ddd; padding: 15px; border-radius: 5px; height: 300px; overflow-y: auto; font-family: monospace; }
    </style>
</head>
<body>
    <h1>📚 weread-exporter 进度面板</h1>
    
    <div class="progress-bar">
        <div class="progress-fill" id="progress"></div>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value" id="percent">0%</div>
            <div class="stat-label">进度</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="current">0/0</div>
            <div class="stat-label">当前</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="success">0</div>
            <div class="stat-label">成功</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="failed">0</div>
            <div class="stat-label">失败</div>
        </div>
    </div>
    
    <h3>日志</h3>
    <div id="log"></div>
    
    <script>
        function update() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('progress').style.width = data.percent + '%';
                    document.getElementById('percent').textContent = data.percent + '%';
                    document.getElementById('current').textContent = data.current + '/' + data.total;
                    document.getElementById('success').textContent = data.success;
                    document.getElementById('failed').textContent = data.failed;
                    
                    let logHtml = '';
                    data.logs.forEach(l => {
                        logHtml += '<div>' + l + '</div>';
                    });
                    document.getElementById('log').innerHTML = logHtml;
                    document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;
                });
        }
        
        setInterval(update, 1000);
        update();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    return jsonify(export_state)

def run_export(book_ids):
    """在后台运行导出"""
    export_state["running"] = True
    export_state["total"] = len(book_ids)
    export_state["start_time"] = time.time()
    
    from subprocess import run
    for i, book_id in enumerate(book_ids):
        export_state["current"] = i + 1
        export_state["current_book"] = book_id
        export_state["logs"].append(f"开始导出: {book_id}")
        
        result = run(
            ["weread-exporter", "-b", book_id, "-o", "epub", "--headless"],
            capture_output=True
        )
        
        if result.returncode == 0:
            export_state["success"] += 1
            export_state["logs"].append(f"✅ 成功: {book_id}")
        else:
            export_state["failed"] += 1
            export_state["logs"].append(f"❌ 失败: {book_id}")
    
    export_state["running"] = False
    export_state["logs"].append("导出完成!")

# 启动示例
# export_book_ids = [...]  # 书籍 ID 列表
# threading.Thread(target=run_export, args=(export_book_ids,)).start()
# app.run(port=5000)
```

### 1.4.2 性能监控

```python
#!/usr/bin/env python3
"""
性能监控脚本
记录导出过程中的资源使用情况
"""

import psutil
import time
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Optional


class PerformanceMonitor:
    def __init__(self, log_file: str = "performance.log"):
        self.log_file = log_file
        self.samples = []
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """监控单个操作的资源使用"""
        start_time = time.time()
        process = psutil.Process()
        
        sample = {
            "operation": operation_name,
            "start_time": datetime.now().isoformat(),
            "cpu_percent": [],
            "memory_mb": [],
            "disk_io": [],
            "network_io": []
        }
        
        # 开始采样
        self._sample(process, sample)
        
        try:
            yield
        finally:
            end_time = time.time()
            self._sample(process, sample)
            
            sample["duration_seconds"] = end_time - start_time
            sample["cpu_percent_avg"] = sum(sample["cpu_percent"]) / len(sample["cpu_percent"])
            sample["memory_peak_mb"] = max(sample["memory_mb"])
            sample["end_time"] = datetime.now().isoformat()
            
            self.samples.append(sample)
            self._save()
    
    def _sample(self, process: psutil.Process, sample: dict):
        """采集资源使用数据"""
        sample["cpu_percent"].append(process.cpu_percent())
        sample["memory_mb"].append(process.memory_info().rss / 1024 / 1024)
    
    def _save(self):
        """保存监控数据"""
        with open(self.log_file, 'w') as f:
            json.dump(self.samples, f, indent=2, default=str)
    
    def generate_report(self) -> str:
        """生成性能报告"""
        if not self.samples:
            return "没有监控数据"
        
        total_time = sum(s["duration_seconds"] for s in self.samples)
        total_memory = sum(s["memory_peak_mb"] for s in self.samples)
        avg_cpu = sum(s["cpu_percent_avg"] for s in self.samples) / len(self.samples)
        
        report = f"""
weread-exporter 性能报告
========================

总执行时间: {total_time:.2f} 秒
峰值内存使用: {total_memory:.2f} MB
平均 CPU 占用: {avg_cpu:.1f}%

各操作详情:
"""
        for s in self.samples:
            report += f"\n{s['operation']}:\n"
            report += f"  时长: {s['duration_seconds']:.2f} 秒\n"
            report += f"  峰值内存: {s['memory_peak_mb']:.2f} MB\n"
            report += f"  平均 CPU: {s['cpu_percent_avg']:.1f}%\n"
        
        return report


# 使用示例
monitor = PerformanceMonitor()

# 模拟监控
with monitor.monitor_operation("导出书籍1"):
    import subprocess
    subprocess.run(["weread-exporter", "-b", "book1", "-o", "epub", "--headless"])

print(monitor.generate_report())
```

## 1.5 Docker 化部署

使用 Docker 可以创建一致、可移植的运行环境。本节介绍如何将 weread-exporter 容器化。

### 1.5.1 Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 安装 Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 创建非 root 用户
RUN groupadd -r exporter && useradd -r -g exporter exporter \
    && mkdir -p /home/exporter/output /home/exporter/cache \
    && chown -R exporter:exporter /home/exporter

# 复制应用代码
COPY weread_exporter /app/weread_exporter
COPY pyproject.toml /app/
COPY hook.js /app/weread_exporter/
COPY style.css /app/weread_exporter/
COPY epub.css /app/weread_exporter/

WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROME_PATH=/opt/google/chrome

# 切换到非 root 用户
USER exporter

# 默认命令
CMD ["python", "-m", "weread_exporter"]
```

### 1.5.2 Docker Compose

```yaml
version: '3.8'

services:
  weread-exporter:
    build: .
    container_name: weread-exporter
    restart: unless-stopped
    volumes:
      - ./output:/home/exporter/output
      - ./cache:/home/exporter/cache
      - ./book_ids.txt:/home/exporter/book_ids.txt:ro
      - ./export.sh:/home/exporter/export.sh:ro
    environment:
      - TZ=Asia/Shanghai
    command: >
      bash /home/exporter/export.sh
    networks:
      - exporter-network

  # 可选：监控面板
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - exporter-network

networks:
  exporter-network:
    driver: bridge
```

## 1.6 本章小结

本章介绍了批量处理与自动化的完整知识体系，包括方案设计、脚本编写、工作流程集成、监控报告以及容器化部署。掌握这些技能后，你能够高效地处理大量书籍的导出需求，并实现完全自动化的导出工作流程。

完成用户路径的全部四级学习后，你已经具备了从新手到专家的完整能力。建议继续深入开发路径或进阶路径，学习工具的内部实现和架构设计，这将帮助你更好地理解和优化你的自动化方案。

## 术语表

| 术语 | 英文 | 解释 |
|------|------|------|
| 批量处理 | Batch Processing | 一次性处理大量数据 |
| 自动化 | Automation | 使用脚本或工具自动执行任务 |
| 定时任务 | Cron Job | 按计划自动执行的任务 |
| Docker | Docker | 容器化平台，提供一致运行环境 |
| 工作流程 | Workflow | 自动化任务的编排和执行 |
