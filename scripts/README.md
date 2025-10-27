# 脚本工具包

本目录包含微信读书导出工具的各种辅助脚本。

## 脚本说明

### 1. build.py
**项目构建脚本**
- 使用PyInstaller构建可执行文件
- 支持Windows、Linux、macOS平台
- 自动处理版本信息和资源文件

**使用方法：**
```bash
python scripts/build.py --backend pyinstaller --version 1.0.0
```

### 2. install.py
**项目安装脚本**
- 检查Python版本兼容性
- 安装项目依赖
- 设置开发环境
- 支持开发模式安装

**使用方法：**
```bash
# 基本安装
python scripts/install.py

# 开发模式安装（包含开发工具）
python scripts/install.py --dev
```

### 3. test_runner.py
**测试运行器**
- 自动发现和运行测试套件
- 提供详细的测试报告
- 支持持续集成环境

**使用方法：**
```bash
python scripts/test_runner.py
```

### 4. cleanup.py
**项目清理脚本**
- 清理缓存目录和临时文件
- 删除Python编译缓存
- 保持项目目录整洁

**使用方法：**
```bash
python scripts/cleanup.py
```

### 5. update_deps.py
**依赖更新脚本**
- 检查过时的依赖包
- 更新指定的包或所有包
- 自动更新requirements.txt文件

**使用方法：**
```bash
# 检查过时的包
python scripts/update_deps.py --check

# 更新所有包
python scripts/update_deps.py --all

# 更新指定的包
python scripts/update_deps.py --package requests

# 更新requirements.txt文件
python scripts/update_deps.py --update-file
```

## 开发工作流

### 标准开发流程
1. **环境准备**
   ```bash
   python scripts/install.py --dev
   ```

2. **运行测试**
   ```bash
   python scripts/test_runner.py
   ```

3. **代码清理**
   ```bash
   python scripts/cleanup.py
   ```

4. **依赖更新**
   ```bash
   python scripts/update_deps.py --check
   ```

### 发布流程
1. **构建发布包**
   ```bash
   python scripts/build.py --backend pyinstaller --version 1.0.0
   ```

2. **测试构建结果**
   ```bash
   # 测试生成的可执行文件
   ./dist/weread-exporter --help
   ```

## 环境要求

- Python 3.7+
- pip 最新版本
- 适当的系统权限（用于安装包）

## 注意事项

1. **权限问题**：某些操作可能需要管理员权限
2. **网络连接**：安装和更新依赖需要网络连接
3. **兼容性**：确保Python版本与项目要求一致
4. **备份**：重要操作前建议备份项目文件

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 使用sudo（Linux/macOS）
   sudo python scripts/install.py
   
   # 或以管理员身份运行（Windows）
   ```

2. **网络连接问题**
   - 检查网络连接
   - 尝试使用国内镜像源
   - 配置代理设置

3. **依赖冲突**
   - 清理虚拟环境
   - 重新安装依赖
   - 检查版本兼容性

### 获取帮助

如果遇到问题，请：
1. 检查错误信息
2. 查看相关文档
3. 提交Issue到项目仓库