# 故障排除指南

## 快速诊断

### 症状识别表

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| 命令未找到 | 未正确安装或PATH问题 | 重新安装或检查PATH |
| 浏览器启动失败 | Chrome未安装或版本不兼容 | 安装Chrome或指定路径 |
| 登录失败 | 网络问题或账号限制 | 检查网络或重新登录 |
| 内容导出为空 | Hook脚本未正确注入 | 检查浏览器控制台 |
| 内存不足 | 书籍过大或内存泄漏 | 增加内存或分批处理 |
| 网络超时 | 网络不稳定或代理问题 | 调整超时时间或检查代理 |

## 安装问题

### 问题1: 命令未找到

**症状**:
```bash
weread-exporter: command not found
```

**解决方案**:

1. **检查安装状态**:
```bash
pip show weread-exporter
```

2. **重新安装**:
```bash
pip uninstall weread-exporter
pip install weread-exporter
```

3. **检查PATH环境变量**:
```bash
# Windows
echo %PATH%

# macOS/Linux
echo $PATH
```

4. **使用Python模块方式**:
```bash
python -m weread_exporter --help
```

### 问题2: 依赖安装失败

**症状**:
```bash
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案**:

1. **更新pip**:
```bash
pip install --upgrade pip
```

2. **使用国内镜像源**:
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple weread-exporter
```

3. **安装系统依赖**:
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential libssl-dev

# CentOS/RHEL
sudo yum install python3-devel gcc openssl-devel
```

## 浏览器问题

### 问题3: 浏览器启动失败

**症状**:
```bash
BrowserError: Failed to launch browser
```

**解决方案**:

1. **检查Chrome安装**:
```bash
# Windows
where chrome

# macOS
which google-chrome

# Linux
which google-chrome || which chromium
```

2. **手动指定浏览器路径**:
```bash
export CHROMIUM_PATH="/path/to/chrome"
weread-exporter -b BOOK_ID -o epub
```

3. **安装Chrome**:
- Windows: 从官网下载安装
- macOS: `brew install --cask google-chrome`
- Linux: 使用包管理器安装

### 问题4: 浏览器版本不兼容

**症状**:
```bash
ProtocolError: Protocol error...
```

**解决方案**:

1. **更新Chrome到最新版本**
2. **使用兼容模式**:
```bash
weread-exporter -b BOOK_ID -o epub --compatibility-mode
```

3. **降级Pyppeteer**:
```bash
pip install pyppeteer==1.0.2
```

## 网络问题

### 问题5: 网络连接超时

**症状**:
```bash
TimeoutError: Navigation timeout of 30000 ms exceeded
```

**解决方案**:

1. **增加超时时间**:
```bash
weread-exporter -b BOOK_ID -o epub --load-timeout 180
```

2. **检查网络连接**:
```bash
# 测试网络连接
ping weread.qq.com

# 检查DNS解析
nslookup weread.qq.com
```

3. **使用代理**:
```bash
weread-exporter -b BOOK_ID -o epub --proxy-server http://proxy:8080
```

### 问题6: SSL证书错误

**症状**:
```bash
SSL: CERTIFICATE_VERIFY_FAILED
```

**解决方案**:

1. **更新证书**:
```bash
# macOS
/Applications/Python\ 3.9/Install\ Certificates.command

# 或手动安装
pip install certifi
/usr/bin/python -m certifi
```

2. **跳过SSL验证（不推荐）**:
```bash
export PYPPETEER_SKIP_SSL_VERIFY=true
```

## 登录和认证问题

### 问题7: 登录失败

**症状**:
```bash
LoginError: Failed to authenticate
```

**解决方案**:

1. **强制重新登录**:
```bash
weread-exporter -b BOOK_ID -o epub --force-login
```

2. **清除登录缓存**:
```bash
rm -rf ~/.weread/cookies.json
```

3. **手动登录检查**:
```bash
# 打开浏览器手动登录
weread-exporter -b BOOK_ID -o epub --no-headless
```

### 问题8: 账号限制

**症状**:
```bash
AccountLimitError: Daily download limit exceeded
```

**解决方案**:

1. **等待限制解除**（通常24小时）
2. **分批处理书籍**
3. **使用多个账号轮换**

## 内容导出问题

### 问题9: 导出内容为空

**症状**: 导出的文件存在但内容为空

**解决方案**:

1. **启用调试模式**:
```bash
weread-exporter -b BOOK_ID -o epub --verbose --debug
```

2. **检查Hook脚本注入**:
```bash
# 查看浏览器控制台输出
weread-exporter -b BOOK_ID -o epub --no-headless
```

3. **手动验证书籍可访问性**:
```bash
# 在浏览器中手动访问书籍URL
open "https://weread.qq.com/web/bookDetail/BOOK_ID"
```

### 问题10: 样式丢失或错乱

**症状**: 导出的文件样式不正确

**解决方案**:

1. **使用自定义CSS**:
```css
/* custom.css */
body { font-family: "Microsoft YaHei"; }
```

```bash
weread-exporter -b BOOK_ID -o epub --css-file custom.css
```

2. **检查CSS兼容性**:
- EPUB: 确保CSS支持EPUB标准
- PDF: 使用WeasyPrint兼容的CSS

## 性能问题

### 问题11: 内存不足

**症状**:
```bash
MemoryError: Out of memory
```

**解决方案**:

1. **分批处理大书籍**:
```bash
# 分章节导出
weread-exporter -b BOOK_ID -o epub --chunk-size 10
```

2. **增加系统内存**
3. **优化导出设置**:
```bash
weread-exporter -b BOOK_ID -o epub --optimize-memory
```

### 问题12: 导出速度过慢

**症状**: 导出过程非常缓慢

**解决方案**:

1. **使用无头模式**:
```bash
weread-exporter -b BOOK_ID -o epub --headless
```

2. **调整加载参数**:
```bash
weread-exporter -b BOOK_ID -o epub --load-interval 5 --load-timeout 60
```

3. **优化网络连接**:
- 使用有线网络
- 关闭其他网络应用
- 使用本地代理缓存

## 格式转换问题

### 问题13: EPUB生成失败

**症状**:
```bash
EPUBError: Failed to generate EPUB file
```

**解决方案**:

1. **检查EbookLib版本**:
```bash
pip show ebooklib
```

2. **验证Markdown内容**:
```bash
# 先导出为Markdown检查内容
weread-exporter -b BOOK_ID -o md
```

3. **使用简化模式**:
```bash
weread-exporter -b BOOK_ID -o epub --simple-mode
```

### 问题14: PDF生成问题

**症状**: PDF文件损坏或无法打开

**解决方案**:

1. **检查WeasyPrint安装**:
```bash
# 验证WeasyPrint
python -c "import weasyprint; print('OK')"
```

2. **安装系统依赖**:
```bash
# Ubuntu/Debian
sudo apt install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0

