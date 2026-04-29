# 闲鱼虚拟产品自动化工作流系统 - 设计规格文档

**项目名称：** Xianyu Virtual Product Workflow System  
**版本：** v1.0  
**创建日期：** 2026-04-27  
**技术栈：** Python + Streamlit + JSON + Jinja2  
**架构模式：** 单体集成式架构（Multipage）

---

## 一、项目概述

### 1.1 项目目标
构建一个功能完善的自动化工作流系统，用于：
1. 自动检索、筛选和整理考研相关资料
2. 收集、分类和管理各类办公模板
3. 整合考研英语资料包（词汇、语法、阅读、写作等）
4. 自动生成小红书平台风格的推广笔记

### 1.2 核心价值主张
- **自动化：** 减少人工操作，提升效率
- **模块化：** 各功能独立可维护、易扩展
- **用户友好：** 直观的Web界面，一键操作
- **智能化：** 模板化内容生成，支持多风格输出

### 1.3 目标用户
- 闲鱼虚拟产品卖家
- 副业从业者/轻创业者
- 需要高效整理资料的个人用户

---

## 二、系统架构

### 2.1 架构类型
**单体集成式架构（Streamlit Multipage）**

### 2.2 分层设计

```
┌─────────────────────────────────────────────────┐
│              表现层 (Streamlit Pages)            │
│   考研资料页 | 办公模板页 | 英语资料页 | 笔记生成页 │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                服务层 (Services)                 │
│ DataCollector | FileManager | ContentGen | Exporter│
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                数据层 (Data)                     │
│     JSON文件存储 | 文件系统 | 模板引擎           │
└─────────────────────────────────────────────────┘
```

### 2.3 目录结构

```
xianyu_xunishangpin/
├── app.py                       # Streamlit主入口
├── config.py                    # 全局配置
├── requirements.txt             # 依赖列表
│
├── pages/                       # 多页面（自动发现）
│   ├── __init__.py
│   ├── 1_📚_考研资料获取.py
│   ├── 2_📝_办公模板管理.py
│   ├── 3_📖_英语资料包.py
│   └── 4_✍️_笔记生成器.py
│
├── services/                    # 核心业务逻辑
│   ├── data_collector.py        # 数据采集服务
│   ├── file_manager.py          # 文件管理服务
│   ├── content_generator.py     # 内容生成服务
│   └── exporter.py              # 导出分享服务
│
├── models/                      # 数据模型定义
│   ├── kaoyan_model.py
│   ├── office_model.py
│   ├── english_model.py
│   └── note_model.py
│
├── utils/                       # 工具函数库
│   ├── data_loader.py           # JSON数据加载器
│   ├── template_engine.py       # Jinja2模板引擎封装
│   └── helpers.py               # 通用辅助函数
│
├── data/                        # JSON数据存储
│   ├── kaoyan_data.json
│   ├── office_data.json
│   ├── english_data.json
│   └── notes_data.json
│
├── files/                       # 文件存储
│   ├── templates/
│   ├── english/
│   ├── exports/
│   └── generated/
│
└── assets/                      # 静态资源
    └── styles.css
```

---

## 三、核心模块详细设计

### 3.1 模块一：📚 考研资料获取模块

**功能清单：**
- ✅ 自动检索考研资料（模拟数据采集）
- ✅ 多维度筛选（科目、年份、类型、状态）
- ✅ 关键词搜索
- ✅ 资料详情预览
- ✅ 批量选择与导出
- ✅ 数据统计可视化
- ✅ 定期更新机制（手动触发）

**数据模型：**
```python
@dataclass
class KaoyanMaterial:
    id: str
    title: str
    subject: str              # 政治/英语/数学/专业课
    year: int
    material_type: str         # 真题/大纲/复习指南/笔记
    description: str
    file_path: str
    file_size: str
    file_format: str
    download_count: int
    rating: float
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    source: str
```

