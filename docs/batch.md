# 批量处理

## 概述

批量处理功能允许您同时导出多本书籍，大大提高工作效率。本章将详细介绍批量导出的各种方法和最佳实践。

## 基本批量导出

### 1. 命令行批量导出

#### 从文件批量导出

创建包含书籍ID的文本文件：

```bash
# 创建书籍ID列表文件
cat > books.txt << EOF
08232ac0720befa90825d88
1a2b3c4d5e6f7g8h9i0j1k
book_id_3_here
book_id_4_here
EOF

# 批量导出
weread-exporter --batch books.txt -o epub -o pdf
```

#### 直接指定多个ID

```bash
# 直接在命令行指定多个书籍ID
weread-exporter --book-ids "id1,id2,id3" -o epub

# 或使用空格分隔
weread-exporter --book-ids "id1 id2 id3" -o epub
```

### 2. 批量导出参数

```bash
# 基本批量导出
weread-exporter --batch books.txt -o epub

# 指定输出目录
weread-exporter --batch books.txt -o epub --output-dir ~/batch_books

# 设置并发数量
weread-exporter --batch books.txt -o epub --concurrency 3

# 无头模式（推荐用于批量）
weread-exporter --batch books.txt -o epub --headless
```

## 高级批量配置

### 1. 并发控制

```bash
# 限制并发数量（避免被封）
weread-exporter --batch books.txt -o epub --concurrency 2

# 动态并发控制
weread-exporter --batch books.txt -o epub --adaptive-concurrency

# 设置请求间隔
weread-exporter --batch books.txt -o epub --request-interval 5
```

### 2. 错误处理

```bash
# 跳过错误继续处理
weread-exporter --batch books.txt -o epub --skip-errors

# 失败重试次数
weread-exporter --batch books.txt -o epub --max-retries 3

# 保存失败列表
weread-exporter --batch books.txt -o epub --save-failures failed.txt

# 仅重试失败的书籍
weread-exporter --retry-failed failed.txt -o epub
```

### 3. 进度监控

```bash
# 显示详细进度
weread-exporter --batch books.txt -o epub --verbose

# 进度条显示
weread-exporter --batch books.txt -o epub --progress

# 实时统计信息
weread-exporter --batch books.txt -o epub --stats

# 生成进度报告
weread-exporter --batch books.txt -o epub --progress-report report.json
```

## 批量处理脚本

### 1. 基础批量脚本

```bash
#!/bin/bash
# batch_export.sh

BOOKS_FILE="books.txt"
OUTPUT_DIR="~/batch_output"
FORMATS="epub pdf"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 批量导出
while IFS= read -r book_id; do
    if [[ -n "$book_id" ]]; then
        echo "正在导出: $book_id"
        weread-exporter -b "$book_id" -o $FORMATS --headless --output-dir "$OUTPUT_DIR"
        echo "导出完成: $book_id"
        echo "---"
    fi
done < "$BOOKS_FILE"

echo "批量导出完成!"
```

### 2. 高级批量脚本

