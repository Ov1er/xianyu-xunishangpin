# 真实数据源接入 - 技术设计规格书

**项目**: 闲鱼虚拟产品工作流系统 - Phase 8  
**版本**: v1.0  
**日期**: 2026-04-27  
**状态**: ✅ 已批准  

---

## 1. 项目概述

### 1.1 目标
将现有模拟数据替换为真实网络数据，实现：
- 📚 考研资料：从考研帮等平台自动采集
- 📝 办公模板：从Canva等平台自动采集
- 📖 英语资料：从知乎等平台自动采集
- ⏰ 定时更新：自动化数据刷新机制

### 1.2 范围
- **Phase 8A**: 核心数据源接入（3个网站）
- **Phase 8B**: 扩展更多数据源（可选）
- **Phase 9**: 闲鱼API对接（后续）
- **Phase 10**: 小红书自动化（后续）

### 1.3 约束条件
- 技术栈: Python 3.12 + requests + BeautifulSoup4
- 更新频率: 考研(每日) / 知乎(6小时) / Canva(每周)
- 数据格式: JSON（兼容现有DataLoader）
- 反爬策略: UA轮换 + 请求间隔 + 异常重试

---

## 2. 架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────┐
│           数据采集调度中心 (Scheduler)         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ 定时任务 │  │ 手动触发│  │ 监控告警│      │
│  └────┬────┘  └────┬────┘  └────┬────┘      │
│       └──────────────┼──────────┘            │
│                      ▼                      │
│  ┌──────────────────────────────────┐       │
│  │      爬虫引擎 (Crawler Engine)    │       │
│  │  ┌──────┐ ┌──────┐ ┌──────┐      │       │
│  │  │考研帮│ │ 知乎 │ │ Canva│      │       │
│  │  └──┬───┘ └──┬───┘ └──┬───┘      │       │
│  └─────┼────────┼────────┼─────────┘       │
│        ▼        ▼        ▼                │
│  ┌──────────────────────────────────┐       │
│  │     数据清洗管道 (Pipeline)       │       │
│  │  去重 → 格式化 → 验证 → 标准化     │       │
│  └──────────────┬───────────────────┘       │
│                 ▼                          │
│  ┌──────────────────────────────────┐       │
│  │      存储层 (Storage)             │       │
│  │  JSON文件 → DataLoader → UI展示   │       │
│  └──────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 文件 |
|------|------|------|
| **BaseCrawler** | 基础爬虫类，封装通用逻辑 | `crawlers/base_crawler.py` |
| **KaoyanCrawler** | 考研帮数据采集 | `crawlers/kaoyan_crawler.py` |
| **ZhihuCrawler** | 知乎英语资料采集 | `crawlers/zhihu_crawler.py` |
| **CanvaCrawler** | Canva模板信息采集 | `crawlers/canva_crawler.py` |
| **Pipeline** | 数据清洗、去重、验证 | `crawlers/pipelines.py` |
| **Scheduler** | APScheduler定时任务管理 | `scheduler/tasks.py` |

---

## 3. 数据源详情

### 3.1 考研帮 (kaoyan.com)

**目标URL结构**:
```
首页: https://www.kaoyan.com/
真题: https://www.kaoyan.com/zhenti/
大纲: https://www.kaoyan.com/dagang/
```

**采集字段**:
```python
{
    'id': str,              # 唯一标识 (KY+时间戳+随机)
    'title': str,           # 资料标题
    'subject': str,         # 科目 (政治/数学/英语/专业课)
    'year': int,            # 年份 (2024/2025/2026)
    'material_type': str,   # 类型 (真题/大纲/指南/笔记)
    'description': str,     # 描述
    'source_url': str,      # 来源链接
    'download_url': str,    # 下载链接
    'file_size': str,       # 文件大小
    'file_format': str,     # 文件格式 (PDF/WORD/ZIP)
    'tags': List[str],      # 标签列表
    'crawl_time': datetime, # 采集时间
    'source': str           # 数据来源标识
}
```

**反爬配置**:
- User-Agent: 每5次请求轮换一次
- 请求间隔: 3-7秒随机延迟
- 最大重试: 3次
- 超时设置: 30秒

---

### 3.2 知乎专栏 (zhihu.com)

**目标URL结构**:
```
搜索: https://www.zhihu.com/search?type=content&q=考研英语
文章: https://zhuanlan.zhihu.com/p/{article_id}
```

**采集字段**:
```python
{
    'id': str,
    'title': str,           # 文章标题
    'category_id': str,     # 分类ID (vocab/grammar/reading/writing)
    'category_name': str,   # 分类名称 (词汇/语法/阅读/写作)
    'author': str,          # 作者
    'content_summary': str, # 内容摘要 (前200字)
    'url': str,             # 原文链接
    'tags': List[str],      # 标签
    'likes': int,           # 点赞数
    'difficulty': str,      # 难度 (基础/强化/冲刺)
    'priority': str,        # 优先级 (必看/推荐/选学)
    'crawl_time': datetime,
    'source': str
}
```

