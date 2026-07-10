# StellectList 清单生成指南

> 📖 **快速入门**：查看 [README.md](README.md) 了解项目概览和基本信息

## 项目简介

**StellectList** 是为 Stellect 目标追踪应用提供数据支持的清单生成和管理系统。这个仓库专门为目标追踪应用提供高质量的清单数据，帮助用户记录、追踪和完成个人目标。

## 数据生成标准

### 核心原则
- **真实性优先**：所有数据必须基于公开可查证的事实，宁可减少数量，也不编造内容
- **质量导向**：注重数据准确性和实用性，确保每个条目都有实际参考价值
- **格式规范**：严格遵守JSON格式要求，确保数据可直接导入应用

### 主题分类规则
**地点类主题**（必须提供地理位置信息）：
- 城市、景点、公园、建筑、博物馆、餐厅、酒店、海滩、山脉、河流等

**非地点类主题**（禁止提供地理位置信息）：
- 技能学习、书籍、电影、音乐、人生目标、运动器材、文化概念等

### 数据质量要求
- **name字段**：简洁、唯一、不超过30字符，不添加编号，不包含Emoji
- **desc字段**：30～120字符，突出条目特色，避免模板化，不重复name
- **真实性**：使用真实信息，使用公开事实，每个条目互不重复
- **禁止**：生成占位内容、示例网址、编造事实
- **排序**：默认按知名度、代表性和推荐程度排序

### 关联项目
- **Stellect App**: https://github.com/JyHu/Stellect - iOS 目标管理应用
- **官网**: https://w.st/
- **App Store**: https://apps.apple.com/app/id6779149152

### 项目目标
- 为 Stellect 应用提供丰富多样的清单数据
- 建立标准化的清单数据格式和发布流程
- 支持多分类、多场景的目标管理需求
- 确保数据质量和版本管理

---

## 项目结构

```
StellectList/
├── indexes.json              # 根索引（自动生成，勿手动编辑）
├── scripts/                  # 脚本目录
│   ├── deploy.py            # 校验 & 部署脚本
│   ├── fix_dump.py          # 重复项处理脚本
│   └── lint.py              # 格式化 & 校验脚本
├── lists/                    # 正式清单目录
│   ├── city/
│   │   ├── _indexes.json     # 分类索引（自动生成，_ 前缀）
│   │   ├── 550E8400-E29B-41D4-A716-446655440000.json
│   │   └── 550E8400-E29B-41D4-A716-446655440001.json
│   ├── book/
│   ├── culture/
│   ├── food/
│   ├── hiking/
│   ├── life/
│   ├── movie/
│   ├── music/
│   ├── nature/
│   ├── sport/
│   └── travel/
└── tmps/                     # 待校验/校验失败的清单
```

## 现有分类

| id | name | icon | 清单数 |
|------|------|------|--------|
| book | 阅读 | book.fill | 2 |
| city | 城市 | building.2.fill | 2 |
| culture | 文化 | building.columns.fill | 2 |
| food | 美食 | fork.knife | 3 |
| hiking | 徒步 | figure.hiking | 3 |
| life | 人生 | heart.fill | 2 |
| movie | 电影 | film.fill | 2 |
| music | 音乐 | music.note | 2 |
| nature | 自然 | leaf.fill | 3 |
| sport | 运动 | sportscourt.fill | 1 |
| travel | 旅行 | airplane | 4 |

## 工作流程

1. **生成清单** → 放到 `tmps/` 目录下
2. **如果是新分类** → 在 `lists/` 下新建对应目录，并创建 `_indexes.json` 填写分类信息（name、icon、desc）
3. **运行部署** → 执行 `python3 scripts/deploy.py`，脚本会自动校验、归档、生成索引

> 根目录下的 `indexes.json` 完全由脚本从 `lists/*/_indexes.json` 自动生成，**不要手动编辑**。

## 清单文件结构

每个清单必须是一个 JSON 文件，结构如下：

```json
{
  "id": "550E8400-E29B-41D4-A716-446655440000",
  "name": "中国最美的50座城市",
  "desc": "总有一座城市让你念念不忘",
  "icon": "building.2.fill",
  "category": "city",
  "date": "2026-05-31",
  "items": [
    {"name": "杭州", "desc": "人间天堂，西湖美景", "latitude": 30.2741, "longitude": 120.1551, "address": "浙江省杭州市"},
    {"name": "苏州", "desc": "上有天堂下有苏杭", "latitude": 31.2990, "longitude": 120.5853, "address": "江苏省苏州市"}
  ]
}
```

> deploy 脚本会自动将 `date` 转为秒级时间戳，并添加 `count` 字段。