```bash
#!/bin/bash
# advanced_batch.sh

BOOKS_FILE="${1:-books.txt}"
OUTPUT_DIR="${2:-~/batch_books}"
LOG_FILE="batch_export.log"
FAILED_FILE="failed_books.txt"

# 初始化
mkdir -p "$OUTPUT_DIR"
rm -f "$FAILED_FILE"

echo "开始批量导出 $(date)" | tee -a "$LOG_FILE"

SUCCESS=0
FAILED=0
TOTAL=$(wc -l < "$BOOKS_FILE")

# 处理每本书籍
while IFS= read -r book_id; do
    if [[ -n "$book_id" ]]; then
        echo "[$((SUCCESS + FAILED + 1))/$TOTAL] 处理: $book_id" | tee -a "$LOG_FILE"
        
        if weread-exporter -b "$book_id" -o epub pdf --headless --output-dir "$OUTPUT_DIR" 2>> "$LOG_FILE"; then
            echo "✅ 成功: $book_id" | tee -a "$LOG_FILE"
            ((SUCCESS++))
        else
            echo "❌ 失败: $book_id" | tee -a "$LOG_FILE"
            echo "$book_id" >> "$FAILED_FILE"
            ((FAILED++))
        fi
        
        # 避免请求过于频繁
        sleep 2
    fi
done < "$BOOKS_FILE"

# 生成报告
echo "=== 批量导出报告 ===" | tee -a "$LOG_FILE"
echo "完成时间: $(date)" | tee -a "$LOG_FILE"
echo "总计: $TOTAL" | tee -a "$LOG_FILE"
echo "成功: $SUCCESS" | tee -a "$LOG_FILE"
echo "失败: $FAILED" | tee -a "$LOG_FILE"

if [[ $FAILED -gt 0 ]]; then
    echo "失败书籍列表已保存到: $FAILED_FILE" | tee -a "$LOG_FILE"
fi
```

### 3. Python批量脚本

```python
#!/usr/bin/env python3
# batch_export.py

import asyncio
import sys
from pathlib import Path
from weread_exporter import WeReadExporter

class BatchExporter:
    def __init__(self, output_dir: str, max_concurrent: int = 3):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def export_book(self, book_id: str) -> dict:
        """导出单本书籍"""
        async with self.semaphore:
            try:
                exporter = WeReadExporter(book_id, {
                    'output_dir': str(self.output_dir / book_id),
                    'headless': True,
                    'timeout': 120
                })
                
                result = await exporter.export(['epub', 'pdf'])
                return {'book_id': book_id, 'success': True, 'result': result}
                
            except Exception as e:
                return {'book_id': book_id, 'success': False, 'error': str(e)}
    
    async def export_batch(self, book_ids: list) -> dict:
        """批量导出书籍"""
        tasks = [self.export_book(book_id) for book_id in book_ids]
        results = await asyncio.gather(*tasks)
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - success_count
        
        return {
            'total': len(results),
            'success': success_count,
            'failed': failed_count,
            'results': results
        }

async def main():
    if len(sys.argv) != 2:
        print("用法: python batch_export.py <书籍ID文件>")
        sys.exit(1)
    
    books_file = sys.argv[1]
    
    # 读取书籍ID
    with open(books_file, 'r') as f:
        book_ids = [line.strip() for line in f if line.strip()]
    
    print(f"找到 {len(book_ids)} 本书籍")
    
    # 批量导出
    exporter = BatchExporter('batch_output', max_concurrent=3)
    result = await exporter.export_batch(book_ids)
    
    # 输出结果
    print(f"\n批量导出完成:")
    print(f"总计: {result['total']}")
    print(f"成功: {result['success']}")
    print(f"失败: {result['failed']}")
    
    # 输出失败详情
    if result['failed'] > 0:
        print("\n失败的书籍:")
        for r in result['results']:
            if not r['success']:
                print(f"  {r['book_id']}: {r['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 批量处理策略

### 1. 并发策略

#### 固定并发

```python
# 固定并发数量
class FixedConcurrencyStrategy:
    def __init__(self, concurrency: int):
        self.concurrency = concurrency
    
    async def process_batch(self, items, process_func):
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def process_item(item):
            async with semaphore:
                return await process_func(item)
        
        tasks = [process_item(item) for item in items]
        return await asyncio.gather(*tasks)
```

#### 动态并发

```python
# 动态调整并发数量
class AdaptiveConcurrencyStrategy:
    def __init__(self, initial_concurrency: int = 3, max_concurrency: int = 10):
        self.current_concurrency = initial_concurrency
        self.max_concurrency = max_concurrency
        self.success_rate = 1.0
    
    async def adjust_concurrency(self, success: bool):
        """根据成功率调整并发数量"""
        if success:
            self.success_rate = min(1.0, self.success_rate + 0.1)
            if self.success_rate > 0.9 and self.current_concurrency < self.max_concurrency:
                self.current_concurrency += 1
        else:
            self.success_rate = max(0.0, self.success_rate - 0.2)
            if self.success_rate < 0.7 and self.current_concurrency > 1:
                self.current_concurrency -= 1
