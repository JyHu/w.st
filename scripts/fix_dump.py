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


def find_all_json_files():
    """查找所有JSON文件"""
    json_files = []
    
    # 扫描 lists 目录
    lists_dir = Path("lists")
    if lists_dir.exists():
        for file_path in lists_dir.rglob("*.json"):
            if not file_path.name.startswith("_"):  # 跳过索引文件
                json_files.append((str(file_path), "lists"))
    
    # 扫描 tmps 目录
    tmps_dir = Path("tmps")
    if tmps_dir.exists():
        for file_path in tmps_dir.rglob("*.json"):
            if not file_path.name.startswith("_"):  # 跳过索引文件
                json_files.append((str(file_path), "tmps"))
    
    return json_files


def find_cross_file_duplicates():
    """查找跨文件的重复项"""
    json_files = find_all_json_files()
    name_to_files = {}
    
    # 收集所有条目及其来源文件
    for file_path, file_type in json_files:
        data = load_json_file(file_path)
        if data is None or 'items' not in data:
            continue
            
        for item in data['items']:
            if 'name' not in item:
                continue
                
            item_name = item['name']
            if item_name not in name_to_files:
                name_to_files[item_name] = []
            name_to_files[item_name].append({
                'file_path': file_path,
                'file_type': file_type,
                'item': item
            })
    
    # 找出重复项
    duplicates = {}
    for name, entries in name_to_files.items():
        if len(entries) > 1:
            duplicates[name] = entries
    
    return duplicates, json_files


def remove_cross_file_duplicates():
    """移除跨文件的重复项"""
    duplicates, json_files = find_cross_file_duplicates()
    
    if not duplicates:
        print("未发现跨文件重复项")
        return 0
    
    print(f"发现 {len(duplicates)} 个跨文件重复项")
    
    # 按优先级排序：lists > tmps
    # 对于每个重复项，优先保留lists目录下的，删除tmps目录下的
    # 如果都在同一个目录，保留第一个遇到的
    
    total_removed = 0
    
    for name, entries in duplicates.items():
        # 按优先级排序：lists > tmps
        entries.sort(key=lambda x: (x['file_type'] != 'lists', x['file_path']))
        
        # 保留第一个，删除其他的
        kept_entry = entries[0]
        removed_entries = entries[1:]
        
        print(f"\n重复项: {name}")
        print(f"保留: {kept_entry['file_path']} ({kept_entry['file_type']})")
        
        for removed_entry in removed_entries:
            print(f"删除: {removed_entry['file_path']} ({removed_entry['file_type']})")
            
            # 从文件中移除该条目
            data = load_json_file(removed_entry['file_path'])
            if data is None:
                continue
                
            if 'items' in data:
                original_count = len(data['items'])
                data['items'] = [item for item in data['items'] 
                               if item.get('name') != name]
                removed_count = original_count - len(data['items'])
                
                if removed_count > 0:
                    if save_json_file(removed_entry['file_path'], data):
                        total_removed += removed_count
                        print(f"  已从文件中移除 {removed_count} 个重复项")
                    else:
                        print(f"  移除失败: {removed_entry['file_path']}")
    
    print(f"\n总共移除了 {total_removed} 个跨文件重复项")
    return total_removed


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='移除指定文件中的重复内容')
    parser.add_argument('file', nargs='?', help='要处理的JSON文件路径')
    parser.add_argument('-all', action='store_true', help='处理所有清单文件，移除跨文件重复项')
    
    args = parser.parse_args()
    
    if args.all:
        # 处理所有文件，移除跨文件重复项
        removed_count = remove_cross_file_duplicates()
        print(f"处理完成，共移除了 {removed_count} 个跨文件重复项")
    else:
        # 处理单个文件
        if not args.file:
            print("错误：必须指定文件路径或使用 -all 参数")
            sys.exit(1)
            
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