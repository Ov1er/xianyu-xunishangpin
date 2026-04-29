# 合法数据聚合系统 - 设计规格书

**项目**: 闲鱼虚拟产品工作流系统 - Phase 8 (合规版)  
**版本**: v3.0 (Legal Compliant)  
**日期**: 2026-04-27  
**状态**: ✅ 已批准  

---

## 1. 项目概述

### 1.1 目标
通过**合法合规的官方API和公开数据源**，为工作流系统获取真实存在的数据，包括：
- 📚 考研资料：真实的图书/出版物信息（ISBN、标题、作者、出版社）
- 🎓 教育产品：真实的课程/培训/学习资源信息
- 🎨 办公模板：开源的设计模板资源链接
- 📖 英语资源：公开的学习材料和电子书信息

### 1.2 核心原则
- ✅ **100%合法合规** - 仅使用官方API和公开数据
- ✅ **尊重知识产权** - 只收集元数据，不复制受版权保护内容
- ✅ **商业可用** - 所有数据可用于商业用途
- ✅ **可追溯验证** - 每条数据包含来源URL和采集时间
- ✅ **可持续更新** - 建立定期更新机制

### 1.3 排除项（明确禁止）
- ❌ 不使用任何绕过反爬机制的技术
- ❌ 不访问robots.txt明确禁止的网站
- ❌ 不采集个人信息或隐私数据
- ❌ 不复制受版权保护的正文/图片/文件内容
- ❌ 不违反任何网站的使用条款(ToS)

---

## 2. 数据源详细清单

### 2.1 考研资料（目标：500-800条）

#### 主要API：

**Google Books API**
- **端点**: `https://www.googleapis.com/books/v1/volumes`
- **免费额度**: 1000次/天（无需API Key即可使用）
- **商用许可**: ✅ 允许商业用途
- **数据字段**: 
  ```json
  {
    "id": "ISBN/ID",
    "volumeInfo": {
      "title": "书籍标题",
      "authors": ["作者列表"],
      "publisher": "出版社",
      "publishedDate": "出版日期",
      "description": "内容简介",
      "industryIdentifiers": [{"type": "ISBN_13", "identifier": "..."}],
      "pageCount": 300,
      "categories": ["考试/教育"],
      "imageLinks": {"thumbnail": "封面缩略图URL"},
      "language": "zh-CN",
      "infoLink": "Google Books详情页"
    }
  }
  ```
- **搜索参数**: `q=考研+数学+真题` 或 `q=考研政治+大纲`
- **Rate Limit**: 遵循Google API政策（建议间隔100ms+）

**Open Library API**
- **端点**: `https://openlibrary.org/api/books`
- **免费额度**: 无限制（但需控制频率）
- **商用许可**: ✅ 公共领域数据（CC0）
- **用途**: 补充Google Books未覆盖的数据

**教育部官网公开数据**
- **网址**: `https://www.moe.gov.cn/`
- **类型**: 政府公开信息（考研政策、招生简章）
- **获取方式**: 直接访问公开页面（非爬虫）
- **数据内容**: 考试科目设置、报名时间、分数线等

#### 数据映射规则：
```python
# Google Books → 系统数据模型
{
    'id': f"GB_{google_books_id}",
    'title': volumeInfo['title'],
    'subject': infer_subject(title, categories),
    'year': extract_year(publishedDate),
    'material_type': infer_type(title, description),
    'description': description[:200],
    'source_url': infoLink,
    'download_url': infoLink,  # 引导到购买页
    'file_format': 'PDF',  # 图书通常是PDF
    'tags': [subject, year_str, material_type],
    'source': 'Google Books API',
    'isbn': isbn_13,
    'publisher': publisher,
    'authors': authors,
    'price': None  # 可后续从电商API补充
}
```

---

### 2.2 英语学习资源（目标：300-500条）

#### 主要API：

**Project Gutenberg API**
- **端点**: `https://gutenberg.org/cache/epub/`
- **免费额度**: 无限制
- **商用许可**: ✅ 公共领域（Public Domain）
- **数据内容**: 免费英语电子书（经典文学、教材等）
- **适用场景**: 英语阅读材料、经典著作

**Wikipedia API**
- **端点**: `https://en.wikipedia.org/w/api.php`
- **免费额度**: 需遵守Bot Policy
- **商用许可**: ⚠️ CC BY-SA 4.0（需标注来源）
- **数据内容**: 学习方法词条、语法讲解、考试指南
- **适用场景**: 英语学习方法论、备考策略

**TED Talks API**
- **端点**: `https://ted.com/talks?language=zh-cn` (RSS)
- **免费额度**: 开放访问
- **商用许可**: ✅ CC BY-NC-ND 4.0（⚠️ 仅限个人/教育用途）
- **替代方案**: 仅收集标题和链接，不嵌入视频

**BBC Learning English**
- **网址**: `https://www.bbc.co.uk/learningenglish`
- **类型**: 公开课程页面
- **获取方式**: 收集公开的课程名称和简介
- **商用限制**: ⚠️ 个人学习用途（不可转售内容）

