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
            sys.executable, "-m", "pip", "list", "--outdated"
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
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ 成功更新 {package_name}")
            return True
        else:
            print(f"✗ 更新 {package_name} 失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 更新 {package_name} 过程中出现错误: {e}")
        return False


def update_all_packages():
    """更新所有依赖包。"""
    print("更新所有依赖包...")
    
    try:
        # 读取requirements.txt
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        success_count = 0
        for req in requirements:
            # 提取包名（忽略版本约束）
            package_name = req.split("==")[0].split(">=")[0].split("<=")[0]
            if update_package(package_name):
                success_count += 1
        
        print(f"\n更新完成: {success_count}/{len(requirements)} 个包成功更新")
        return success_count == len(requirements)
    except Exception as e:
        print(f"更新过程中出现错误: {e}")
        return False


def update_requirements_file():
    """更新requirements.txt文件。"""
    print("更新requirements.txt文件...")
    
    try:
        # 获取当前安装的包版本
        result = subprocess.run([
            sys.executable, "-m", "pip", "freeze"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open("requirements.txt", "w") as f:
                f.write(result.stdout)
            print("✓ requirements.txt 已更新")
            return True
        else:
            print("✗ 获取包列表失败")
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