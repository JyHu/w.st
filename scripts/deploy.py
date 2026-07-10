#!/usr/bin/env python3
"""
Deploy script for StellectList.
Validates JSON files in lists/ and tmps/ directories,
moves valid files to lists/<category>/, invalid files to tmps/,
and generates indexes.
"""

import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
LISTS_DIR = ROOT_DIR / "lists"
TMPS_DIR = ROOT_DIR / "tmps"
ROOT_INDEX = ROOT_DIR / "indexes.json"
RELEASE_DIR = ROOT_DIR / "release"
RELEASE_ZIP = RELEASE_DIR / "stellect_release.zip"
RELEASE_META = RELEASE_DIR / "release.json"

REQUIRED_FIELDS = {"id", "name", "desc", "icon", "category", "date", "items"}
REQUIRED_ITEM_FIELDS = {"name"}
OPTIONAL_ITEM_FIELDS = {"desc", "address", "latitude", "longitude"}
CATEGORY_INDEX_NAME = "_indexes.json"


def load_category_index(category_dir):
    """Load _indexes.json from a category directory."""
    cat_index_file = category_dir / CATEGORY_INDEX_NAME
    if not cat_index_file.exists():
        return {}
    try:
        with open(cat_index_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {}


def validate_item(item, index):
    """Validate a single item in the items array."""
    errors = []
    if not isinstance(item, dict):
        errors.append(f"  items[{index}]: not a valid object")
        return errors

    for field in REQUIRED_ITEM_FIELDS:
        if field not in item:
            errors.append(f"  items[{index}]: missing required field '{field}'")
        elif not isinstance(item[field], str) or not item[field].strip():
            errors.append(f"  items[{index}]: field '{field}' must be a non-empty string")

    if "latitude" in item:
        if not isinstance(item["latitude"], (int, float)):
            errors.append(f"  items[{index}]: 'latitude' must be a number")
    if "longitude" in item:
        if not isinstance(item["longitude"], (int, float)):
            errors.append(f"  items[{index}]: 'longitude' must be a number")

    # Check for unexpected fields
    allowed = REQUIRED_ITEM_FIELDS | OPTIONAL_ITEM_FIELDS
    for key in item:
        if key not in allowed:
            errors.append(f"  items[{index}]: unexpected field '{key}'")

    return errors


def validate_json_file(filepath):
    """Validate a JSON file against the schema. Returns (data, errors)."""
    errors = []

    # Content files must not start with underscore
    if filepath.name.startswith("_"):
        return None, [f"File name must not start with '_' (reserved for index files)"]

    # Check if file name matches list id (this should be the first check)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extract expected filename from id field
        if "id" in data:
            expected_filename = f"{data['id']}.json"
            if filepath.name != expected_filename:
                errors.append(f"File name mismatch: expected '{expected_filename}', got '{filepath.name}'")
                # Note: We'll handle the actual renaming in update_list_file to avoid conflicts
    except (json.JSONDecodeError, OSError):
        # If we can't read the file, let the other validation checks handle it
        pass

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return None, [f"Invalid JSON: {e}"]
    except Exception as e:
        return None, [f"Cannot read file: {e}"]

    if not isinstance(data, dict):
        return None, ["Root must be a JSON object"]

    # Check required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field '{field}'")

    # Validate field types
    if "id" in data and (not isinstance(data["id"], str) or not data["id"].strip()):
        errors.append("'id' must be a non-empty string")
    if "name" in data and (not isinstance(data["name"], str) or not data["name"].strip()):
        errors.append("'name' must be a non-empty string")
    if "desc" in data and (not isinstance(data["desc"], str)):
        errors.append("'desc' must be a string")
    if "icon" in data and (not isinstance(data["icon"], str) or not data["icon"].strip()):
        errors.append("'icon' must be a non-empty string")
    if "category" in data and (not isinstance(data["category"], str) or not data["category"].strip()):
        errors.append("'category' must be a non-empty string")
    if "date" in data:
        if not isinstance(data["date"], (str, int, float)):
            errors.append("'date' must be a date string or timestamp")
        elif isinstance(data["date"], str) and not data["date"].strip():
            errors.append("'date' must not be empty")

    # Validate items
    if "items" in data:
        if not isinstance(data["items"], list):
            errors.append("'items' must be an array")
        elif len(data["items"]) == 0:
            errors.append("'items' must not be empty")
        else:
            for i, item in enumerate(data["items"]):
                errors.extend(validate_item(item, i))

    return data, errors


def move_to_tmps(filepath):
    """Move a file to the tmps directory."""
    TMPS_DIR.mkdir(parents=True, exist_ok=True)
    dest = TMPS_DIR / filepath.name
    if dest == filepath:
        return
    shutil.move(str(filepath), str(dest))


def move_to_category(filepath, category):
    """Move a file to lists/<category>/ directory."""
    category_dir = LISTS_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    dest = category_dir / filepath.name
    if dest == filepath:
        return
    shutil.move(str(filepath), str(dest))


def collect_json_files():
    """Recursively collect all JSON files from lists/ and tmps/ (excluding _indexes.json)."""
    files = []
    for directory in [LISTS_DIR, TMPS_DIR]:
        if not directory.exists():
            continue
        for filepath in directory.rglob("*.json"):
            if filepath.name == CATEGORY_INDEX_NAME:
                continue
            files.append(filepath)
    return files


def _date_to_timestamp(date_str):
    """Convert YYYY-MM-DD date string to second-level timestamp. Returns 0 for invalid."""
    try:
        parts = date_str.split("-")
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=8))
        dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=tz)
        return int(dt.timestamp())
    except (IndexError, ValueError, TypeError):
        return 0