```

### 2. 错误处理策略

#### 立即重试

```python
class ImmediateRetryStrategy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def execute_with_retry(self, coro, *args):
        for attempt in range(self.max_retries + 1):
            try:
                return await coro(*args)
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                print(f"尝试 {attempt + 1} 失败，立即重试...")
```

#### 指数退避

```python
class ExponentialBackoffStrategy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(self, coro, *args):
        for attempt in range(self.max_retries + 1):
            try:
                return await coro(*args)
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                
                delay = self.base_delay * (2 ** attempt)
                print(f"尝试 {attempt + 1} 失败，等待 {delay} 秒后重试...")
                await asyncio.sleep(delay)
```

## 批量导出工作流

### 1. 预处理阶段

```python
async def preprocess_batch(book_ids: list) -> dict:
    """批量预处理"""
    
    # 验证书籍ID格式
    valid_ids = []
    invalid_ids = []
    
    for book_id in book_ids:
        if validate_book_id(book_id):
            valid_ids.append(book_id)
        else:
            invalid_ids.append(book_id)
    
    # 检查书籍可访问性
    accessible_ids = []
    inaccessible_ids = []
    
    for book_id in valid_ids:
        if await check_book_accessibility(book_id):
            accessible_ids.append(book_id)
        else:
            inaccessible_ids.append(book_id)
    
    return {
        'valid': valid_ids,
        'invalid': invalid_ids,
        'accessible': accessible_ids,
        'inaccessible': inaccessible_ids
    }
```

### 2. 导出阶段

```python
async def export_batch_phase(book_ids: list, strategy: BatchStrategy) -> dict:
    """批量导出阶段"""
    
    results = {}
    
    # 并发导出
    export_results = await strategy.execute_batch(
        book_ids, 
        export_single_book
    )
    
    # 分类结果
    for book_id, result in zip(book_ids, export_results):
        if result['success']:
            results[book_id] = {
                'status': 'success',
                'files': result['output_files'],
                'size': result['total_size']
            }
        else:
            results[book_id] = {
                'status': 'failed',
                'error': result['error']
            }
    
    return results