### 顶层字段（全部必填）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 清单唯一标识，使用随机UUID格式（如：550E8400-E29B-41D4-A716-446655440000），比如可以用 uuidgen |
| name | string | 清单名称 |
| desc | string | 清单简短描述（可为空字符串） |
| icon | string | SF Symbol 名称或 emoji 表情符号 |
| category | string | 所属分类 id |
| date | string/number | 创建日期，格式 YYYY-MM-DD 或秒级时间戳 |
| items | array | 清单条目，不能为空，默认生成50个目标，如果按照实际情况不足50条，那么有多少条就添加多少条 |

### 自动生成字段（deploy 脚本维护）

| 字段 | 类型 | 说明 |
|------|------|------|
| count | number | items 条目数量，由脚本自动写入 |
| date | number | 部署后会被转换为秒级时间戳 |

### items 条目字段

| 字段 | 是否必填 | 类型 | 说明 |
|------|---------|------|------|
| name | 必填 | string | 条目名称，简洁唯一，不超过30字符 |
| desc | 必填 | string | 条目描述，30～120字符，突出特色 |
| latitude | 条件可选 | number | 纬度，仅地点类主题提供 |
| longitude | 条件可选 | number | 经度，仅地点类主题提供 |
| address | 条件可选 | string | 地址信息，仅地点类主题提供 |

**地理位置信息使用规则**：
- 地点类主题：必须提供真实的latitude、longitude、address
- 非地点类主题：禁止提供latitude、longitude、address字段
- 判断标准：条目是否为具体物理地点

## 索引文件结构

### 根索引 indexes.json（自动生成）

```json
{
  "updateAt": 1780215741,
  "categories": [
    {"id": "city", "name": "城市", "icon": "building.2.fill", "desc": "探索世界上最美的城市", "count": 2, "updateAt": 1780156800}
  ]
}
```

- `updateAt`（根级）：脚本运行时的秒级时间戳
- `categories`：数组，按各分类的 `updateAt` 降序排列（最近更新的排前面）
- 每个分类的 `updateAt`：该分类下最新清单的 date

### 分类索引 _indexes.json（自动生成）

```json
{
  "id": "city",
  "name": "城市",
  "icon": "building.2.fill",
  "desc": "探索世界上最美的城市",
  "count": 2,
  "updateAt": 1780156800,
  "items": [
    {"id": "550E8400-E29B-41D4-A716-446655440000", "name": "中国最美的50座城市", "desc": "总有一座城市让你念念不忘", "icon": "building.2.fill", "date": 1780156800, "count": 50}
  ]
}
```

- `count`：该分类下清单文件数量
- `updateAt`：该分类下最新清单的 date 时间戳
- `items`：按 date 降序排列，同日期按名称字母序
- `name`、`icon`、`desc` 需在新建分类时手动填写，脚本会保留

## 命名规范

- 文件名：使用随机UUID格式，如 `550E8400-E29B-41D4-A716-446655440000.json`
- **内容文件不允许以 `_` 开头**（`_` 前缀保留给系统索引文件如 `_indexes.json`）
- id 字段：与文件名一致（不含 .json 后缀）
- category：使用已有分类 id，新分类需在 `lists/` 下新建目录并创建 `_indexes.json`

## deploy.py 校验规则

- 递归扫描 `lists/` 和 `tmps/` 下所有 JSON 文件（跳过 `_` 前缀的索引文件）
- 内容文件名不允许以 `_` 开头（否则校验失败）
- 校验通过 → 移动到 `lists/<category>/`
- 校验失败 → 移动到 `tmps/`，输出具体错误原因
- 校验完成后：
  - 每个清单文件写入 `count`，`date` 转为秒级时间戳
  - 生成每个分类的 `_indexes.json`（含 `updateAt`）
  - 生成根 `indexes.json`（按 `updateAt` 排序）

## 注意事项

- icon 推荐使用 Apple SF Symbols（如 `building.2.fill`、`fork.knife`、`figure.hiking`），也可以直接用 emoji
- 每个清单的 items 数量建议 20-100 个
- **地理位置信息规则**：
  - 仅适用于地点类主题（城市、景点、公园、建筑、博物馆、餐厅等）
  - 非地点类主题（如技能、书籍、电影、人生目标等）**禁止**添加 latitude、longitude、address 字段
  - 地点类条目必须提供真实、公开、可信的地理位置信息
- 生成清单时 date 填当天日期（YYYY-MM-DD 格式即可，脚本会自动转换）
- 所有时间戳均为秒级（10位数字）
- **格式化标准**：所有脚本统一使用 2空格缩进、字段按字母顺序排序、items数组按name排序

## 脚本使用指南