#### 数据映射示例：
```python
# Project Gutenberg → 英语资源模型
{
    'id': f"PG_{book_id}",
    'title': title,
    'category_id': 'reading',
    'category_name': '阅读训练',
    'author': author,
    'content_summary': summary[:200],
    'url': f"https://www.gutenberg.org/ebooks/{book_id}",
    'tags': ['英语阅读', '公共领域', difficulty_level],
    'likes': download_count,  # 用下载量代替点赞数
    'difficulty': infer_difficulty(word_count),
    'priority': calculate_priority(download_count),
    'source': 'Project Gutenberg',
    'license': 'Public Domain',
    'language': language
}
```

---

### 2.3 办公模板资源（目标：200-400个）

#### 主要数据源：

**GitHub API（搜索开源模板）**
- **端点**: `https://api.github.com/search/repositories`
- **搜索查询**: 
  - LaTeX模板: `q=latex+template+resume`
  - PPT模板: `q=powerpoint+template+business`
  - Word模板: `q=word+template+report`
- **免费额度**: 60次/小时（认证后5000次/小时）
- **商用许可**: ✅ MIT/Apache等开源许可允许商
- **数据字段**:
  ```json
  {
    "full_name": "username/repo-name",
    "html_url": "https://github.com/...",
    "description": "模板描述",
    "stargazers_count": 1234,
    "forks_count": 567,
    "language": "TeX",
    "license": {"spdx_id": "MIT"},
    "updated_at": "2026-01-15",
    "topics": ["resume", "cv", "latex"]
  }
  ```

**Overleaf Gallery**
- **网址**: `https://www.overleaf.com/gallery/tagged/`
- **类型**: 公开展示页面
- **获取方式**: 访问公开的标签页
- **商用许可**: ✅ 大部分是LaTeX模板，可自由使用
- **数据内容**: 学术论文模板、简历模板、演示文稿模板

**Google Slides模板库**
- **网址**: `https://docs.google.com/presentation/u/0/`
- **类型**: 官方模板库
- **获取方式**: 手动收集热门模板信息
- **商用许可**: ✅ Google官方提供

#### 数据映射示例：
```python
# GitHub Repo → 办公模板模型
{
    'id': f"GH_{repo_id}",
    'title': name.replace('-', ' ').title(),
    'category': infer_category(language, topics),
    'subcategory': infer_subcategory(topics),
    'description': description[:150],
    'preview_url': '',  # GitHub无直接预览图
    'template_url': html_url,
    'difficulty': infer_difficulty(stargazers_count),
    'tags': topics + [category, license_type],
    'usage_count': stargazers_count,
    'rating': normalize_rating(stargazers_count, forks_count),
    'source': 'GitHub',
    'license': spdx_id,  # 重要！记录许可证
    'last_updated': updated_at
}
```

---

## 3. 技术架构

### 3.1 新增模块结构

```
data_collectors/           # 替代原crawlers/（强调合法性）
├── __init__.py
├── base_collector.py     # 基础数据收集器（非爬虫）
├── google_books.py       # Google Books API客户端
├── open_library.py      # Open Library API客户端
├── github_api.py         # GitHub API客户端
├── project_gutenberg.py  # Project Gutenberg客户端
├── wikipedia_api.py      # Wikipedia API客户端
└── pipelines.py          # 复用现有管道（已保留）
```

### 3.2 BaseCollector 基类设计

```python
class BaseCollector:
    """
    合法数据收集器基类
    
    与原BaseCrawler的区别：
    - 不包含反爬对抗逻辑
    - 强调API Rate Limit遵守
    - 明确记录数据来源和许可信息
    """
    
    NAME: str = ""
    DATA_TYPE: str = ""
    
    # API配置
    RATE_LIMIT: int = 10  # 每秒请求数
    DAILY_QUOTA: int = 1000  # 每日配额
    COMMERCIAL_USE: bool = True  # 是否允许商用
    
    def __init__(self):
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(min_delay=0.1, max_delay=0.5)
        self.request_count = 0
        self.last_request_time = None
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'rate_limited': 0,
            'errors': 0,
            'items_collected': 0
        }
    
    def request(self, url: str, params=None) -> dict:
        """
        合法API请求
        
        关键特性：
        1. 严格遵守Rate Limit
        2. 正确处理429 Too Many Requests
        3. 记录请求统计用于监控配额
        4. 自动添加User-Agent标识
        """
        # 检查是否超出速率限制
        self._check_rate_limit()
        
        # 发送请求
        response = self.session.get(url, params=params, timeout=30)
        self.request_count += 1
        self.stats['total_requests'] += 1
        
        if response.status_code == 200:
            self.stats['successful'] += 1
            return response.json()
            
        elif response.status_code == 429:
            self.stats['rate_limited'] += 1
            logger.warning(f"[{self.NAME}] 触发速率限制，等待...")
            time.sleep(60)  # 等待1分钟
            return self.request(url, params)
            
        else:
            self.stats['errors'] += 1
            raise APIError(f"API错误 {response.status_code}")
    
    def _check_rate_limit(self):
        """确保不超过速率限制"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            min_interval = 1.0 / self.RATE_LIMIT
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
        self.last_request_time = time.time()
```

