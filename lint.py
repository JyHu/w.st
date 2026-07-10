#!/usr/bin/env python3
"""
StellectList 数据校验脚本
检查清单文件的有效性和重复性
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


def is_valid_uuid(uuid_str: str) -> bool:
    """
    检查是否为有效的UUID格式（大写）
    B2C3D4E5-F6G7-8901-BCDE-F23456789012
    """
    pattern = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$'
    return bool(re.match(pattern, uuid_str))


def is_valid_timestamp(timestamp: int) -> bool:
    """检查时间戳是否在有效范围内（2026-01-01 至 2050）"""
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2050, 12, 31)
    
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    return start_timestamp <= timestamp <= end_timestamp


def load_json_file(file_path: str) -> Dict:
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


def check_single_list(file_path: str, list_data: Dict) -> List[str]:
    """检查单个清单的有效性"""
    errors = []
    
    # 检查必填字段
    required_fields = ['id', 'name', 'desc', 'icon', 'category', 'date', 'items']
    for field in required_fields:
        if field not in list_data:
            errors.append(f"缺少必填字段: {field}")
    
    if errors:
        return errors
    
    # 检查id格式
    if not is_valid_uuid(list_data['id']):
        errors.append("id格式无效，应为UUID格式且大写")
    
    # 检查date格式和范围
    if isinstance(list_data['date'], int):
        if not is_valid_timestamp(list_data['date']):
            errors.append("date超出有效范围（2026-01-01 至 2050）")
    else:
        errors.append("date应为整数类型（秒级时间戳）")
    
    # 检查items
    items = list_data['items']
    if not isinstance(items, list):
        errors.append("items应为数组")
    elif len(items) == 0:
        errors.append("items不能为空数组")
    else:
        # 检查items中的重复name
        names = []
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"items[{i}]不是对象")
                continue
            
            if 'name' not in item:
                errors.append(f"items[{i}]缺少name字段")
            else:
                if item['name'] in names:
                    errors.append(f"items[{i}]的name重复: {item['name']}")
                names.append(item['name'])
            
            if 'desc' not in item:
                errors.append(f"items[{i}]缺少desc字段")
    
    return errors


def find_duplicate_items(all_items: List[Tuple[str, str, str]]) -> List[Tuple[str, List[str]]]:
    """查找跨清单重复的items（排除同一文件内的重复）"""
    name_to_files = {}
    
    for file_path, list_id, item_name in all_items:
        if item_name not in name_to_files:
            name_to_files[item_name] = []
        name_to_files[item_name].append((file_path, list_id))
    
    duplicates = []
    for item_name, file_list in name_to_files.items():
        # 只保留出现在不同文件中的重复项
        unique_files = set()
        cross_file_duplicates = []
        
        for file_path, list_id in file_list:
            if file_path not in unique_files:
                unique_files.add(file_path)
                cross_file_duplicates.append((file_path, list_id))
        
        # 如果有跨文件重复，才添加到结果中
        if len(cross_file_duplicates) > 1:
            details = [f"{file_path} (清单ID: {list_id})" for file_path, list_id in cross_file_duplicates]
            duplicates.append((item_name, details))
    
    return duplicates


def main():
    """主函数"""
    errors_found = False
    
    # 收集所有清单文件
    list_files = []
    
    # 扫描lists目录
    lists_dir = Path("lists")
    if lists_dir.exists():
        for category_dir in lists_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('_'):
                for json_file in category_dir.glob("*.json"):
                    if not json_file.name.startswith('_'):
                        list_files.append((str(json_file), "lists"))
    
    # 扫描tmps目录
    tmps_dir = Path("tmps")
    if tmps_dir.exists():
        for json_file in tmps_dir.glob("*.json"):
            list_files.append((str(json_file), "tmps"))
    
    print(f"发现 {len(list_files)} 个清单文件")
    
    # 存储所有items用于重复检查
    all_items = []
    
    # 检查每个清单
    for file_path, location in list_files:
        print(f"\n检查清单: {file_path}")
        
        list_data = load_json_file(file_path)
        if list_data is None:
            errors_found = True
            continue
        
        # 检查单个清单
        errors = check_single_list(file_path, list_data)
        if errors:
            for error in errors:
                print(f"  ❌ {error}")
            errors_found = True
        else:
            print(f"  ✅ 单个清单检查通过")
        
        # 收集items用于重复检查
        if 'items' in list_data:
            for item in list_data['items']:
                if 'name' in item:
                    all_items.append((file_path, list_data.get('id', 'unknown'), item['name']))
    
    # 检查跨清单重复
    print(f"\n检查跨清单重复...")
    duplicates = find_duplicate_items(all_items)
    
    if duplicates:
        for item_name, file_details in duplicates:
            print(f"  ❌ 重复项: {item_name}")
            for detail in file_details:
                print(f"    - {detail}")
        errors_found = True
    else:
        print(f"  ✅ 无跨清单重复")
    
    # 输出总结
    print(f"\n{'='*50}")
    if errors_found:
        print("❌ 发现错误，校验失败")
        sys.exit(1)
    else:
        print("✅ 所有检查通过")
        sys.exit(0)


if __name__ == "__main__":
    main()