# macOS
brew install cairo pango gdk-pixbuf
```

3. **使用替代PDF生成器**:
```bash
weread-exporter -b BOOK_ID -o epub  # 先导出EPUB
# 然后使用其他工具转换EPUB到PDF
```

## 平台特定问题

### Windows系统问题

#### 问题15: DLL加载失败

**症状**:
```bash
DLL load failed while importing...
```

**解决方案**:

1. **安装Visual C++ Redistributable**:
- 下载: https://aka.ms/vs/16/release/vc_redist.x64.exe

2. **使用兼容的Python版本**
3. **以管理员身份运行命令提示符**

#### 问题16: 路径长度限制

**症状**: 文件路径过长错误

**解决方案**:

1. **使用短路径**:
```bash
weread-exporter -b BOOK_ID -o epub -d C:\\short
```

2. **启用长路径支持**:
- 编辑注册表启用长路径
- 或使用WSL

### macOS系统问题

#### 问题17: 权限被拒绝

**症状**:
```bash
Permission denied: /usr/local/bin
```

**解决方案**:

1. **使用用户安装**:
```bash
pip install --user weread-exporter
```

2. **使用虚拟环境**:
```bash
python -m venv venv
source venv/bin/activate
pip install weread-exporter
```

#### 问题18: Gatekeeper阻止

**症状**: "无法打开应用，因为无法验证开发者"

**解决方案**:

1. **系统偏好设置 → 安全性与隐私 → 允许**
2. **或使用命令行绕过**:
```bash
sudo spctl --master-disable
```

### Linux系统问题

#### 问题19: 缺少系统库

**症状**: 依赖库未找到

**解决方案**:

1. **安装系统依赖**:
```bash
# Ubuntu/Debian
sudo apt install libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1

# CentOS/RHEL
sudo yum install alsa-lib cups-libs libXcomposite libXrandr pango
```

#### 问题20: 字体缺失

**症状**: 中文显示为方块

**解决方案**:

1. **安装中文字体**:
```bash
# Ubuntu/Debian
sudo apt install fonts-wqy-microhei fonts-wqy-zenhei

# CentOS/RHEL
sudo yum install wqy-microhei-fonts wqy-zenhei-fonts
```

## 高级调试技巧

### 启用详细日志

```bash
# 启用所有调试信息
weread-exporter -b BOOK_ID -o epub --verbose --debug --log-file debug.log

# 查看日志文件
tail -f debug.log
```

### 浏览器调试模式

```bash
# 显示浏览器界面
weread-exporter -b BOOK_ID -o epub --no-headless

# 打开开发者工具查看控制台错误
```

### 网络抓包分析

```bash
# 使用tcpdump分析网络请求
sudo tcpdump -i any -w weread.pcap host weread.qq.com

# 使用Wireshark分析pcap文件
wireshark weread.pcap
```

### 内存使用监控

```bash
# 实时监控内存使用
while true; do
    ps aux | grep weread-exporter | grep -v grep | awk '{print $6/1024 "MB"}'
    sleep 5
done
```

## 预防措施

### 定期维护

1. **清理缓存**:
```bash
rm -rf ~/.weread/cache
rm -rf ~/.cache/pyppeteer
```

2. **更新依赖**:
```bash
pip install --upgrade weread-exporter
```

3. **检查磁盘空间**:
```bash
df -h  # 检查磁盘使用情况
```

### 最佳实践

1. **使用虚拟环境**避免依赖冲突
2. **定期备份重要数据**
3. **监控系统资源使用情况**
4. **保持系统和软件更新**

## 获取更多帮助

如果以上解决方案都无法解决问题：

1. **查看项目Issues**: https://github.com/drunkdream/weread-exporter/issues
2. **提交新的Issue**并提供详细信息：
   - 操作系统和版本
   - Python版本
   - 完整的错误信息
   - 重现步骤

3. **社区支持**:
   - 项目Wiki页面
   - 相关技术论坛
   - Stack Overflow

---

**记住**: 大多数问题都有解决方案。保持耐心，按照步骤排查，您一定能成功使用这个强大的工具！ 🔧