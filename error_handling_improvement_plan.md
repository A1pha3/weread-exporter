# 错误处理改进计划

## 概述

本文档详细描述了对weread-exporter项目中错误处理的改进计划，旨在将宽泛的空except块替换为具体的异常处理，提高代码质量和可维护性。

## 当前问题

项目中存在5个空的except块，捕获所有异常类型，导致：

1. 无法区分不同类型的错误
2. 错误信息不具体，难以调试
3. 缺乏针对性的错误处理逻辑
4. 代码可维护性差

## 改进目标

1. 将所有空except块替换为具体的异常类型
2. 提供具体的错误信息和日志记录
3. 实现针对性的错误处理逻辑
4. 保持应用程序的稳定性和可恢复性

## 具体改进计划

### 1. `weread_exporter/webpage.py` (行169-171) - Cookie解析

**当前代码**:
```python
try:
    cookie = json.loads(cookie)
except:
    for it in cookie.split(";"):
```

**改进后**:
```python
try:
    cookie = json.loads(cookie)
except json.JSONDecodeError as e:
    logging.warning(
        "[%s] Failed to parse cookie as JSON, falling back to legacy format: %s"
        % (self.__class__.__name__, str(e))
    )
    # 继续使用原有的分号分隔解析逻辑
    for it in cookie.split(";"):
```

**改进理由**:
- 具体捕获JSON解析错误
- 提供详细的错误日志
- 保持回退机制不变

### 2. `weread_exporter/export.py` (行106-108) - 图片下载

**当前代码**:
```python
try:
    data = await utils.fetch(url)
except:
    logging.exception(
        "[%s] Fetch image data of %s failed"
        % (self.__class__.__name__, url)
    )
    pos += 10
```

**改进后**:
```python
try:
    data = await utils.fetch(url)
except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
    logging.warning(
        "[%s] Failed to fetch image %s: %s"
        % (self.__class__.__name__, url, str(e))
    )
    # 继续处理下一个图片
    pos += 10
    continue
```

**改进理由**:
- 具体捕获网络相关异常
- 提供更具体的错误信息
- 保持继续处理机制

### 3. `weread_exporter/export.py` (行355-357) - 章节导航

**当前代码**:
```python
except:
    logging.exception(
        "[%s] Go to chapter %s failed"
        % (self.__class__.__name__, chapter["title"])
    )
```

**改进后**:
```python
except (asyncio.TimeoutError, pyppeteer.errors.TimeoutError,
        pyppeteer.errors.NetworkError, RuntimeError) as e:
    logging.error(
        "[%s] Failed to navigate to chapter %s: %s"
        % (self.__class__.__name__, chapter["title"], str(e))
    )
    # 重试逻辑已经存在，保持不变
```

**改进理由**:
- 具体捕获导航相关异常
- 提供详细的错误信息
- 保持现有重试机制

### 4. `weread_exporter/__main__.py` (行242-243) - 主程序入口

**当前代码**:
```python
except:
    import traceback
    traceback.print_exc()
```

**改进后**:
```python
except Exception as e:
    logging.error("Fatal error in main program: %s" % str(e))
    import traceback
    traceback.print_exc()
    return 1  # 返回非零退出码
```

**改进理由**:
- 捕获所有异常但提供具体信息
- 添加错误日志
- 返回适当的退出码

### 5. `weread_exporter/utils.py` (行47-48) - 网络请求

**当前代码**:
```python
except:
    logging.exception("Fetch url %s failed" % url)
```

**改进后**:
```python
except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
    logging.warning(
        "Failed to fetch URL %s (attempt %d/3): %s"
        % (url, attempt + 1, str(e))
    )
    if attempt == 2:  # 最后一次尝试失败
        raise RuntimeError("Fetch url %s failed after 3 attempts" % url)
```

**改进理由**:
- 具体捕获网络相关异常
- 提供尝试次数信息
- 保持重试逻辑但改进错误消息

## 测试计划

### 测试场景

1. **Cookie解析测试**:
   - 测试无效JSON格式的cookie文件
   - 测试遗留格式的cookie文件（分号分隔）
   - 验证错误日志和回退机制

2. **图片下载测试**:
   - 模拟网络错误（404, 500等）
   - 模拟超时错误
   - 验证错误日志和继续处理机制

3. **章节导航测试**:
   - 模拟页面加载超时
   - 模拟网络错误
   - 验证错误日志和重试机制

4. **主程序异常测试**:
   - 模拟致命错误
   - 验证错误日志和退出码

5. **网络请求测试**:
   - 模拟多次失败后的最终异常
   - 验证重试逻辑和错误日志

### 测试方法

1. 创建单元测试用例覆盖每个异常处理场景
2. 使用mock库模拟各种异常情况
3. 验证日志输出和错误处理行为
4. 确保应用程序在错误情况下仍然稳定运行

## 预期效果

1. 所有空except块被具体异常类型替换
2. 错误日志更具体，更易于调试
3. 错误处理更有针对性
4. 代码可维护性显著提高
5. 应用程序稳定性得到增强

## 实施计划

1. 按照上述计划逐个修改每个空except块
2. 为每个修改添加适当的单元测试
3. 运行现有测试套件确保无回归
4. 进行集成测试验证整体功能
5. 部署到生产环境并监控错误日志

## 批准要求

请审阅此计划并确认以下内容：

1. 改进方向是否符合预期
2. 具体异常类型选择是否合适
3. 错误处理逻辑是否合理
4. 测试计划是否全面
5. 是否有其他需要考虑的方面

如有任何修改建议或补充要求，请提供反馈。