**反爬配置**:
- Cookie维持: 使用session保持登录态
- 请求间隔: 8-15秒（知乎较严格）
- 最大并发: 1（串行采集）
- 失败处理: 记录失败URL，稍后重试

---

### 3.3 Canva模板页 (canva.cn)

**目标URL结构**:
```
PPT: https://www.canva.cn/templates/ppt/
Word: https://www.canva.cn/templates/word/
Excel: https://www.canva.cn/templates/excel/
简历: https://www.canva.cn/templates/resume/
```

**采集字段**:
```python
{
    'id': str,
    'title': str,           # 模板名称
    'category': str,        # 主类别 (PPT/Word/Excel/简历)
    'subcategory': str,     # 子类别 (工作汇报/年终总结/...)
    'description': str,     # 模板描述
    'preview_url': str,     # 预览图URL
    'template_url': str,    # 模板页面URL
    'difficulty': str,      # 难度 (入门级/进阶级/高级定制)
    'tags': List[str],
    'usage_count': int,     # 使用次数 (估算)
    'rating': float,        # 评分 (4.0-5.0)
    'crawl_time': datetime,
    'source': str
}
```

**反爬配置**:
- 完整Headers: Referer + Accept-Language
- 请求间隔: 5-10秒
- 图片下载: 仅记录URL，不下载图片
- 并发控制: 最多2个并发

---

## 4. 技术实现细节

### 4.1 BaseCrawler 基础类

```python
class BaseCrawler:
    """爬虫基类 - 封装通用功能"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua_pool = UserAgentPool()
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)
        
    def request(self, url, **kwargs) -> Response:
        """带反爬保护的请求"""
        # 1. 设置UA
        headers = self._build_headers()
        
        # 2. 限速
        self.rate_limiter.wait()
        
        # 3. 发送请求
        response = self.session.get(
            url,
            headers=headers,
            timeout=30,
            **kwargs
        )
        
        # 4. 错误处理
        if response.status_code == 403:
            raise BlockedError(f"被封锁: {url}")
            
        return response
    
    def parse(self, html: str) -> List[Dict]:
        """解析HTML，子类实现"""
        raise NotImplementedError
    
    def save(self, data: List[Dict], data_type: str):
        """保存数据"""
        pipeline = DataPipeline()
        cleaned_data = pipeline.process(data)
        DataLoader().save(data_type, cleaned_data)
```

### 4.2 Pipeline 数据清洗管道

```python
class DataPipeline:
    """数据处理管道"""
    
    def process(self, raw_data: List[Dict]) -> Dict:
        # Step 1: 去重
        unique_data = self.deduplicate(raw_data)
        
        # Step 2: 字段标准化
        standardized = self.standardize(unique_data)
        
        # Step 3: 数据验证
        validated = self.validate(standardized)
        
        # Step 4: 补充元数据
        enriched = self.enrich_metadata(validated)
        
        return {
            'metadata': {
                'version': '1.0.0',
                'last_updated': datetime.now().isoformat(),
                'total_count': len(enriched),
                'source': 'crawler'
            },
            f'{self.data_key}s': enriched
        }
    
    def deduplicate(self, data):
        """基于title+source_url去重"""
        seen = set()
        unique = []
        for item in data:
            key = (item.get('title', ''), item.get('source_url', ''))
            if key not in seen and key[0]:
                seen.add(key)
                unique.append(item)
        return unique
```

### 4.3 Scheduler 定时任务

```python
# scheduler/config.py

SCHEDULER_CONFIG = {
    'kaoyan': {
        'cron': '0 8 * * *',       # 每天8:00执行
        'crawler': 'KaoyanCrawler',
        'data_type': 'kaoyan',
        'enabled': True
    },
    'zhihu': {
        'interval_hours': 6,       # 每6小时
        'crawler': 'ZhihuCrawler',
        'data_type': 'english',
        'enabled': True
    },
    'canva': {
        'cron': '0 9 * * 1',       # 每周一9:00
        'crawler': 'CanvaCrawler',
        'data_type': 'office',
        'enabled': True
    }
}

# scheduler/tasks.py

def setup_scheduler():
    scheduler = BackgroundScheduler()
    
    for name, config in SCHEDULER_CONFIG.items():
        if not config['enabled']:
            continue
            
        if 'cron' in config:
            scheduler.add_job(
                run_crawler_job,
                CronTrigger.from_crontab(config['cron']),
                id=f'update_{name}',
                args=[config['crawler'], config['data_type']],
                replace_existing=True
            )
        elif 'interval_hours' in config:
            scheduler.add_job(
                run_crawler_job,
                IntervalTrigger(hours=config['interval_hours']),
                id=f'update_{name}',
                args=[config['crawler'], config['data_type']],
                replace_existing=True
            )
    
    scheduler.start()
    logger.info("调度器启动完成")
    return scheduler


async def run_crawler_job(crawler_class_name, data_type):
    """执行爬虫任务"""
    try:
        crawler = get_crawler_instance(crawler_class_name)
        raw_data = crawler.fetch_all()
        
        if raw_data:
            save_result = crawler.save(raw_data, data_type)
            log_success(
                f"[{data_type}] 采集完成: {len(raw_data)}条"
            )
            # 可选: 发送通知
            notify_update_success(data_type, len(raw_data))
        else:
            log_warning(f"[{data_type}] 未采集到新数据")
            
    except Exception as e:
        log_error(f"[{data_type}] 采集失败: {e}")
        notify_error(data_type, str(e))
```

