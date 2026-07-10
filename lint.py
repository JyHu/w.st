#!/usr/bin/env python3
"""
StellectList 数据校验脚本
检查清单文件的有效性和重复性
"""

import argparse
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


def save_json_file(file_path: str, data: Dict) -> bool:
    """保存JSON文件，格式化输出"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件错误 {file_path}: {e}")
        return False


def sort_dict_keys(data: Dict) -> Dict:
    """递归地对字典的键进行排序"""
    if isinstance(data, dict):
        sorted_dict = {}
        for key in sorted(data.keys()):
            sorted_dict[key] = sort_dict_keys(data[key])
        return sorted_dict
    elif isinstance(data, list):
        return [sort_dict_keys(item) for item in data]
    else:
        return data


def sort_items(items: List[Dict]) -> List[Dict]:
    """对items数组进行排序，按name字段"""
    return sorted(items, key=lambda x: x.get('name', ''))


def format_list_data(data: Dict) -> Dict:
    """格式化清单数据"""
    # 确保必填字段存在
    required_fields = ['id', 'name', 'desc', 'icon', 'category', 'date', 'items']
    for field in required_fields:
        if field not in data:
            data[field] = '' if field != 'items' else []
    
    # 格式化date字段（如果是字符串格式，转换为时间戳）
    if isinstance(data['date'], str):
        try:
            # 尝试解析YYYY-MM-DD格式
            dt = datetime.strptime(data['date'], '%Y-%m-%d')
            data['date'] = int(dt.timestamp())
        except ValueError:
            pass  # 保持原样
    
    # 排序items
    if 'items' in data and isinstance(data['items'], list):
        data['items'] = sort_items(data['items'])
    
    # 递归排序所有字典键
    return sort_dict_keys(data)


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
    parser = argparse.ArgumentParser(description='校验和格式化清单文件')
    parser.add_argument('--format-only', action='store_true', help='只格式化文件，不进行校验')
    parser.add_argument('--check-only', action='store_true', help='只校验文件，不进行格式化')
    
    args = parser.parse_args()
    
    errors_found = False
    files_formatted = 0
    
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
    
    # 处理每个清单
    for file_path, location in list_files:
        print(f"\n处理清单: {file_path}")
        
        list_data = load_json_file(file_path)
        if list_data is None:
            errors_found = True
            continue
        
        # 格式化数据
        formatted_data = format_list_data(list_data.copy())
        
        # 如果需要格式化且数据有变化，则保存
        should_format = not args.check_only
        if should_format:
            # 比较原始数据和格式化后的数据
            original_str = json.dumps(list_data, ensure_ascii=False, indent=2, sort_keys=True)
            formatted_str = json.dumps(formatted_data, ensure_ascii=False, indent=2, sort_keys=True)
            
            if original_str != formatted_str:
                print(f"  📝 格式化文件...")
                if save_json_file(file_path, formatted_data):
                    files_formatted += 1
                    print(f"  ✅ 文件已格式化")
                else:
                    print(f"  ❌ 文件格式化失败")
                    errors_found = True
        
        # 如果不是仅格式化模式，则进行校验
        if not args.format_only:
            # 检查单个清单
            errors = check_single_list(file_path, formatted_data)
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
                errors_found = True
            else:
                print(f"  ✅ 单个清单检查通过")
            
            # 收集items用于重复检查
            if 'items' in formatted_data:
                for item in formatted_data['items']:
                    if 'name' in item:
                        all_items.append((file_path, formatted_data.get('id', 'unknown'), item['name']))
    
    # 如果不是仅格式化模式，则检查跨清单重复
    if not args.format_only:
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
    if args.format_only:
        print(f"✅ 格式化完成，共处理 {files_formatted} 个文件")
        sys.exit(0)
    elif args.check_only:
        if errors_found:
            print("❌ 发现错误，校验失败")
            sys.exit(1)
        else:
            print("✅ 所有检查通过")
            sys.exit(0)
    else:
        if files_formatted > 0:
            print(f"📝 共格式化了 {files_formatted} 个文件")
        if errors_found:
            print("❌ 发现错误，校验失败")
            sys.exit(1)
        else:
            print("✅ 所有检查通过")
            sys.exit(0)


if __name__ == "__main__":
    main()