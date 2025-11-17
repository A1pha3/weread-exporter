# 获取全部书籍ID

## 概述
- 目标：一次性获取某个书单中的全部书籍ID，包含原始ID与哈希ID。
- 范围：当前实现支持“书单页面”的解析；不直接枚举个人书架，请将书架书籍加入一个书单后使用。

## 方法一：命令行一次性打印
- 命令：
```
python -m weread_exporter -b <booklistId> --list-ids
```
- 输出格式：
```
书名<TAB>原始ID<TAB>哈希ID
```
- 示例：
```
python -m weread_exporter -b my_booklist_123 --list-ids
```

## 字段说明
- 原始ID：用于 `https://weread.qq.com/web/bookDetail/<bookId>`。
- 哈希ID：用于章节阅读与导出内部流程；由 `weread_exporter/utils.py` 的 `wr_hash` 计算。

## 方法二：在代码中获取（函数级示例）
```python
import asyncio
from weread_exporter import utils

async def list_book_ids(book_list_id: str):
    """
    获取书单内所有书籍的原始ID与哈希ID
    参数：
        book_list_id: 书单ID（URL中 misc/booklist/<id>）
    返回：
        List[Dict]: [{"original_id": "...", "hashed_id": "...", "title": "..."}]
    """
    return await utils.get_book_list_full(book_list_id)

def main():
    """
    命令行入口：打印书单中所有书籍ID
    用法：
        python list_ids.py <booklistId>
    """
    import sys
    items = asyncio.run(list_book_ids(sys.argv[1]))
    for it in items:
        print(f'{it["title"]}\t{it["original_id"]}\t{it["hashed_id"]}')

if __name__ == "__main__":
    main()
```

## 获取书单ID
- 在网页端打开你的书单页面：`https://weread.qq.com/misc/booklist/<booklistId>`。
- `<booklistId>` 通常包含下划线 `_`，命令行检测到下划线会将其视为“书单ID”。

## 常见问题
- 是否需要登录：仅打印ID无需登录；导出内容需浏览器与有效 Cookie。
- Mac 使用：支持在 macOS 环境运行；如需 PDF 导出请安装 `weasyprint` 相关依赖。