### 3.3 数据处理流程

```
API原始数据 → 字段标准化 → 去重 → 许可证检查 → 质量验证 → 存储
     │             │          │           │           │         │
     ▼             ▼          ▼           ▼           ▼         ▼
  JSON响应   统一字段格式  URL去重   过滤非商用  必填项检查  JSON文件
```

---

## 4. 合规性保障清单

### 4.1 使用前检查清单

- [ ] 已阅读并理解每个API的Terms of Service
- [ ] 确认数据可用于Commercial Use
- [ ] 设置合理的Request Interval（≥100ms）
- [ ] 监控API调用次数，不超出Daily Quota
- [ ] 在代码中添加Source Attribution注释
- [ ] 不缓存/存储受版权保护的完整内容

### 4.2 数据输出规范

每条数据必须包含以下元数据字段：

```python
{
    # ... 业务字段 ...
    
    # 合规性元数据（必须包含）
    '_meta': {
        'source': 'Google Books API',        # 数据来源
        'source_url': 'https://...',          # 原始链接
        'collected_at': '2026-04-27T...',     # 采集时间
        'license': 'CC-BY' or 'Public Domain',  # 许可证类型
        'commercial_use_allowed': True,       # 是否可商用
        'last_verified': '2026-04-27',         # 最后验证日期
        'api_version': 'v1',                  # API版本
    }
}
```

### 4.3 禁止行为清单

❌ **绝对禁止：**
- 使用多个账号/API Key绕过配额限制
- 伪造User-Agent冒充浏览器或搜索引擎
- 批量导出API完整数据库供离线使用
- 将API数据重新包装为竞争性产品
- 采集用户生成的内容（评论、评分等个人数据）

⚠️ **需要谨慎：**
- 缓存API响应超过24小时
- 对同一数据进行二次加工后销售
- 高频自动化请求（>1次/秒）

✅ **推荐做法：**
- 实时或准实时调用API
- 提供原始来源链接（引流）
- 标注数据来源和许可证
- 实现透明的数据溯源

---

## 5. 实施计划概要

### Phase 8A: API集成开发（Day 1-2）

**Day 1:**
- [ ] 实现 BaseCollector 基类
- [ ] 集成 Google Books API（考研图书）
- [ ] 集成 Open Library API
- [ ] 单元测试 + 数据验证

**Day 2:**
- [ ] 集成 GitHub API（办公模板）
- [ ] 集成 Project Gutenberg（英语资源）
- [ ] 数据聚合与去重
- [ ] 全量集成测试

### Phase 8B: 数据扩充（Day 3）
- [ ] 从教育部官网补充考研政策数据
- [ ] 从高校官网补充招生信息
- [ ] 人工审核与质量检查
- [ ] 性能优化与错误处理

### Phase 8C: 上线准备
- [ ] 文档编写（API使用说明）
- [ ] 监控告警（配额使用率）
- [ ] 定时任务配置（每周更新）
- [ ] 用户界面展示优化

---

## 6. 成功标准

| 指标 | 目标值 | 验证方式 |
|------|--------|---------|
| 数据真实性 | 100% | 每条数据含可访问的source_url |
| 法律合规性 | 0风险 | 通过合规审计 |
| 考研资料数量 | ≥500条 | 统计kaoyan_data.json |
| 英语资源数量 | ≥300条 | 统计english_data.json |
| 办公模板数量 | ≥200条 | 统计office_data.json |
| API配额使用 | <80% | 日志监控 |
| 数据更新周期 | ≤7天 | 定时任务记录 |

---

## 7. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| API服务变更 | 中 | 高 | 版本锁定 + 多源备份 |
| 配额不足 | 低 | 中 | 优化查询 + 分批执行 |
| 数据质量不一 | 中 | 中 | 多源交叉验证 + 人工审核 |
| 许可证变更 | 低 | 高 | 定期审查 + 及时调整 |

---

## 8. 参考资源

### API文档
- Google Books API: https://developers.google.com/books
- Open Library: https://openlibrary.org/developers/api
- GitHub API: https://docs.github.com/en/rest
- Wikipedia API: https://www.mediawiki.org/wiki/API:Main_page

### 法律参考
- 《网络安全法》: http://www.npc.gov.cn
- 《数据安全法》: http://www.npc.gov.cn
- CC许可证: https://creativecommons.org/licenses/
- Google ToS: https://policies.google.com/terms

---

**文档版本**: v3.0  
**最后更新**: 2026-04-27  
**审批状态**: ✅ 用户已批准  
**下一步**: 编写实施计划 (writing-plans)
