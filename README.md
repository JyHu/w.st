# StellectList

> 为 Stellect 目标追踪应用提供数据支持的清单生成和管理系统

## 📱 关于 Stellect

**Stellect** 是一款专为热爱生活的你设计的目标追踪应用。把想做的事，变成看得见的星迹。

### 核心功能
- **灵活的清单管理** - 创建个性化的目标清单，支持自定义颜色和图标
- **完成记录与回忆** - 添加照片、笔记和位置信息，保存独特足迹
- **地理位置标记** - 为目标标记地理坐标，支持多种地图应用打开
- **无缝 iCloud 同步** - 自动同步数据，安全备份，跨设备无缝访问
- **成就展示** - 荣誉殿堂展示已完成的所有目标，见证成长

### 应用场景
- 旅行探险：收集想去的地方，记录每一次登顶、景点打卡
- 美食探索：列出必吃餐厅，记录品尝过的美食
- 个人成长：规划学习目标、技能突破，见证进步
- 文娱体验：追剧、看展览、看电影，记录文化体验
- 健身挑战：制定运动目标，记录锻炼成果
- 人生清单：列出人生必做清单，用实际行动诠释梦想

---

## 🗂️ 项目简介

StellectList 是 Stellect 应用的数据内容生成和管理仓库，专门为目标追踪应用提供高质量的清单数据。

### 仓库结构
```
StellectList/
├── indexes.json              # 根索引（自动生成）
├── deploy.py                 # 校验 & 部署脚本
├── lists/                    # 正式清单目录
│   ├── city/                 # 城市清单
│   ├── book/                 # 阅读清单
│   ├── culture/             # 文化清单
│   ├── food/                # 美食清单
│   ├── hiking/              # 徒步清单
│   ├── life/                # 人生清单
│   ├── movie/               # 电影清单
│   ├── music/               # 音乐清单
│   ├── nature/              # 自然清单
│   ├── sport/               # 运动清单
│   └── travel/              # 旅行清单
└── tmps/                     # 待校验/校验失败的清单
```

### 现有分类
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

---

## 📋 数据格式

### 清单文件结构
每个清单都是一个 JSON 文件，结构如下：

```json
{
  "id": "cities_china",
  "name": "中国最美的50座城市",
  "desc": "总有一座城市让你念念不忘",
  "icon": "building.2.fill",
  "category": "city",
  "date": "2026-05-31",
  "items": [
    {
      "name": "杭州",
      "desc": "人间天堂，西湖美景",
      "latitude": 30.2741,
      "longitude": 120.1551,
      "address": "浙江省杭州市"
    }
  ]
}
```

### 顶层字段（全部必填）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 清单唯一标识，建议用英文小写+下划线 |
| name | string | 清单名称 |
| desc | string | 清单简短描述 |
| icon | string | SF Symbol 名称或 emoji 表情符号 |
| category | string | 所属分类 id |
| date | string/number | 创建日期，格式 YYYY-MM-DD 或秒级时间戳 |
| items | array | 清单条目，不能为空 |

### items 条目字段
| 字段 | 是否必填 | 类型 | 说明 |
|------|---------|------|------|
| name | 必填 | string | 条目名称 |
| desc | 可选（建议带上） | string | 条目描述 |
| latitude | 可选 | number | 纬度 |
| longitude | 可选 | number | 经度 |
| address | 可选 | string | 地址信息 |

### 自动生成字段
部署脚本会自动添加以下字段：
- `count` - items 条目数量
- `date` - 转换为秒级时间戳

---

## 🚀 发布方式

### 工作流程
1. **生成清单** → 放到 `tmps/` 目录下
2. **如果是新分类** → 在 `lists/` 下新建对应目录，并创建 `_indexes.json` 填写分类信息（name、icon、desc）
3. **运行部署** → 执行 `python3 deploy.py`，脚本会自动校验、归档、生成索引

> 根目录下的 `indexes.json` 完全由脚本从 `lists/*/_indexes.json` 自动生成，**不要手动编辑**。

### 部署脚本功能
- **自动校验** - 检查 JSON 格式和字段完整性
- **自动归档** - 将校验通过的文件移动到 `lists/<category>/`
- **错误处理** - 将校验失败的文件移动到 `tmps/`
- **索引生成** - 自动生成分类索引和根索引
- **版本管理** - 生成发布版本包

### 发布文件
部署完成后会生成：
- `release/stellect_release.zip` - 完整数据包
- `release/release.json` - 发布元数据（版本号、发布时间）

### 使用方法
```bash
# 1. 将新的清单文件放入 tmps/ 目录
# 2. 如有新分类，在 lists/ 下创建目录和 _indexes.json
# 3. 运行部署脚本
python3 deploy.py

# 4. 获取发布包
ls -la release/
```

### 命名规范
- 文件名：英文小写 + 下划线，如 `cities_china.json`、`food_100.json`
- **内容文件不允许以 `_` 开头**（`_` 前缀保留给系统索引文件）
- id 字段：与文件名一致（不含 .json 后缀）
- category：使用已有分类 id，新分类需在 `lists/` 下新建目录

### 注意事项
- icon 推荐使用 Apple SF Symbols（如 `building.2.fill`、`fork.knife`、`figure.hiking`），也可以直接用 emoji
- 每个清单的 items 数量建议 20-100 个
- 有地理位置属性的条目建议补全 latitude、longitude、address
- 生成清单时 date 填当天日期（YYYY-MM-DD 格式即可，脚本会自动转换）
- 所有时间戳均为秒级（10位数字）

---

## 📖 文档参考

### 主要文档
- **App Store 描述**：`/Users/hujinyou/Documents/Project/Owner/Stellect/docs/APP_STORE_DESCRIPTION.md`
- **项目总览**：`/Users/hujinyou/Documents/Project/Owner/Stellect/docs/PROJECT_OVERVIEW.md`
- **技术指南**：`AGENTS.md` - 详细的部署指南和数据格式说明

### 索引文件结构
部署脚本会自动生成两个索引文件：

#### 根索引 `indexes.json`
```json
{
  "updateAt": 1780215741,
  "categories": [
    {"id": "city", "name": "城市", "icon": "building.2.fill", "desc": "探索世界上最美的城市", "count": 2, "updateAt": 1780156800}
  ]
}
```

#### 分类索引 `_indexes.json`
```json
{
  "id": "city",
  "name": "城市",
  "icon": "building.2.fill",
  "desc": "探索世界上最美的城市",
  "count": 2,
  "updateAt": 1780156800,
  "items": [
    {"id": "cities_china", "name": "中国最美的50座城市", "desc": "总有一座城市让你念念不忘", "icon": "building.2.fill", "date": 1780156800, "count": 50}
  ]
}
```

---

## 🔗 相关链接

- **官网**：https://w.st/
- **App Store**：https://apps.apple.com/app/id6779149152
- **GitHub**：https://github.com/JyHu/Stellect

---

**最后更新**：2026 年 7 月 10 日