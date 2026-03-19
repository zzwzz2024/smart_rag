#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM清理脚本 - Python版本
使用方法: python fix_bom.py
脚本会提示用户输入模块名和文件类型
"""

import os
import sys
import glob
import codecs


def remove_bom_from_file(file_path):
    """移除单个文件的BOM字符"""
    try:
        # 以二进制模式读取文件
        with open(file_path, 'rb') as f:
            content = f.read()

        # 检查UTF-8 BOM (EF BB BF)
        if len(content) >= 3 and content[0] == 0xEF and content[1] == 0xBB and content[2] == 0xBF:
            print(f"✓ 发现BOM: {os.path.basename(file_path)}")

            # 移除BOM，重新写入
            new_content = content[3:]
            with open(file_path, 'wb') as f:
                f.write(new_content)
            return True

        # 检查UTF-16 LE BOM (FF FE)
        elif len(content) >= 2 and content[0] == 0xFF and content[1] == 0xFE:
            print(f"✓ 发现UTF-16 LE BOM: {os.path.basename(file_path)}")

            # 转换为UTF-8无BOM
            text_content = content[2:].decode('utf-16-le')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True

        # 检查UTF-16 BE BOM (FE FF)
        elif len(content) >= 2 and content[0] == 0xFE and content[1] == 0xFF:
            print(f"✓ 发现UTF-16 BE BOM: {os.path.basename(file_path)}")

            # 转换为UTF-8无BOM
            text_content = content[2:].decode('utf-16-be')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            return True

        return False

    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        return False


def get_user_input():
    """获取用户输入的模块名和文件类型"""
    print("=" * 50)
    print("BOM清理工具")
    print("=" * 50)

    # 获取模块名（支持相对路径）
    while True:
        module_name = input("请输入模块名或相对路径（直接回车使用当前目录）: ").strip()
        if module_name:
            break
        module_name = "."  # 使用当前目录
        break

    # 获取文件类型
    file_type = input("请输入文件类型(默认为*.java，直接回车使用默认值): ").strip()
    if not file_type:
        file_type = "*.java"

    return module_name, file_type


def main():
    # 获取用户输入
    module_name, file_pattern = get_user_input()

    # 如果用户输入的是相对路径，使用当前工作目录
    if module_name == ".":
        module_path = os.getcwd()
    else:
        module_path = os.path.abspath(module_name)

    if not os.path.exists(module_path):
        print(f"错误: 路径不存在 {module_path}")
        return

    print(f"\n开始处理路径: {module_path}")
    print(f"文件类型: {file_pattern}")

    total_files = 0
    bom_files = 0

    # 使用glob搜索文件
    search_pattern = os.path.join(module_path, "**", file_pattern)
    files = glob.glob(search_pattern, recursive=True)

    for file_path in files:
        if os.path.isfile(file_path):
            total_files += 1
            if remove_bom_from_file(file_path):
                bom_files += 1

    print(f"\n处理完成!")
    print(f"总文件数: {total_files}")
    print(f"含BOM文件数: {bom_files}")


if __name__ == "__main__":
    main()