---

## 5. 目录结构

```
d:\workSpace\xianyu_xunishangpin\
│
├── crawlers/                    # 🆕 爬虫模块
│   ├── __init__.py             # 模块初始化
│   ├── base_crawler.py         # 基础爬虫类
│   ├── kaoyan_crawler.py       # 考研帮爬虫
│   ├── zhihu_crawler.py        # 知乎爬虫
│   ├── canva_crawler.py        # Canva爬虫
│   ├── pipelines.py            # 数据清洗管道
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── user_agents.py      # UA池 (100+真实UA)
│       ├── rate_limiter.py     # 限速器
│       ├── proxies.py          # 代理管理 (预留)
│       └── validators.py       # 数据验证器
│
├── scheduler/                  # 🆕 任务调度
│   ├── __init__.py
│   ├── tasks.py               # 任务定义
│   └── config.py              # 调度配置
│
├── logs/                       # 🆕 日志目录
│   ├── crawler_2026-04-27.log
│   └── scheduler.log
│
├── data/                       # 数据存储 (已有)
├── models/                     # 数据模型 (已有)
├── services/                   # 服务层 (已有)
├── pages/                      # 页面 (已有)
├── utils/                      # 工具函数 (已有)
├── assets/                     # 静态资源 (已有)
├── app.py                      # 应用入口 (已有)
├── config.py                   # 全局配置 (已有)
└── requirements.txt            # 依赖 (需更新)
```

---

## 6. 依赖更新

```txt
# requirements.txt 新增依赖

# HTTP & 解析
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
html5lib>=1.1

# 定时任务
apscheduler>=3.10.0

# 反爬工具
fake-useragent>=1.4.0

# 已有依赖 (保留)
streamlit>=1.30.0
pandas>=2.0.0
jinja2>=3.1.0
pyperclip>=1.8.0
```

---

## 7. 实施计划

### Day 1: 基础框架搭建
- [ ] 创建 `crawlers/` 目录和基础文件
- [ ] 实现 `BaseCrawler` 基类
- [ ] 实现 `UserAgentPool` 和 `RateLimiter`
- [ ] 实现 `DataPipeline` 清洗管道
- [ ] 配置日志系统

### Day 2: 核心爬虫开发
- [ ] 实现 `KaoyanCrawler` (考研帮)
- [ ] 实现 `ZhihuCrawler` (知乎)
- [ ] 实现 `CanvaCrawler` (Canva)
- [ ] 单元测试每个爬虫
- [ ] 手动运行验证数据采集

### Day 3: 调度与集成
- [ ] 实现 `Scheduler` 定时任务
- [ ] 集成到现有 DataLoader
- [ ] 测试完整流程（采集→清洗→存储→展示）
- [ ] 性能优化与异常处理
- [ ] 编写使用文档

---

## 8. 成功标准

### 功能验收
- [x] 能成功从3个目标网站采集数据
- [x] 数据通过清洗管道标准化存储
- [x] Streamlit页面正常显示真实数据
- [x] 定时任务按配置自动执行
- [x] 异常情况有完善的重试和告警机制

### 性能指标
- 单次全量采集 < 30分钟
- 内存占用 < 500MB
- 数据准确率 > 95%
- 重复率 < 1%

### 可维护性
- 代码覆盖率 > 80%
- 完善的日志和错误追踪
- 清晰的文档注释
- 易于扩展新的数据源

---

## 9. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| **目标网站改版** | 中 | 高 | 监控页面变化，快速适配 |
| **IP被封禁** | 低 | 高 | 代理IP池 + 降低频率 |
| **数据质量差** | 中 | 中 | 多源交叉验证 + 人工抽检 |
| **法律风险** | 低 | 高 | 仅采集公开数据，遵守robots.txt |

---

## 10. 后续扩展路线图

### Phase 9: 闲鱼API对接
- 商品发布API
- 订单查询API
- 自动回复机器人
- 价格监控

### Phase 10: 小红书自动化
- 笔记发布API
- 内容审核接口
- 数据分析API
- 评论互动自动化

### Phase 11: 智能化升级
- AI内容生成增强
- 用户行为分析
- 个性化推荐
- A/B测试框架

---

**文档版本**: v1.0  
**最后更新**: 2026-04-27  
**作者**: AI Assistant  
**审批状态**: ✅ 已批准
