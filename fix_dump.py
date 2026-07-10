#!/usr/bin/env python3
"""
StellectList 修复脚本
移除指定文件中的重复内容，以name为准，对重复的内容只保留1个
"""

import json
import argparse
import sys
from pathlib import Path


def load_json_file(file_path: str) -> dict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 {file_path}: {e}")
        return None
    except Exception as e:
        print(f"读取文件错误 {file_path}: {e}")
        return None


def save_json_file(file_path: str, data: dict) -> bool:
    """保存JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件错误 {file_path}: {e}")
        return False


def remove_duplicate_items(data: dict) -> tuple[int, int]:
    """
    移除重复的items，以name为准
    返回：(移除的数量, 保留的数量)
    """
    if 'items' not in data or not isinstance(data['items'], list):
        return 0, len(data.get('items', []))
    
    items = data['items']
    seen_names = set()
    unique_items = []
    removed_count = 0
    
    for item in items:
        if 'name' not in item:
            # 如果没有name字段，保留原样
            unique_items.append(item)
            continue
            
        item_name = item['name']
        if item_name not in seen_names:
            # 第一次见到这个name，保留
            seen_names.add(item_name)
            unique_items.append(item)
        else:
            # 重复的name，移除
            removed_count += 1
    
    data['items'] = unique_items
    return removed_count, len(unique_items)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='移除指定文件中的重复内容')
    parser.add_argument('file', help='要处理的JSON文件路径')
    
    args = parser.parse_args()
    file_path = args.file
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"错误：文件不存在 {file_path}")
        sys.exit(1)
    
    # 加载文件
    print(f"正在处理文件: {file_path}")
    data = load_json_file(file_path)
    if data is None:
        print("文件加载失败")
        sys.exit(1)
    
    # 检查并移除重复项
    removed_count, kept_count = remove_duplicate_items(data)
    
    if removed_count > 0:
        print(f"发现并移除了 {removed_count} 个重复项")
        print(f"保留了 {kept_count} 个唯一项")
        
        # 保存文件
        if save_json_file(file_path, data):
            print(f"文件已保存: {file_path}")
        else:
            print("文件保存失败")
            sys.exit(1)
    else:
        print("未发现重复项")
    
    print("处理完成")


if __name__ == "__main__":
    main()