**UI组件：**
- 搜索栏（st.text_input + st.button）
- 筛选器（st.multiselect / st.selectbox）
- 数据表格（st.dataframe / st.table）
- 详情展示（st.expander / st.modal）
- 批量操作按钮
- 统计图表（st.chart）

---

### 3.2 模块二：📝 办公模板管理功能

**功能清单：**
- ✅ 分类浏览（PPT/Word/Excel/简历等）
- ✅ 卡片网格视图展示
- ✅ 模板预览（缩略图+详情）
- ✅ 一键下载
- ✅ 智能搜索（名称+标签）
- ✅ 自定义筛选
- ✅ 收藏功能
- ✅ 统计总览

**数据模型：**
```python
@dataclass
class OfficeTemplate:
    id: str
    name: str
    category: str             # PPT/Word/Excel/简历等
    subcategory: str
    description: str
    preview_image: str
    file_path: str
    file_format: str
    file_size: str
    tags: List[str]
    difficulty: str           # 入门/进阶/高级
    download_count: int
    rating: float
    is_premium: bool
    created_at: datetime
```

**UI布局：**
- 横向分类导航（按钮组/Tabs）
- 搜索栏
- 3列网格卡片布局（st.columns(3)）
- 每个卡片包含：预览图、名称、评分、下载量、操作按钮

---

### 3.3 模块三：📖 考研英语资料包整合

**功能清单：**
- ✅ 资料包总览（元信息展示）
- ✅ 分类导航（词汇/语法/阅读/写作/听力/真题）
- ✅ 子类别资源列表
- ✅ 单文件下载
- ✅ 完整包下载
- ✅ 学习路径建议
- ✅ 资源关联推荐

**数据模型：**
```python
@dataclass
class EnglishResource:
    id: str
    package_name: str
    category: str              # 词汇/语法/阅读/写作/听力/真题
    title: str
    description: str
    file_path: str
    file_size: str
    file_format: str
    difficulty: str            # 基础/强化/冲刺
    priority: str              # 必看/推荐/选学
    study_hours: int
    related_resources: List[str]
```

**特色功能：**
- 资料包配置文件（package_config.json）
- 层级目录结构展示
- 优先级标签（必看⭐/推荐✓/选学○）

---

### 3.4 模块四：✍️ 小红书笔记生成器 ⭐核心亮点

**功能清单：**
- ✅ 选择素材来源（从其他三个模块选取内容）
- ✅ 笔记风格选择（干货分享/经验分享/种草推荐）
- ✅ 语气调性调整（亲切姐妹风/专业导师风/幽默吐槽风）
- ✅ 目标受众设定
- ✅ 标题长度控制
- ✅ 多版本生成（1-3个版本）
- ✅ 实时预览
- ✅ 智能标签推荐
- ✅ 配图建议
- ✅ 一键复制/保存/导出

**生成引擎架构：**
- 标题模板库（每个风格10+模板）
- 正文Jinja2模板（9种风格×语气组合）
- 标签推荐算法（基于内容匹配+热门标签库）
- 配图建议规则引擎

**输出格式：**
```json
{
  "version": 1,
  "title": "生成的标题",
  "body": "生成的正文内容",
  "tags": ["#标签1", "#标签2"],
  "image_suggestions": ["建议1", "建议2"],
  "metadata": {
    "style": "干货分享",
    "tone": "亲切姐妹风",
    "char_count": 500,
    "emoji_count": 15
  }
}
```

---

## 四、技术规格

### 4.1 依赖库

| 库名 | 版本 | 用途 |
|------|------|------|
| streamlit | ^1.30.0 | Web UI框架 |
| pandas | ^2.0.0 | 数据处理 |
| jinja2 | ^3.1.0 | 模板渲染 |
| pyperclip | ^1.8.0 | 剪贴板操作 |

### 4.2 Python版本要求
- **最低版本：** Python 3.9+
- **推荐版本：** Python 3.10 或 3.11

### 4.3 数据存储规范

**JSON文件结构标准：**
```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "ISO8601时间戳",
    "total_count": 数字,
    "source": "来源标识"
  },
  "[数据键名]": [数据列表]
}
```