def _gen_uuid():
    """Generate a UUID using uuidgen command."""
    result = subprocess.run(["uuidgen"], capture_output=True, text=True)
    return result.stdout.strip()


def sort_dict_keys(data):
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


def sort_items(items):
    """对items数组进行排序，按name字段"""
    return sorted(items, key=lambda x: x.get('name', ''))


def format_list_data(data):
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
            from datetime import datetime
            dt = datetime.strptime(data['date'], '%Y-%m-%d')
            data['date'] = int(dt.timestamp())
        except ValueError:
            pass  # 保持原样
    
    # 排序items
    if 'items' in data and isinstance(data['items'], list):
        data['items'] = sort_items(data['items'])
    
    # 递归排序所有字典键
    return sort_dict_keys(data)


def update_list_file(filepath):
    """Update count, ensure id (UUID), convert date, and rename file to match id in a list JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Ensure id (UUID) exists
    if "id" not in data:
        data["id"] = _gen_uuid()
    
    # Rename file to match id if needed (this should always be done)
    expected_name = f"{data['id']}.json"
    if filepath.name != expected_name:
        new_path = filepath.parent / expected_name
        # Avoid overwriting existing files
        if new_path.exists() and new_path != filepath:
            # Generate a new UUID to avoid conflicts
            data["id"] = _gen_uuid()
            expected_name = f"{data['id']}.json"
            new_path = filepath.parent / expected_name
        
        filepath.rename(new_path)
        filepath = new_path
    
    data["count"] = len(data.get("items", []))
    # Convert date to second-level timestamp
    date_val = data.get("date", "")
    if isinstance(date_val, str) and date_val:
        data["date"] = _date_to_timestamp(date_val)
    elif isinstance(date_val, (int, float)) and date_val > 9999999999:
        # Was millisecond timestamp, convert to seconds
        data["date"] = int(date_val // 1000)
    
    # 格式化数据以确保一致性
    data = format_list_data(data)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def generate_category_index(category_dir):
    """Generate _indexes.json for a specific category directory."""
    category = category_dir.name
    items = []
    file_count = 0
    latest_date = 0

    for filepath in sorted(category_dir.glob("*.json")):
        if filepath.name.startswith("_"):
            continue
        file_count += 1
        try:
            # Update count and convert date in each list file
            filepath = update_list_file(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            date_val = data.get("date", 0)
            if isinstance(date_val, (int, float)) and date_val > latest_date:
                latest_date = int(date_val)
            items.append({
                "id": data["id"],
                "name": data["name"],
                "desc": data["desc"],
                "icon": data.get("icon", ""),
                "date": date_val,
                "count": data.get("count", 0),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    # Sort: newest date first, then by name alphabetically for same date
    items.sort(key=lambda x: (-x.get("date", 0), x.get("name", "")))

    # Read existing _indexes.json to preserve category metadata (name/icon/desc)
    cat_index_file = category_dir / CATEGORY_INDEX_NAME
    old_data = load_category_index(category_dir)
    cat_id = category  # Use folder name as id
    cat_name = old_data.get("name", "")
    cat_icon = old_data.get("icon", "")
    cat_desc = old_data.get("desc", "")

    index_data = {
        "id": cat_id,
        "name": cat_name,
        "icon": cat_icon,
        "desc": cat_desc,
        "count": file_count,
        "updateAt": latest_date,
        "items": items,
    }

    with open(cat_index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    return file_count




def generate_root_index(version=None):
    """Generate the root indexes.json purely from lists/*/_indexes.json."""
    categories = []
    warnings = []

    if not LISTS_DIR.exists():
        return warnings

    for category_dir in sorted(LISTS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue

        category = category_dir.name

        # Read category metadata solely from _indexes.json
        cat_data = load_category_index(category_dir)
        if not cat_data:
            continue

        cat_id = category  # Use folder name as id
        cat_name = cat_data.get("name", "")
        cat_icon = cat_data.get("icon", "")
        cat_desc = cat_data.get("desc", "")
        cat_count = cat_data.get("count", 0)

        if cat_count == 0:
            continue

        if not cat_name:
            warnings.append(f"Warning: category '{category}' missing 'name', please update lists/{category}/{CATEGORY_INDEX_NAME}")
        if not cat_icon:
            warnings.append(f"Warning: category '{category}' missing 'icon', please update lists/{category}/{CATEGORY_INDEX_NAME}")

        cat_update_at = cat_data.get("updateAt", 0)

        categories.append({
            "id": cat_id,
            "name": cat_name,
            "icon": cat_icon,
            "desc": cat_desc,
            "count": cat_count,
            "updateAt": cat_update_at,
        })

    # Sort by updateAt descending (newest first)
    categories.sort(key=lambda x: -x.get("updateAt", 0))

    root_data = {
        "updateAt": int(time.time()),
        "categories": categories,
    }
    if version is not None:
        root_data["version"] = version
    with open(ROOT_INDEX, "w", encoding="utf-8") as f:
        json.dump(root_data, f, ensure_ascii=False, indent=2)

    return warnings


def _read_release_version():
    """Read current release version from release/release.json."""
    if not RELEASE_META.exists():
        return 0

    try:
        with open(RELEASE_META, "r", encoding="utf-8") as f:
            data = json.load(f)
        version = data.get("version", 0)
        if isinstance(version, int) and version >= 0:
            return version
    except (json.JSONDecodeError, OSError):
        pass

    return 0


def generate_release_assets(version=None):
    """Create release zip and update release metadata."""
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(RELEASE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if ROOT_INDEX.exists():
            zf.write(ROOT_INDEX, arcname="indexes.json")

        if LISTS_DIR.exists():
            for filepath in sorted(LISTS_DIR.rglob("*")):
                if filepath.is_file():
                    if any(part.startswith(".") for part in filepath.relative_to(LISTS_DIR).parts):
                        continue
                    arcname = str(filepath.relative_to(LISTS_DIR))
                    zf.write(filepath, arcname=arcname)

    new_version = version if version is not None else (_read_release_version() + 1)
    release_data = {
        "version": new_version,
        "releaseDate": int(time.time()),
    }
    with open(RELEASE_META, "w", encoding="utf-8") as f:
        json.dump(release_data, f, ensure_ascii=False, indent=2)

    return new_version


def main():
    print("=" * 50)
    print("StellectList Deploy Script")
    print("=" * 50)

    # Ensure directories exist
    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    TMPS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all JSON files
    json_files = collect_json_files()

    if not json_files:
        print("\nNo JSON files found to process.")
    else:
        print(f"\nFound {len(json_files)} JSON file(s) to validate.\n")

    valid_count = 0
    invalid_count = 0

    for filepath in json_files:
        rel_path = filepath.relative_to(ROOT_DIR)
        data, errors = validate_json_file(filepath)

        if errors:
            invalid_count += 1
            print(f"FAIL: {rel_path}")
            for err in errors:
                print(f"  {err}")
            move_to_tmps(filepath)
        else:
            valid_count += 1
            category = data["category"]
            print(f"  OK: {rel_path} -> lists/{category}/")
            move_to_category(filepath, category)

    # Clean up empty directories in lists/
    if LISTS_DIR.exists():
        for d in list(LISTS_DIR.iterdir()):
            if d.is_dir() and not any(f for f in d.glob("*.json") if not f.name.startswith("_")):
                idx = d / CATEGORY_INDEX_NAME
                if idx.exists():
                    idx.unlink()
                if not any(d.iterdir()):
                    d.rmdir()

    # Generate category indexes
    print("\n" + "-" * 50)
    print("Generating indexes...")

    if LISTS_DIR.exists():
        for category_dir in sorted(LISTS_DIR.iterdir()):
            if not category_dir.is_dir():
                continue
            count = generate_category_index(category_dir)
            print(f"  Generated: lists/{category_dir.name}/{CATEGORY_INDEX_NAME} ({count} items)")

    # Generate root index
    release_version = _read_release_version() + 1
    warnings = generate_root_index(version=release_version)
    print(f"  Generated: indexes.json")

    # Generate release package and metadata
    release_version = generate_release_assets(version=release_version)
    print(f"  Generated: release/stellect_release.zip")
    print(f"  Updated: release/release.json (version={release_version})")

    # Print warnings
    if warnings:
        print("\n" + "-" * 50)
        for w in warnings:
            print(f"  {w}")

    # Summary
    print("\n" + "=" * 50)
    print(f"Summary: {valid_count} valid, {invalid_count} invalid")
    print("=" * 50)

    if invalid_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