### deploy.py - 部署脚本
```bash
# 基本部署 - 校验、归档、生成索引
python3 scripts/deploy.py

# 功能说明：
# - 自动校验 JSON 格式和字段完整性
# - 将校验通过的文件移动到 lists/<category>/
# - 将校验失败的文件移动到 tmps/
# - 自动生成分类索引和根索引
# - 生成发布版本包
# - 统一格式化：2空格缩进、字段排序、items排序
```

### lint.py - 格式化 & 校验脚本
```bash
# 默认模式：格式化 + 校验
python3 scripts/lint.py

# 只格式化，不校验
python3 scripts/lint.py --format-only

# 只校验，不格式化
python3 scripts/lint.py --check-only

# 功能说明：
# - 格式化：2空格缩进、字段按字母顺序排序、items数组按name排序
# - 校验：JSON格式、字段完整性、数据质量
```

### fix_dump.py - 重复项处理脚本
```bash
# 处理所有清单文件的重复项（优先保留lists目录下的）
python3 scripts/fix_dump.py -all

# 处理单个清单文件的重复项
python3 scripts/fix_dump.py lists/movie/xxx.json

# 功能说明：
# - 识别并处理跨文件重复项
# - -all参数：优先保留lists目录下的重复项，删除tmps目录下的
# - 单文件模式：处理指定文件内的重复项
```

## 数据生成规则

### 优先级原则
**真实性 > 数据质量 > JSON 合法性 > 数量**
宁可减少数量，也不要编造数据。所有内容必须真实、准确、具有参考价值。

### 地理位置信息约束
- **必须提供地理位置的主题**：城市、景点、公园、建筑、博物馆、餐厅、酒店、海滩、山脉、河流等
- **禁止提供地理位置的主题**：技能学习、书籍、电影、音乐、人生目标、运动器材、文化概念等
- **判断标准**：如果条目是一个具体的物理地点，才考虑提供地理位置信息

### 数据质量要求
- **name**：简洁、唯一、不超过30个字符，不添加编号，不包含Emoji
- **desc**：30～120个字符，突出条目特色，避免模板化，不重复name
- **真实性**：使用真实信息，使用公开事实，每个条目互不重复
- **禁止**：生成占位内容、示例网址、编造事实
- **排序**：默认按知名度、代表性和推荐程度排序

---

## 贡献指南

### 如何贡献清单数据

1. **创建清单文件**
   - 将清单文件放在 `tmps/` 目录下
   - 确保文件符合 JSON 格式和字段要求

2. **新分类处理**
   - 如果创建新分类，在 `lists/` 下创建对应目录
   - 创建 `_indexes.json` 文件，填写分类信息：
   ```json
   {
     "id": "new_category",
     "name": "新分类名称",
     "icon": "icon.symbol",
     "desc": "分类描述"
   }
   ```

3. **运行部署脚本**
   ```bash
   python3 deploy.py
   ```

4. **提交更改**
   - 将 `lists/` 目录下的新文件添加到 git
   - 提交更改并创建 PR

### 质量要求

- **数据准确性**：确保清单内容的准确性和时效性，所有信息必须可验证
- **描述完整性**：每个条目必须添加有意义的描述，突出条目特色
- **地理位置**：严格按照地理位置信息规则执行，非地点类主题禁止提供
- **分类合理**：确保清单分类清晰，避免重复和交叉
- **内容唯一性**：每个条目名称必须唯一，避免重复
- **语言一致性**：所有字段必须使用统一语言，专有名词优先使用目标语言中的通用名称

### 数据验证标准

每个清单条目必须通过以下验证：
1. **真实性验证**：所有内容必须基于公开可查证的事实
2. **格式验证**：JSON格式必须符合RFC 8259标准
3. **字段验证**：必填字段完整，可选字段按需添加
4. **内容验证**：无重复、无占位、无编造内容
5. **地理验证**：地理位置信息仅适用于地点类主题

### 开发环境设置

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt  # 如果有依赖文件

# 运行部署脚本
python3 deploy.py
```

---

## 发布管理

### 版本控制
- 每次部署脚本运行都会生成新的版本
- 版本号存储在 `release/release.json` 中
- 发布包 `stellect_release.zip` 包含所有清单数据

### 数据更新流程
1. 开发者在 `tmps/` 目录添加新的清单文件
2. 运行 `python3 deploy.py` 进行校验和部署
3. 系统自动更新索引文件和版本信息
4. 生成新的发布包供 Stellect 应用使用

### 问题排查
- 如果部署失败，检查 `tmps/` 目录下的错误信息
- 确保 JSON 格式正确，所有必填字段完整
- 检查文件名是否符合命名规范
- **地理位置信息错误**：非地点类主题不应包含 latitude、longitude、address 字段
- **数据真实性检查**：确保所有条目都是真实存在的，不编造内容
- **内容重复检查**：确保每个条目的 name 和 desc 都是唯一的

---

**最后更新**：2026 年 7 月 11 日
