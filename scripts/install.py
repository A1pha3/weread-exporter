"""项目安装脚本。

负责安装项目依赖和配置环境。
"""

import os
import subprocess
import sys


def check_python_version():
    """检查Python版本。"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return False
    print(f"✓ Python版本: {sys.version}")
    return True


def install_requirements():
    """安装项目依赖。"""
    print("安装项目依赖...")

    try:
        result = subprocess.run([
            "uv", "sync"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 依赖安装成功")
            return True
        else:
            print(f"✗ 依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 安装过程中出现错误: {e}")
        return False


def install_development_deps():
    """安装开发依赖。"""
    print("安装开发依赖...")

    try:
        result = subprocess.run([
            "uv", "sync", "--extra", "dev"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 开发依赖安装成功")
            return True
        else:
            print(f"✗ 开发依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 安装开发依赖过程中出现错误: {e}")
        return False


def setup_environment():
    """设置环境变量。"""
    print("设置环境变量...")
    
    # 添加项目根目录到PYTHONPATH
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print("✓ 环境变量设置完成")
    return True


def install_package():
    """以开发模式安装包。"""
    print("以开发模式安装包...")

    try:
        result = subprocess.run([
            "uv", "pip", "install", "-e", "."
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 包安装成功")
            return True
        else:
            print(f"✗ 包安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 包安装过程中出现错误: {e}")
        return False


def main():
    """主安装函数。"""
    print("开始安装微信读书导出工具...")
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 安装依赖
    if not install_requirements():
        return 1
    
    # 设置环境
    if not setup_environment():
        return 1
    
    # 安装包
    if not install_package():
        return 1
    
    # 可选：安装开发依赖
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        if not install_development_deps():
            return 1
    
    print("\n✓ 安装完成！")
    print("\n使用方法:")
    print("  python -m weread_exporter -b <书籍ID> -o epub -o pdf")
    print("\n开发模式安装:")
    print("  python scripts/install.py --dev")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())