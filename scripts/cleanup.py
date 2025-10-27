"""项目清理脚本。

负责清理临时文件、缓存和构建产物。
"""

import os
import shutil
import sys


def clean_cache():
    """清理缓存目录。"""
    cache_dirs = ['cache', 'output', 'dist', 'build']
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"清理目录: {cache_dir}")
            shutil.rmtree(cache_dir)
            print(f"✓ 已清理 {cache_dir}")


def clean_pycache():
    """清理Python缓存文件。"""
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"清理Python缓存: {pycache_path}")
            shutil.rmtree(pycache_path)
            print(f"✓ 已清理 {pycache_path}")


def clean_temp_files():
    """清理临时文件。"""
    temp_files = [
        'version.py',
        'version_file.txt',
        'main.py',
        'webpage.html',
        'screenshot.jpg'
    ]
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            print(f"清理临时文件: {temp_file}")
            os.remove(temp_file)
            print(f"✓ 已清理 {temp_file}")


def main():
    """主清理函数。"""
    print("开始清理项目...")
    
    try:
        clean_cache()
        clean_pycache()
        clean_temp_files()
        
        print("\n✓ 项目清理完成")
        return 0
    except Exception as e:
        print(f"\n✗ 清理过程中出现错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())