### 4.4 接口规范

**服务层统一接口签名：**
- 所有公开方法使用类型注解
- 返回值统一为具体类型或List/Dict
- 异常通过自定义异常类抛出
- 日志记录关键操作

### 4.5 错误处理策略

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 文件未找到 | 记录日志 + 返回空结果 | "所需文件不存在" |
| JSON解析错误 | 记录日志 + 使用默认值 | "数据加载异常" |
| 权限错误 | 记录日志 + 提示用户 | "权限不足" |
| 网络错误 | 重试机制 + 降级处理 | "网络连接失败" |
| 业务逻辑错误 | 校验前置 + 友好提示 | 具体错误原因 |

---

## 五、用户体验设计

### 5.1 导航设计
- **主页面：** 系统概览 + 快速入口
- **侧边栏：** 系统状态 + 导航辅助
- **多Tab切换：** 四大功能模块

### 5.2 交互原则
- **即时反馈：** 操作后立即显示结果
- **渐进式披露：** 先概览后详情
- **一键操作：** 常用功能一步到位
- **容错性：** 支持撤销和重做

### 5.3 视觉设计
- **配色方案：** 清新专业（蓝紫渐变主题）
- **图标系统：** Emoji + 简洁图标
- **响应式布局：** 适配不同屏幕尺寸
- **加载状态：** 进度条/骨架屏/Spinner

---

## 六、扩展性设计

### 6.1 新增模块流程
1. 在 `pages/` 创建新页面文件（按命名规范）
2. 在 `models/` 定义数据模型
3. 在 `services/` 实现业务逻辑
4. 在 `data/` 创建JSON数据文件
5. 更新 `config.py` 配置

### 6.2 接入真实数据源
- 修改 `DataCollectorService` 的采集方法
- 替换模拟数据为真实API/爬虫调用
- 保持接口签名不变

### 6.3 升级AI能力
- 在 `ContentGeneratorService` 中集成LLM API
- 保留模板化生成作为fallback
- 支持用户自选生成方式

---

## 七、测试策略

### 7.1 单元测试
- 每个service方法对应测试用例
- 数据校验逻辑全覆盖
- 边界条件测试

### 7.2 集成测试
- 页面间数据流转测试
- 文件导入导出测试
- 端到端工作流测试

### 7.3 用户验收测试
- 功能完整性检查
- UI/UX体验验证
- 性能压力测试

---

## 八、部署方案

### 8.1 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

### 8.2 生产部署（可选）
- **Streamlit Cloud：** 免费托管，一键部署
- **Docker容器化：** 可移植的部署方案
- **云服务器：** AWS/GCP/Aliyun + Nginx反向代理

---

## 九、维护指南

### 9.1 日常维护
- 定期备份 `data/` 目录下的JSON文件
- 监控日志文件 `app.log`
- 更新模拟数据保持时效性

### 9.2 版本升级
- 遵循语义化版本号（MAJOR.MINOR.PATCH）
- 更新 `config.py` 中的版本号
- 记录变更日志

### 9.3 故障排查
- 查看日志定位问题
- 检查数据文件完整性
- 验证依赖库兼容性

---

## 十、交付物清单

### 10.1 代码文件
- [x] 主入口文件 `app.py`
- [x] 配置文件 `config.py`
- [x] 依赖声明 `requirements.txt`
- [x] 4个功能页面（pages/）
- [x] 4个服务模块（services/）
- [x] 4个数据模型（models/）
- [x] 3个工具模块（utils/）

### 10.2 数据文件
- [x] 模拟数据JSON文件（4个）
- [x] Jinja2笔记模板（9个）
- [x] 示例文件（可选）

### 10.3 文档文件
- [x] 本设计规格文档
- [x] README.md 使用指南
- [x] API接口文档（代码注释）

---

**文档状态：** ✅ 已批准  
**下一步行动：** 进入实现阶段（Implementation Phase）  
**预计开发时间：** 2-3天（完整MVP）
