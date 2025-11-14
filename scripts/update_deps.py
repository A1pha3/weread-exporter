"""依赖更新脚本。

负责检查和更新项目依赖。
"""

import subprocess
import sys


def check_outdated_packages():
    """检查过时的依赖包。"""
    print("检查过时的依赖包...")
    
    try:
        result = subprocess.run([
            "uv", "pip", "list", "--outdated"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("过时的包:")
            print(result.stdout)
            return True
        else:
            print("检查失败")
            return False
    except Exception as e:
        print(f"检查过程中出现错误: {e}")
        return False


def update_package(package_name):
    """更新指定的包。"""
    print(f"更新包: {package_name}")

    try:
        add_result = subprocess.run([
            "uv", "add", package_name
        ], capture_output=True, text=True)

        if add_result.returncode != 0:
            print(f"✗ 更新 {package_name} 失败: {add_result.stderr}")
            return False

        sync_result = subprocess.run([
            "uv", "sync"
        ], capture_output=True, text=True)

        if sync_result.returncode == 0:
            print(f"✓ 成功更新 {package_name}")
            return True
        else:
            print(f"✗ 同步依赖失败: {sync_result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 更新 {package_name} 过程中出现错误: {e}")
        return False


def update_all_packages():
    """更新所有依赖包。"""
    print("更新所有依赖包...")

    try:
        lock_result = subprocess.run([
            "uv", "lock", "--upgrade"
        ], capture_output=True, text=True)

        if lock_result.returncode != 0:
            print(f"✗ 生成锁文件失败: {lock_result.stderr}")
            return False

        sync_result = subprocess.run([
            "uv", "sync"
        ], capture_output=True, text=True)

        if sync_result.returncode == 0:
            print("✓ 所有依赖已升级并同步")
            return True
        else:
            print(f"✗ 同步依赖失败: {sync_result.stderr}")
            return False
    except Exception as e:
        print(f"更新过程中出现错误: {e}")
        return False


def update_requirements_file():
    """更新requirements.txt文件。"""
    print("更新requirements.txt文件...")

    try:
        result = subprocess.run([
            "uv", "export", "-o", "requirements.txt"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ requirements.txt 已根据锁文件导出")
            return True
        else:
            print(f"✗ 导出失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 更新requirements.txt过程中出现错误: {e}")
        return False


def main():
    """主更新函数。"""
    import argparse
    
    parser = argparse.ArgumentParser(description="更新项目依赖")
    parser.add_argument("--check", action="store_true", help="只检查不更新")
    parser.add_argument("--package", help="更新指定的包")
    parser.add_argument("--all", action="store_true", help="更新所有包")
    parser.add_argument("--update-file", action="store_true", help="更新requirements.txt文件")
    
    args = parser.parse_args()
    
    if args.check:
        return 0 if check_outdated_packages() else 1
    elif args.package:
        return 0 if update_package(args.package) else 1
    elif args.all:
        return 0 if update_all_packages() else 1
    elif args.update_file:
        return 0 if update_requirements_file() else 1
    else:
        print("请指定操作选项:")
        print("  --check         检查过时的包")
        print("  --package NAME  更新指定的包")
        print("  --all           更新所有包")
        print("  --update-file   更新requirements.txt文件")
        return 1


if __name__ == "__main__":
    sys.exit(main())