```

### 3. 后处理阶段

```python
async def postprocess_batch(export_results: dict) -> dict:
    """批量后处理"""
    
    # 生成统计报告
    stats = {
        'total': len(export_results),
        'success': sum(1 for r in export_results.values() if r['status'] == 'success'),
        'failed': sum(1 for r in export_results.values() if r['status'] == 'failed'),
        'total_size': 0
    }
    
    # 计算总文件大小
    for result in export_results.values():
        if result['status'] == 'success':
            stats['total_size'] += result.get('size', 0)
    
    # 生成详细报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'statistics': stats,
        'details': export_results
    }
    
    # 保存报告
    with open('batch_report.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report
```

## 性能优化

### 1. 内存优化

```python
class MemoryOptimizedBatchExporter:
    def __init__(self, memory_limit_mb: int = 512):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        self.batch_size = self.calculate_optimal_batch_size()
    
    def calculate_optimal_batch_size(self) -> int:
        """根据内存限制计算最优批量大小"""
        # 估算单本书籍的内存使用
        estimated_memory_per_book = 50 * 1024 * 1024  # 50MB
        
        optimal_size = max(1, self.memory_limit // estimated_memory_per_book)
        return min(optimal_size, 10)  # 最大批量大小限制
    
    async def export_large_batch(self, book_ids: list) -> dict:
        """分批处理大批量书籍"""
        
        all_results = {}
        
        # 分批处理
        for i in range(0, len(book_ids), self.batch_size):
            batch = book_ids[i:i + self.batch_size]
            
            print(f"处理批次 {i//self.batch_size + 1}/{(len(book_ids)-1)//self.batch_size + 1}")
            
            # 导出当前批次
            batch_results = await self.export_batch(batch)
            all_results.update(batch_results)
            
            # 清理内存
            await self.cleanup_memory()
        
        return all_results
```

### 2. 网络优化

```python
class NetworkOptimizedBatchExporter:
    def __init__(self, max_requests_per_minute: int = 60):
        self.rate_limiter = RateLimiter(max_requests_per_minute)
    
    async def export_with_rate_limit(self, book_ids: list) -> dict:
        """带速率限制的批量导出"""
        
        results = {}
        
        for book_id in book_ids:
            # 等待速率限制
            await self.rate_limiter.wait_if_needed()
            
            try:
                result = await self.export_single_book(book_id)
                results[book_id] = result
                
                # 更新成功率统计
                self.rate_limiter.record_success()
                
            except Exception as e:
                results[book_id] = {'error': str(e)}
                
                # 更新失败率统计
                self.rate_limiter.record_failure()
        
        return results
```

## 监控和报告

### 1. 实时监控

```python
class BatchMonitor:
    def __init__(self, total_items: int):
        self.total = total_items
        self.completed = 0
        self.start_time = time.time()
        self.success_count = 0
        self.failure_count = 0
    
    def update_progress(self, success: bool = True):
        """更新进度"""
        self.completed += 1
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.display_progress()
    
    def display_progress(self):
        """显示进度信息"""
        percentage = (self.completed / self.total) * 100
        elapsed = time.time() - self.start_time
        
        if self.completed > 0:
            estimated_total = elapsed * self.total / self.completed
            remaining = estimated_total - elapsed
        else:
            remaining = 0
        
        print(f"进度: {self.completed}/{self.total} ({percentage:.1f}%) "
              f"成功: {self.success_count} 失败: {self.failure_count} "
              f"剩余: {self.format_time(remaining)}")
```

### 2. 详细报告生成

```python
async def generate_batch_report(export_results: dict, config: dict) -> str:
    """生成批量导出详细报告"""
    
    report = {
        'export_session': {
            'start_time': config.get('start_time'),
            'end_time': datetime.now().isoformat(),
            'duration': config.get('duration'),
            'total_books': len(export_results)
        },
        'statistics': {
            'successful_exports': sum(1 for r in export_results.values() if r['status'] == 'success'),
            'failed_exports': sum(1 for r in export_results.values() if r['status'] == 'failed'),
            'success_rate': 0,
            'total_file_size': 0
        },
        'books': export_results
    }
    
    # 计算成功率
    total = report['statistics']['successful_exports'] + report['statistics']['failed_exports']
    if total > 0:
        report['statistics']['success_rate'] = (
            report['statistics']['successful_exports'] / total * 100
        )
    
    # 计算总文件大小
    for book_result in export_results.values():
        if book_result['status'] == 'success':
            report['statistics']['total_file_size'] += book_result.get('file_size', 0)
    
    # 格式化报告
    report_str = format_report(report)
    
    # 保存报告文件
    report_file = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file
```

## 最佳实践

### 1. 批量大小选择

- **小批量**（1-10本书）：适合网络不稳定或需要实时监控的情况
- **中批量**（10-50本书）：平衡效率和稳定性
- **大批量**（50+本书）：需要良好的错误处理和恢复机制

### 2. 时间安排

- **避开高峰时段**：选择网络使用较少的时段进行批量导出
- **分时段处理**：将大批量任务分成多个时段处理
- **夜间处理**：利用夜间空闲时间进行批量导出

### 3. 错误处理策略

- **立即重试**：对于临时性错误
- **延迟重试**：对于服务器限制或网络问题
- **跳过处理**：对于无法解决的错误
- **记录日志**：详细记录所有错误信息

---

**批量处理指南到此结束。** 这些方法和策略将帮助您高效地处理大量书籍导出任务。继续阅读其他文档了解更多功能！ 📚