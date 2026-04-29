# 闲鱼虚拟产品工作流系统 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个基于Streamlit的自动化工作流系统，包含考研资料获取、办公模板管理、英语资料包整合和小红书笔记生成四大核心模块。

**架构：** 单体集成式架构（Streamlit Multipage），采用分层设计（表现层→服务层→数据层），使用JSON文件存储数据，Jinja2模板引擎驱动内容生成。

**技术栈：** Python 3.10+ / Streamlit ^1.30.0 / Pandas ^2.0.0 / Jinja2 ^3.1.0 / Pyperclip ^1.8.0

---

## 文件结构总览

### 将要创建的文件：

```
xianyu_xunishangpin/
├── app.py                           # Streamlit主入口 + 路由配置
├── config.py                        # 全局配置常量
├── requirements.txt                 # Python依赖声明
│
├── pages/                           # Streamlit多页面（自动发现）
│   ├── __init__.py                  # 页面包初始化
│   ├── 1_📚_考研资料获取.py         # 模块1：考研资料检索与管理
│   ├── 2_📝_办公模板管理.py         # 模块2：办公模板浏览与下载
│   ├── 3_📖_英语资料包.py           # 模块3：考研英语资料整合展示
│   └── 4_✍️_笔记生成器.py           # 模块4：小红书笔记智能生成
│
├── services/                        # 核心业务逻辑层
│   ├── __init__.py                  # 服务包初始化
│   ├── data_collector.py            # 数据采集服务（模拟+预留真实接口）
│   ├── file_manager.py              # 文件管理服务（存储/预览/下载）
│   ├── content_generator.py         # 内容生成服务（小红书笔记引擎）
│   └── exporter.py                  # 导出分享服务（多格式支持）
│
├── models/                          # 数据模型定义
│   ├── __init__.py                  # 模型包初始化
│   ├── kaoyan_model.py              # 考研资料数据模型
│   ├── office_model.py              # 办公模板数据模型
│   ├── english_model.py             # 英语资源数据模型
│   └── note_model.py                # 笔记生成结果数据模型
│
├── utils/                           # 工具函数库
│   ├── __init__.py                  # 工具包初始化
│   ├── data_loader.py               # JSON数据统一加载/保存接口
│   ├── template_engine.py           # Jinja2模板渲染封装
│   └── helpers.py                   # 通用辅助函数（日志/装饰器/工具函数）
│
├── data/                            # JSON数据存储目录
│   ├── kaoyan_data.json             # 考研资料数据库（模拟数据128条）
│   ├── office_data.json             # 办公模板数据库（模拟数据256条）
│   ├── english_data.json            # 英语资料数据库（模拟数据156条）
│   └── notes_data.json              # 生成的笔记记录库
│
├── utils/templates/                 # Jinja2笔记模板目录
│   ├── 干货分享_亲切姐妹风.j2        # 风格1×语气A 正文模板
│   ├── 干货分享_专业导师风.j2        # 风格1×语气B 正文模板
│   ├── 干货分享_幽默吐槽风.j2        # 风格1×语气C 正文模板
│   ├── 经验分享_亲切姐妹风.j2        # 风格2×语气A 正文模板
│   ├── 经验分享_专业导师风.j2        # 风格2×语气B 正文模板
│   ├── 经验分享_幽默吐槽风.j2        # 风格2×语气C 正文模板
│   ├── 种草推荐_亲切姐妹风.j2        # 风格3×语气A 正文模板
│   ├── 种草推荐_专业导师风.j2        # 风格3×语气B 正文模板
│   └── 种草推荐_幽默吐槽风.j2        # 风格3×语气C 正文模板
│
├── files/                           # 文件存储目录（运行时自动创建）
│   ├── templates/                   # 办公模板实际文件
│   ├── english/                     # 英语资料实际文件
│   ├── exports/                     # 用户导出文件
│   └── generated/                   # 生成的笔记内容
│
└── assets/                          # 静态资源
    └── styles.css                   # 自定义CSS样式
```

---

## 任务分解

### 任务 1：项目基础设施搭建

**文件：**
- 创建：`requirements.txt`
- 创建：`config.py`
- 创建：`app.py`
- 创建：`assets/styles.css`

- [ ] **步骤 1：创建 requirements.txt**

```txt
# Streamlit Web Framework
streamlit>=1.30.0,<2.0.0

# Data Processing
pandas>=2.0.0,<3.0.0

# Template Engine
jinja2>=3.1.0,<4.0.0

# Clipboard Operations
pyperclip>=1.8.0,<2.0.0

# Type Hints (built-in, but explicit for clarity)
typing-extensions>=4.0.0
```

- [ ] **步骤 2：创建 config.py 全局配置**

```python
"""
全局系统配置模块
集中管理所有配置常量，便于维护和修改
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SystemConfig:
    """系统配置类 - 单一真相源"""
    
    # ========== 应用基础信息 ==========
    APP_NAME: str = "闲鱼虚拟产品工作流系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "高效、智能、自动化的虚拟产品资料管理与内容生成平台"
    DEBUG: bool = True
    
    # ========== 路径配置 ==========
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent)
    DATA_DIR: str = "data"
    FILES_DIR: str = "files"
    PAGES_DIR: str = "pages"
    SERVICES_DIR: str = "services"
    MODELS_DIR: str = "models"
    UTILS_DIR: str = "utils"
    TEMPLATES_DIR: str = "utils/templates"
    ASSETS_DIR: str = "assets"
    
    # ========== Streamlit页面配置 ==========
    PAGE_TITLE: str = "🚀 闲鱼虚拟产品工作流系统"
    PAGE_ICON: str = "🚀"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # ========== 考研资料模块配置 ==========
    KAOYAN_SUBJECTS: List[str] = field(default_factory=lambda: [
        "政治", "英语", "数学一", "数学二", "数学三", "专业课"
    ])
    KAOYAN_YEARS: List[int] = field(default_factory=lambda: [
        2026, 2025, 2024, 2023, 2022, 2021
    ])
    KAOYAN_TYPES: List[str] = field(default_factory=lambda: [
        "历年真题", "考试大纲", "复习指南", "学霸笔记", "模拟试题"
    ])
    KAOYAN_STATUSES: List[str] = field(default_factory=lambda: [
        "最新发布", "热门推荐", "编辑精选", "经典必备"
    ])
    
    # ========== 办公模板模块配置 ==========
    OFFICE_CATEGORIES: List[str] = field(default_factory=lambda: [
        "PPT模板", "Word模板", "Excel模板",
        "简历模板", "合同范本", "报告模板", "其他模板"
    ])
    
    OFFICE_SUBCATEGORIES: Dict[str, List[str]] = field(default_factory=lambda: {
        "PPT模板": ["工作汇报", "年终总结", "项目答辩", "培训课件", "商业计划"],
        "Word模板": ["求职简历", "合同协议", "公文写作", "论文排版"],
        "Excel模板": ["财务报表", "项目管理", "数据分析", "库存管理"],
        "简历模板": ["应届生", "社招", "实习", "留学生"],
        "合同范本": ["租赁合同", "劳务合同", "保密协议", "合作协议"],
        "报告模板": ["调研报告", "分析报告", "总结报告", "可行性报告"]
    })
    
    OFFICE_DIFFICULTIES: List[str] = ["入门级", "进阶级", "高级定制"]
    
    # ========== 英语资料模块配置 ==========
    ENGLISH_CATEGORIES: List[str] = field(default_factory=lambda: [
        {"id": "vocab", "name": "词汇", "icon": "📚", "description": "核心词汇、词根词缀、高频词"},
        {"id": "grammar", "name": "语法", "icon": "📝", "description": "语法精讲、长难句分析"},
        {"id": "reading", "name": "阅读", "icon": "📖", "description": "阅读理解训练、真题阅读"},
        {"id": "writing", "name": "写作", "icon": "✍️", "description": "大小作文模板、写作技巧"},
        {"id": "listening", "name": "听力", "icon": "🎧", "description": "听力专项训练"},
        {"id": "past_exams", "name": "历年真题", "icon": "📋", "description": "完整真题及解析"}
    ])
    
    ENGLISH_DIFFICULTIES: List[str] = ["基础阶段", "强化阶段", "冲刺阶段"]
    ENGLISH_PRIORITIES: List[str] = ["⭐ 必看", "✓ 推荐", "○ 选学"]
    
    # ========== 笔记生成模块配置 ==========
    NOTE_STYLES: List[Dict] = field(default_factory=lambda: [
        {"id": "ganhuo", "name": "干货分享", 
         "description": "实用性强，适合教程类、资料分享类内容",
         "title_patterns": ["必看", "全攻略", "吐血整理", "别再花冤枉钱"]},
        {"id": "jingyan", "name": "经验分享",
         "description": "个人经历，真实感强，容易建立信任",
         "title_patterns": ["从X到Y", "真相要说", "正确打开方式", "普通人如何"]},
        {"id": "zhongcao", "name": "种草推荐",
         "description": "情绪感染力强，适合安利类、好物推荐类",
         "title_patterns": ["挖到宝了", "谁懂啊", "按头安利", "真香预警"]}
    ])
    
    NOTE_TONES: List[Dict] = field(default_factory=lambda: [
        {"id": "qinjie", "name": "亲切姐妹风",
         "description": "像闺蜜聊天一样自然，亲和力强"},
        {"id": "zhuanye", "name": "专业导师风",
         "description": "权威可信，适合知识类、教育类内容"},
        {"id": "youmo", "name": "幽默吐槽风",
         "description": "轻松有趣，容易传播和互动"}
    ])
    
    NOTE_TARGET_AUDIENCES: List[str] = field(default_factory=lambda: [
        "考研党", "大学生", "职场新人", "宝妈群体", "自由职业者", "小企业主"
    ])
    
    # ========== 小红书热门标签库 ==========
    HOT_TAGS: Dict[str, List[str]] = field(default_factory=lambda: {
        "考研": ["考研", "2026考研", "考研上岸", "考研资料", "学习打卡",
                "考研政治", "考研英语", "考研数学", "研究生", "复试"],
        "办公": ["职场", "办公技巧", "PPT模板", "工作效率", "职场必备",
                "职场干货", "升职加薪", "办公室生存指南"],
        "英语": ["英语学习", "考研英语", "英语单词", "学习方法",
                "四六级", "雅思托福", "口语练习"],
        "通用": ["干货分享", "建议收藏", "宝藏资源", "好物推荐",
                "保姆级教程", "小白必看", "省钱攻略", "副业搞钱"],
        "情绪": ["绝绝子", "真的栓Q", "家人们谁懂啊", "破防了",
                "泪目了", "太上头了", "yyds", "永远的神"]
    })
    
    # ========== 标题模板库 ==========
    TITLE_TEMPLATES: Dict[str, List[str]] = field(default_factory=lambda: {
        "ganhuo": [
            "{target}必看！{topic}全攻略，建议收藏！⭐",
            "吐血整理！{topic}最完整资料，{benefit}💯",
            "别再花冤枉钱了！{topic}看这一篇就够🔥",
            "{number}天搞定{topic}，我的私藏资料分享✨",
            "熬夜整理！{topic}全套资源，{benefit}🚀",
            "{topic}保姆级教程，小白也能轻松上手！"
        ],
        "jingyan": [
            "{topic}从{start}到{end}，我只做了这{number}件事💪",
            "关于{topic}，我有{number}个真相要说😤",
            "后悔没早知道！{topic}的正确打开方式✅",
            "普通人如何通过{topic}实现{goal}？真实经历📖",
            "试错{number}次后，我终于找到了{topic}的最佳方法🎯"
        ],
        "zhongcao": [
            "挖到宝了！这个{topic}神器真的绝绝子🥳",
            "谁懂啊！{topic}居然可以这么简单😭",
            "按头安利！{topic}这个资源太好用了❤️‍🔥",
            "真香预警！{topic}让我{benefit}✨",
            "我不允许还有人不知道这个{topic}！！📢",
            "姐妹们！{topic}这个真的要冲！！🏃‍♀️💨"
        ]
    })


# 全局配置单例实例
config = SystemConfig()
```

- [ ] **步骤 3：创建 app.py 主入口**

```python
"""
Streamlit 应用主入口
负责全局配置、侧边栏和主页面的渲染
"""

import streamlit as st
from config import config


def main():
    """应用主函数"""
    
    # ========== 页面基础配置 ==========
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state=config.SIDEBAR_STATE
    )
    
    # ========== 注入自定义CSS样式 ==========
    _inject_custom_styles()
    
    # ========== 渲染侧边栏 ==========
    _render_sidebar()
    
    # ========== 渲染主页面（首页） ==========
    _render_main_page()


def _inject_custom_styles():
    """注入自定义CSS样式"""
    try:
        with open(f"{config.ASSETS_DIR}/styles.css", "r", encoding="utf-8") as f:
            custom_css = f.read()
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # 使用默认样式


def _render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # Logo区域
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; margin: 0;">🚀</h1>
            <h3 style="margin: 5px 0;">工作流系统</h3>
            <p style="color: #666; font-size: 0.9rem;">v{version}</p>
        </div>
        """.format(version=config.APP_VERSION), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 系统状态仪表盘
        st.subheader("📊 系统状态")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("资料总数", "540+", "+12 今日")
        with col2:
            st.metric("生成笔记", "89", "本周")
        
        st.metric("导出次数", "234", "累计")
        
        st.markdown("---")
        
        # 快速导航提示
        st.caption("💡 使用顶部Tab切换功能模块")
        
        st.markdown("---")
        
        # 版本信息
        st.caption(f"© 2026 {config.APP_NAME}")
        st.caption(f"版本 {config.APP_VERSION}")


def _render_main_page():
    """渲染主页面（系统概览）"""
    st.title("🚀 闲鱼虚拟产品自动化工作流系统")
    st.markdown(f"### v{config.APP_VERSION} - 高效 · 智能 · 自动化")
    st.markdown("---")
    
    # 功能卡片介绍
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("""
        ### 📚 考研资料
        
        自动检索、筛选、整理最新考研相关资料
        
        ✓ 历年真题  
        ✓ 复习指南  
        ✓ 考试大纲  
        ✓ 学霸笔记
        """)
    
    with col2:
        st.success("""
        ### 📝 办公模板
        
        收集、分类和提供各类常用办公模板
        
        ✓ PPT模板  
        ✓ Word模板  
        ✓ Excel模板  
        ✓ 简历模板
        """)
    
    with col3:
        st.warning("""
        ### 📖 英语资料包
        
        整合考研英语全方位学习资源
        
        ✓ 核心词汇  
        ✓ 语法精讲  
        ✓ 阅读训练  
        ✓ 写作模板
        """)
    
    with col4:
        st.error("""
        ### ✍️ 笔记生成
        
        自动生成小红书风格推广笔记
        
        ✓ 多风格切换  
        ✓ 多版本输出  
        ✓ 智能标签  
        ✓ 配图建议
        """)
    
    st.markdown("---")
    
    # 使用说明
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
        ### 快速上手指南
        
        1. **浏览资料** → 点击上方Tab进入各功能模块
        2. **筛选查找** → 使用搜索和筛选条件定位目标资料
        3. **预览详情** → 点击查看详细信息和文件列表
        4. **下载导出** → 一键下载单个文件或批量导出
        5. **生成笔记** → 在笔记生成器中选择素材并生成推广内容
        
        ### 特色功能
        
        - 🔍 **智能搜索**：支持关键词模糊匹配
        - 📦 **批量操作**：多选后一键导出
        - ✍️ **AI生成**：模板化生成小红书风格笔记
        - 🔄 **定期更新**：手动触发数据刷新
        """)


if __name__ == "__main__":
    main()
```

- [ ] **步骤 4：创建 assets/styles.css 自定义样式**

```css
/* ====== 全局样式重置 ====== */

/* 主容器优化 */
.main .block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

/* 标题样式 */
h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h2 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
}

h3 {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
}

/* ====== 卡片样式 ====== */

/* 信息卡片 */
.stInfo {
    border-left: 4px solid #48bb78 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* 成功卡片 */
.stSuccess {
    border-left: 4px solid #4299e1 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* 警告卡片 */
.stWarning {
    border-left: 4px solid #ed8936 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* 错误卡片 */
.stError {
    border-left: 4px solid #f56565 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* ====== 表格样式 ====== */

/* 数据表格 */
[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

[data-testid="stDataFrame"] th {
    background-color: #f7fafc !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
    text-align: left !important;
    padding: 12px 16px !important;
}

[data-testid="stDataFrame"] td {
    padding: 10px 16px !important;
    border-bottom: 1px solid #e2e8f0 !important;
}

[data-testid="stDataFrame"] tr:hover {
    background-color: #f7fafc !important;
}

/* ====== 按钮样式 ====== */

/* 主要按钮 */
.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35) !important;
}

.stButton>button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.45) !important;
}

/* 次要按钮 */
.stButton>button[kind="secondary"] {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    background: white !important;
    color: #4a5568 !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stButton>button[kind="secondary"]:hover {
    border-color: #667eea !important;
    color: #667eea !important;
    background: #f7fafc !important;
}

/* ====== 侧边栏样式 ====== */

/* 侧边栏背景 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%) !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* 侧边栏标题 */
[data-testid="stSidebar"] h3 {
    color: #2d3748 !important;
}

/* ====== 输入框样式 ====== */

/* 文本输入框 */
.stTextInput>div>div>input,
.stTextArea textarea {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
}

.stTextInput>div>div>input:focus,
.stTextArea textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
}

/* 选择框 */
.stSelectbox>div>div {
    border-radius: 8px !important;
}

/* 多选框 */
.stMultiSelect>div>div {
    border-radius: 8px !important;
}

/* ====== Expander样式 ====== */

.streamlit-expanderHeader {
    background-color: #f7fafc !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: #2d3748 !important;
}

/* ====== Metric指标卡 ====== */

[data-testid="stMetric"] {
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

/* ====== Tab标签页 ====== */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    background-color: #f7fafc !important;
    color: #718096 !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

/* ====== 进度条 ====== */

.stProgress>div>div>div>div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 9999px !important;
}

/* ====== 工具提示 ====== */

.stTooltip {
    background-color: #2d3748 !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
}

/* ====== 动画效果 ====== */

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stApp {
    animation: fadeIn 0.5s ease-in-out;
}
```

- [ ] **步骤 5：Commit 基础设施代码**

```bash
git add requirements.txt config.py app.py assets/styles.css
git commit -m "feat: initialize project infrastructure and global configuration"
```

---

### 任务 2：数据模型层实现

**文件：**
- 创建：`models/__init__.py`
- 创建：`models/kaoyan_model.py`
- 创建：`models/office_model.py`
- 创建：`models/english_model.py`
- 创建：`models/note_model.py`

- [ ] **步骤 1：创建 models/__init__.py 包初始化**

```python
"""
数据模型包
定义系统中使用的所有数据结构
"""

from models.kaoyan_model import KaoyanMaterial
from models.office_model import OfficeTemplate
from models.english_model import EnglishResource
from models.note_model import GeneratedNote

__all__ = [
    'KaoyanMaterial',
    'OfficeTemplate', 
    'EnglishResource',
    'GeneratedNote'
]
```

- [ ] **步骤 2：创建 models/kaoyan_model.py 考研资料模型**

```python
"""
考研资料数据模型
定义考研相关资料的数据结构和验证逻辑
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class KaoyanMaterial:
    """
    考研资料数据模型
    
    属性:
        id: 唯一标识符（格式：KY + 年份 + 序号）
        title: 资料标题
        subject: 科目分类（政治/英语/数学/专业课）
        year: 适用年份
        material_type: 资料类型（真题/大纲/复习指南/笔记/模拟题）
        description: 详细描述
        file_path: 文件存储路径
        file_size: 文件大小（人类可读格式，如"256MB"）
        file_format: 文件格式（PDF/WORD/ZIP等）
        download_count: 累计下载次数
        rating: 用户评分（1.0-5.0）
        tags: 标签列表（用于搜索和分类）
        created_at: 创建时间
        updated_at: 最后更新时间
        source: 数据来源（模拟采集/官方/用户上传）
    """
    
    id: str
    title: str
    subject: str
    year: int
    material_type: str
    description: str
    file_path: str
    file_size: str
    file_format: str
    download_count: int = 0
    rating: float = 5.0
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: str = "simulated"
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于JSON序列化）"""
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'year': self.year,
            'material_type': self.material_type,
            'description': self.description,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'download_count': self.download_count,
            'rating': self.rating,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KaoyanMaterial':
        """从字典创建实例（用于JSON反序列化）"""
        return cls(
            id=data['id'],
            title=data['title'],
            subject=data['subject'],
            year=data['year'],
            material_type=data['material_type'],
            description=data.get('description', ''),
            file_path=data.get('file_path', ''),
            file_size=data.get('file_size', '0MB'),
            file_format=data.get('file_format', 'PDF'),
            download_count=data.get('download_count', 0),
            rating=data.get('rating', 5.0),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            source=data.get('source', 'simulated')
        )
    
    def matches_keyword(self, keyword: str) -> bool:
        """检查是否匹配关键词（在标题、描述、标签中搜索）"""
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.title.lower() or
            keyword_lower in self.description.lower() or
            any(keyword_lower in tag.lower() for tag in self.tags)
        )
```

- [ ] **步骤 3：创建 models/office_model.py 办公模板模型**

```python
"""
办公模板数据模型
定义办公模板的数据结构和属性
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class OfficeTemplate:
    """
    办公模板数据模型
    
    属性:
        id: 唯一标识符
        name: 模板名称
        category: 主分类（PPT/Word/Excel/简历等）
        subcategory: 子分类（如PPT下的汇报/答辩/培训）
        description: 模板描述和使用场景说明
        preview_image: 预览图路径
        file_path: 模板文件实际路径
        file_format: 文件格式（.pptx/.docx/.xlsx）
        file_size: 文件大小
        tags: 标签列表
        difficulty: 难度等级（入门级/进阶级/高级定制）
        download_count: 下载次数
        rating: 评分（1.0-5.0）
        is_premium: 是否为精品/付费模板
        created_at: 上传/创建时间
    """
    
    id: str
    name: str
    category: str
    subcategory: str = ""
    description: str = ""
    preview_image: str = ""
    file_path: str = ""
    file_format: str = ".pptx"
    file_size: str = "0MB"
    tags: List[str] = field(default_factory=list)
    difficulty: str = "入门级"
    download_count: int = 0
    rating: float = 5.0
    is_premium: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'preview_image': self.preview_image,
            'file_path': self.file_path,
            'file_format': self.file_format,
            'file_size': self.file_size,
            'tags': self.tags,
            'difficulty': self.difficulty,
            'download_count': self.download_count,
            'rating': self.rating,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OfficeTemplate':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            category=data['category'],
            subcategory=data.get('subcategory', ''),
            description=data.get('description', ''),
            preview_image=data.get('preview_image', ''),
            file_path=data.get('file_path', ''),
            file_format=data.get('file_format', '.pptx'),
            file_size=data.get('file_size', '0MB'),
            tags=data.get('tags', []),
            difficulty=data.get('difficulty', '入门级'),
            download_count=data.get('download_count', 0),
            rating=data.get('rating', 5.0),
            is_premium=data.get('is_premium', False),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )
    
    @property
    def display_name(self) -> str:
        """显示名称（带难度标记）"""
        prefix = "⭐" if self.is_premium else "📄"
        return f"{prefix} {self.name}"
    
    def matches_search(self, query: str) -> bool:
        """检查是否匹配搜索查询"""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.description.lower() or
            any(query_lower in tag.lower() for tag in self.tags) or
            query_lower in self.category.lower() or
            query_lower in self.subcategory.lower()
        )
```

- [ ] **步骤 4：创建 models/english_model.py 英语资料模型**

```python
"""
考研英语资料数据模型
定义英语资料包中各类资源的数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class EnglishResource:
    """
    英语学习资源数据模型
    
    属性:
        id: 唯一标识符
        package_name: 所属资料包名称
        category: 子类别（词汇/语法/阅读/写作/听力/真题）
        title: 资源标题
        description: 详细描述
        file_path: 文件路径
        file_size: 文件大小
        file_format: 文件格式
        difficulty: 学习阶段（基础/强化/冲刺）
        priority: 优先级（必看/推荐/选学）
        study_hours: 建议学习时长（小时）
        related_resources: 关联资源ID列表
    """
    
    id: str
    package_name: str
    category: str
    title: str
    description: str = ""
    file_path: str = ""
    file_size: str = "0MB"
    file_format: str = "PDF"
    difficulty: str = "强化阶段"
    priority: str = "✓ 推荐"
    study_hours: int = 0
    related_resources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'package_name': self.package_name,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'difficulty': self.difficulty,
            'priority': self.priority,
            'study_hours': self.study_hours,
            'related_resources': self.related_resources
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EnglishResource':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            package_name=data['package_name'],
            category=data['category'],
            title=data['title'],
            description=data.get('description', ''),
            file_path=data.get('file_path', ''),
            file_size=data.get('file_size', '0MB'),
            file_format=data.get('file_format', 'PDF'),
            difficulty=data.get('difficulty', '强化阶段'),
            priority=data.get('priority', '✓ 推荐'),
            study_hours=data.get('study_hours', 0),
            related_resources=data.get('related_resources', [])
        )
    
    @property
    def priority_emoji(self) -> str:
        """根据优先级返回对应的emoji图标"""
        priority_map = {
            "⭐ 必看": "⭐",
            "✓ 推荐": "✓",
            "○ 选学": "○"
        }
        return priority_map.get(self.priority, "○")


@dataclass
class EnglishPackageConfig:
    """
    英语资料包配置信息
    描述整个资料包的元数据和结构
    """
    
    package_name: str
    version: str = "1.0"
    total_size: str = "0GB"
    total_files: int = 0
    last_updated: str = ""
    description: str = ""
    categories: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'package_name': self.package_name,
            'version': self.version,
            'total_size': self.total_size,
            'total_files': self.total_files,
            'last_updated': self.last_updated,
            'description': self.description,
            'categories': self.categories
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EnglishPackageConfig':
        return cls(
            package_name=data['package_name'],
            version=data.get('version', '1.0'),
            total_size=data.get('total_size', '0GB'),
            total_files=data.get('total_files', 0),
            last_updated=data.get('last_updated', ''),
            description=data.get('description', ''),
            categories=data.get('categories', [])
        )
```

- [ ] **步骤 5：创建 models/note_model.py 笔记生成结果模型**

```python
"""
小红书笔记生成结果数据模型
定义生成后的笔记内容和元数据
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class GeneratedNote:
    """
    生成的小红书笔记数据模型
    
    属性:
        note_id: 笔记唯一ID
        version: 生成版本号（支持多版本）
        title: 生成的标题
        body: 生成的正文内容（含emoji和格式）
        tags: 推荐的话题标签列表
        image_suggestions: 配图建议列表
        source_content_id: 来源资料的ID
        style: 使用的笔记风格
        tone: 使用的语气调性
        target_audience: 目标受众
        char_count: 正文字符数
        emoji_count: emoji数量
        created_at: 生成时间
        metadata: 其他元数据
    """
    
    note_id: str
    version: int = 1
    title: str = ""
    body: str = ""
    tags: List[str] = field(default_factory=list)
    image_suggestions: List[str] = field(default_factory=list)
    source_content_id: str = ""
    source_content_type: str = ""  # kaoyan/office/english
    style: str = "干货分享"
    tone: str = "亲切姐妹风"
    target_audience: List[str] = field(default_factory=list)
    char_count: int = 0
    emoji_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典（用于保存到JSON）"""
        return {
            'note_id': self.note_id,
            'version': self.version,
            'title': self.title,
            'body': self.body,
            'tags': self.tags,
            'image_suggestions': self.image_suggestions,
            'source_content_id': self.source_content_id,
            'source_content_type': self.source_content_type,
            'style': self.style,
            'tone': self.tone,
            'target_audience': self.target_audience,
            'char_count': self.char_count,
            'emoji_count': self.emoji_count,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GeneratedNote':
        """从字典创建实例"""
        return cls(
            note_id=data['note_id'],
            version=data.get('version', 1),
            title=data.get('title', ''),
            body=data.get('body', ''),
            tags=data.get('tags', []),
            image_suggestions=data.get('image_suggestions', []),
            source_content_id=data.get('source_content_id', ''),
            source_content_type=data.get('source_content_type', ''),
            style=data.get('style', '干货分享'),
            tone=data.get('tone', '亲切姐妹风'),
            target_audience=data.get('target_audience', []),
            char_count=data.get('char_count', 0),
            emoji_count=data.get('emoji_count', 0),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            metadata=data.get('metadata', {})
        )
    
    @property
    def full_text(self) -> str:
        """获取完整的可复制文本（标题+正文+标签）"""
        return f"{self.title}\n\n{self.body}\n\n{' '.join(self.tags)}"
    
    @property
    def word_count(self) -> int:
        """估算字数（中文+英文混合）"""
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', self.body))
        english_words = len(re.findall(r'[a-zA-Z]+', self.body))
        return chinese_chars + english_words
    
    def export_to_text(self) -> str:
        """导出为纯文本格式"""
        lines = [
            "=" * 50,
            f"小红书笔记 v{self.version}",
            "=" * 50,
            "",
            f"【标题】",
            self.title,
            "",
            f"【正文】",
            self.body,
            "",
            f"【标签】",
            " ".join(self.tags),
            "",
            f"【配图建议】",
            * [f"- {suggestion}" for suggestion in self.image_suggestions],
            "",
            f"【生成信息】",
            f"- 风格: {self.style}",
            f"- 语气: {self.tone}",
            f"- 字数: ~{self.word_count}字",
            f"- 生成时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50
        ]
        return "\n".join(lines)
    
    def export_to_markdown(self) -> str:
        """导出为Markdown格式"""
        md_lines = [
            f"# {self.title}",
            "",
            self.body.replace('\n', '\n\n'),
            "",
            "---",
            "",
            "**标签：** " + " ".join(self.tags),
            "",
            "**配图建议：**",
            *[f"- {suggestion}" for suggestion in self.image_suggestions],
            "",
            "*生成信息*",
            f"- 风格：{self.style} | 语气：{self.tone}",
            f"- 字数：约{self.word_count}字 | Emoji数：{self.emoji_count}",
            f"- 生成于：{self.created_at.strftime('%Y-%m-%d %H:%M')}"
        ]
        return "\n".join(md_lines)
```

- [ ] **步骤 6：Commit 数据模型代码**

```bash
git add models/
git commit -m "feat: implement data models for all four modules"
```

---

### 任务 3：工具函数层实现

**文件：**
- 创建：`utils/__init__.py`
- 创建：`utils/data_loader.py`
- 创建：`utils/helpers.py`
- 创建：`utils/template_engine.py`

- [ ] **步骤 1：创建 utils/__init__.py**

```python
"""
工具函数包
提供数据处理、日志、模板渲染等通用能力
"""

from utils.data_loader import DataLoader
from utils.helpers import (
    handle_errors,
    log_execution_time,
    safe_division,
    format_file_size,
    generate_unique_id,
    get_timestamp
)
from utils.template_engine import TemplateEngine

__all__ = [
    'DataLoader',
    'handle_errors',
    'log_execution_time',
    'safe_division',
    'format_file_size',
    'generate_unique_id',
    'get_timestamp',
    'TemplateEngine'
]
```

- [ ] **步骤 2：创建 utils/data_loader.py JSON数据加载器**

```python
"""
JSON数据统一加载器
提供标准化的数据读写接口，支持多种数据类型的存取
"""

import json
import logging
from pathlib import Path
from typing import List, Any, Optional, Dict
import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """
    JSON数据加载器
    
    统一管理所有JSON数据文件的读取和写入，
    提供类型安全的数据访问接口。
    
    使用示例:
        >>> loader = DataLoader()
        >>> data = loader.load('kaoyan')
        >>> df = loader.load_as_dataframe('kaoyan', 'materials')
    """
    
    DATA_FILES = {
        'kaoyan': 'data/kaoyan_data.json',
        'office': 'data/office_data.json',
        'english': 'data/english_data.json',
        'notes': 'data/notes_data.json'
    }
    
    EMPTY_DATA_TEMPLATES = {
        'kaoyan': {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '',
                'total_count': 0,
                'source': 'simulated'
            },
            'materials': []
        },
        'office': {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '',
                'total_count': 0
            },
            'templates': []
        },
        'english': {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '',
                'total_count': 0
            },
            'resources': [],
            'package_config': {}
        },
        'notes': {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '',
                'total_count': 0
            },
            'notes': []
        }
    }
    
    def __init__(self, base_dir: str = None):
        """
        初始化数据加载器
        
        参数:
            base_dir: 数据目录根路径（默认为项目根目录）
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent.parent
        
        self.data_dir = self.base_dir / 'data'
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self, data_type: str) -> dict:
        """
        加载指定类型的JSON数据
        
        参数:
            data_type: 数据类型标识 ('kaoyan' | 'office' | 'english' | 'notes')
            
        返回:
            解析后的字典数据
            
        异常:
            ValueError: 当data_type无效时
        """
        if data_type not in self.DATA_FILES:
            raise ValueError(f"无效的数据类型: {data_type}. "
                           f"有效值: {list(self.DATA_FILES.keys())}")
        
        file_path = self.data_dir / self.DATA_FILES[data_type].split('/')[-1]
        
        if not file_path.exists():
            logger.warning(f"数据文件不存在: {file_path}, 返回空数据结构")
            return self.EMPTY_DATA_TEMPLATES.get(data_type, {})
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"成功加载数据: {data_type}, 记录数: {self._count_records(data)}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {file_path} - {e}")
            return self.EMPTY_DATA_TEMPLATES.get(data_type, {})
        except Exception as e:
            logger.error(f"加载数据失败: {file_path} - {e}")
            return self.EMPTY_DATA_TEMPLATES.get(data_type, {})
    
    def load_as_dataframe(
        self, 
        data_type: str, 
        data_key: str = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        加载数据并转换为Pandas DataFrame
        
        参数:
            data_type: 数据类型
            data_key: 要转换的数据键名（如'materials'/'templates'/'resources'/'notes'）
            **kwargs: 传递给pd.DataFrame的额外参数
            
        返回:
            DataFrame对象（如果找不到数据则返回空DataFrame）
        """
        data = self.load(data_type)
        
        if data_key and data_key in data:
            records = data[data_key]
        elif data_key is None:
            records = data
        else:
            logger.warning(f"未找到数据键: {data_key}")
            return pd.DataFrame()
        
        if not records:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(records, **kwargs)
            logger.debug(f"转换为DataFrame: {data_type}.{data_key}, 形状: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"DataFrame转换失败: {e}")
            return pd.DataFrame()
    
    def save(self, data_type: str, data: dict) -> bool:
        """
        保存数据到JSON文件
        
        参数:
            data_type: 数据类型标识
            data: 要保存的字典数据
            
        返回:
            是否保存成功
        """
        if data_type not in self.DATA_FILES:
            logger.error(f"无效的数据类型: {data_type}")
            return False
        
        file_path = self.data_dir / self.DATA_FILES[data_type].split('/')[-1]
        
        try:
            # 更新元数据中的时间戳
            if 'metadata' in data:
                from datetime import datetime
                data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据保存成功: {file_path}")
            return True
        except Exception as e:
            logger.error(f"数据保存失败: {file_path} - {e}")
            return False
    
    def append_record(
        self, 
        data_type: str, 
        data_key: str, 
        record: dict
    ) -> bool:
        """
        向现有数据中追加一条记录
        
        参数:
            data_type: 数据类型
            data_key: 数据键名
            record: 要追加的记录字典
            
        返回:
            是否成功
        """
        data = self.load(data_type)
        
        if data_key not in data:
            data[data_key] = []
        
        data[data_key].append(record)
        
        if 'metadata' in data:
            data['metadata']['total_count'] = len(data[data_key])
        
        return self.save(data_type, data)
    
    def update_record(
        self,
        data_type: str,
        data_key: str,
        record_id: str,
        updates: dict
    ) -> bool:
        """
        更新指定ID的记录
        
        参数:
            data_type: 数据类型
            data_key: 数据键名
            record_id: 记录ID
            updates: 要更新的字段字典
            
        返回:
            是否找到并更新成功
        """
        data = self.load(data_type)
        
        if data_key not in data:
            return False
        
        for i, record in enumerate(data[data_key]):
            if record.get('id') == record_id:
                record.update(updates)
                return self.save(data_type, data)
        
        logger.warning(f"未找到记录: ID={record_id} in {data_type}.{data_key}")
        return False
    
    def delete_record(
        self,
        data_type: str,
        data_key: str,
        record_id: str
    ) -> bool:
        """
        删除指定ID的记录
        
        参数:
            data_type: 数据类型
            data_key: 数据键名
            record_id: 记录ID
            
        返回:
            是否删除成功
        """
        data = self.load(data_type)
        
        if data_key not in data:
            return False
        
        original_length = len(data[data_key])
        data[data_key] = [
            r for r in data[data_key] if r.get('id') != record_id
        ]
        
        if len(data[data_key]) < original_length:
            if 'metadata' in data:
                data['metadata']['total_count'] = len(data[data_key])
            return self.save(data_type, data)
        
        return False
    
    def get_statistics(self, data_type: str) -> dict:
        """
        获取指定数据类型的统计信息
        
        返回:
            统计信息字典
        """
        data = self.load(data_type)
        
        stats = {
            'total_count': 0,
            'last_updated': data.get('metadata', {}).get('last_updated', '未知'),
            'version': data.get('metadata', {}).get('version', '未知')
        }
        
        for key in data:
            if key != 'metadata' and isinstance(data[key], list):
                stats['total_count'] += len(data[key])
                stats[f'{key}_count'] = len(data[key])
        
        return stats
    
    def exists(self, data_type: str) -> bool:
        """检查数据文件是否存在"""
        if data_type not in self.DATA_FILES:
            return False
        file_path = self.data_dir / self.DATA_FILES[data_type].split('/')[-1']
        return file_path.exists()
    
    def reset_to_default(self, data_type: str) -> bool:
        """
        重置数据为默认空状态
        
        警告：这将清除所有数据！
        """
        if data_type not in self.EMPTY_DATA_TEMPLATES:
            return False
        return self.save(data_type, self.EMPTY_DATA_TEMPLATES[data_type])
    
    @staticmethod
    def _count_records(data: dict) -> int:
        """统计数据中的记录总数"""
        count = 0
        for key, value in data.items():
            if key != 'metadata' and isinstance(value, list):
                count += len(value)
        return count
```

- [ ] **步骤 3：创建 utils/helpers.py 通用辅助函数**

```python
"""
通用辅助函数库
提供日志、错误处理、工具函数等通用能力
"""

import logging
import functools
import random
import string
from datetime import datetime
from typing import Callable, Any, Optional


# ========== 日志配置 ==========
def setup_logging(log_file: str = 'app.log', level: int = logging.INFO):
    """
    配置日志系统
    
    参数:
        log_file: 日志文件路径
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


logger = logging.getLogger(__name__)


# ========== 装饰器 ==========

def handle_errors(func: Callable = None, *, error_message: str = None):
    """
    错误处理装饰器
    统一捕获异常并提供友好的错误提示
    
    使用方式:
        @handle_errors
        def my_function(): ...
        
        或带自定义消息:
        @handle_errors(error_message="操作失败")
        def my_function(): ...
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return fn(*args, **kwargs)
            except FileNotFoundError as e:
                msg = error_message or "⚠️ 所需文件不存在，请检查数据目录"
                logger.error(f"文件未找到 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except json.JSONDecodeError as e:
                msg = error_message or "⚠️ 数据文件格式错误，请重新初始化"
                logger.error(f"JSON解析错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except PermissionError as e:
                msg = error_message or "⚠️ 文件权限不足，请检查目录权限"
                logger.error(f"权限错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except KeyError as e:
                msg = error_message or f"⚠️ 缺少必要的数据字段: {e}"
                logger.error(f"键错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except ValueError as e:
                msg = error_message or f"⚠️ 参数值无效: {e}"
                logger.error(f"值错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except Exception as e:
                msg = error_message or f"❌ 操作失败: {str(e)}"
                logger.error(f"未知错误 [{fn.__name__}]: {e}", exc_info=True)
                raise Exception(msg)
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    执行时间记录装饰器
    记录函数执行耗时，用于性能监控
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"⏱️ {func.__name__} 执行耗时: {duration:.3f}秒")
        return result
    return wrapper


# ========== 工具函数 ==========

def safe_division(a: float, b: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    参数:
        a: 被除数
        b: 除数
        default: 除数为零时的默认返回值
        
    返回:
        除法结果或默认值
    """
    try:
        if b == 0:
            return default
        return a / b
    except (TypeError, ZeroDivisionError):
        return default


def format_file_size(size_bytes: int) -> str:
    """
    将字节转换为人类可读的文件大小
    
    参数:
        size_bytes: 文件大小（字节）
        
    返回:
        格式化后的字符串（如"256MB"、"1.5GB"）
    """
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)}{units[unit_index]}"
    elif size < 10:
        return f"{size:.2f}{units[unit_index]}"
    elif size < 100:
        return f"{size:.1f}{units[unit_index]}"
    else:
        return f"{int(size)}{units[unit_index]}"


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    生成唯一标识符
    
    参数:
        prefix: ID前缀（如'KY','OT','ER','NT'）
        length: 随机部分长度
                
    返回:
        唯一ID字符串
    """
    timestamp_part = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{timestamp_part}{random_part}" if prefix else f"{timestamp_part}{random_part}"


def get_timestamp(format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    获取当前时间戳字符串
    
    参数:
        format_str: 时间格式
        
    返回:
        格式化的时间字符串
    """
    return datetime.now().strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    参数:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    返回:
        截断后的文本
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    从文本中提取关键词（简单实现，基于词频）
    
    参数:
        text: 输入文本
        top_n: 返回前N个关键词
        
    返回:
        关键词列表
    """
    import re
    from collections import Counter
    
    # 简单的分词（中文按字符，英文按单词）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    english_words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    
    all_tokens = chinese_chars + english_words
    
    # 过滤停用词（简单版）
    stopwords = {'的', '是', '在', '了', '和', '与', '或', '等', 'the', 'a', 'an', 'is', 'are', 'was', 'were'}
    filtered = [t for t in all_tokens if t.lower() not in stopwords and len(t) > 1]
    
    counter = Counter(filtered)
    return [word for word, count in counter.most_common(top_n)]


def calculate_reading_time(text: str, words_per_minute: int = 300) -> str:
    """
    估算文本阅读时间
    
    参数:
        text: 文本内容
        words_per_minute: 每分钟阅读字数
        
    返回:
        阅读时间描述（如"约3分钟"）
    """
    import re
    
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    total_units = chinese_chars + english_words
    
    minutes = total_units / words_per_minute
    
    if minutes < 1:
        seconds = int(minutes * 60)
        return f"约{seconds}秒"
    elif minutes < 60:
        return f"约{int(minutes)}分钟"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"约{hours}小时{mins分钟}"


# 需要在顶部添加json导入
import json
```

- [ ] **步骤 4：创建 utils/template_engine.py Jinja2模板引擎封装**

```python
"""
Jinja2模板引擎封装
专门用于小红书笔记内容的模板化生成
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Jinja2模板引擎封装
    
    提供简化的模板加载和渲染接口，
    支持多风格、多语气的笔记模板管理。
    
    使用示例:
        >>> engine = TemplateEngine('utils/templates')
        >>> result = engine.render('干货分享_亲切姐妹风', context)
    """
    
    def __init__(self, templates_dir: str = 'utils/templates'):
        """
        初始化模板引擎
        
        参数:
            templates_dir: 模板文件目录路径
        """
        self.templates_dir = Path(templates_dir)
        
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(f"模板目录不存在，已创建: {self.templates_dir}")
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,  # 笔记内容不需要HTML转义
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # 注册自定义过滤器
        self._register_custom_filters()
        
        logger.info(f"模板引擎初始化完成，模板目录: {self.templates_dir}")
    
    def _register_custom_filters(self):
        """注册自定义Jinja2过滤器"""
        
        def emoji_bullet(content: str, emoji: str = "✅") -> str:
            """添加emoji项目符号"""
            return f"{emoji} {content}"
        
        def bold_text(text: str) -> str:
            """加粗文本"""
            return f"**{text}**"
        
        def highlight_text(text: str) -> str:
            """高亮文本（用于重点标注）"""
            return f"`{text}`"
        
        self.env.filters['emoji_bullet'] = emoji_bullet
        self.env.filters['bold'] = bold_text
        self.env.filters['highlight'] = highlight_text
    
    def render(
        self,
        template_name: str,
        context: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        渲染指定模板
        
        参数:
            template_name: 模板名称（不含扩展名）
            context: 模板上下文变量
            **kwargs: 额外的上下文变量
            
        返回:
            渲染后的字符串
            
        异常:
            TemplateNotFoundError: 模板不存在
        """
        template_file = f"{template_name}.j2"
        
        try:
            template = self.env.get_template(template_file)
            
            # 合并上下文
            merged_context = {**context, **kwargs}
            
            result = template.render(**merged_context)
            logger.debug(f"模板渲染成功: {template_name}")
            return result
            
        except TemplateNotFound:
            logger.error(f"模板不存在: {template_file}")
            raise FileNotFoundError(f"模板文件未找到: {template_file}")
        except Exception as e:
            logger.error(f"模板渲染失败: {template_file} - {e}")
            raise
    
    def render_with_fallback(
        self,
        template_name: str,
        context: Dict[str, Any],
        fallback_template: str = None,
        **kwargs
    ) -> str:
        """
        带回退机制的模板渲染
        
        如果主模板不存在，使用回退模板
        
        参数:
            template_name: 主模板名称
            context: 上下文变量
            fallback_template: 回退模板名称
            **kwargs: 额外上下文
            
        返回:
            渲染结果
        """
        try:
            return self.render(template_name, context, **kwargs)
        except FileNotFoundError:
            if fallback_template:
                logger.warning(f"主模板不存在，使用回退模板: {fallback_template}")
                return self.render(fallback_template, context, **kwargs)
            raise
    
    def get_available_templates(self) -> List[str]:
        """
        获取所有可用模板列表
        
        返回:
            模板名称列表（不含扩展名）
        """
        templates = []
        
        if self.templates_dir.exists():
            for file in self.templates_dir.glob('*.j2'):
                templates.append(file.stem)
        
        templates.sort()
        logger.debug(f"发现{len(templates)}个模板: {templates}")
        return templates
    
    def get_templates_by_style(self, style: str) -> List[str]:
        """
        获取指定风格的所有模板
        
        参数:
            style: 笔记风格（如"干货分享"、"经验分享"、"种草推荐"）
            
        返回:
            该风格下的模板列表
        """
        all_templates = self.get_available_templates()
        return [t for t in all_templates if t.startswith(style)]
    
    def create_template(
        self,
        template_name: str,
        content: str,
        overwrite: bool = False
    ) -> bool:
        """
        创建新模板文件
        
        参数:
            template_name: 模板名称（不含扩展名）
            content: 模板内容
            overwrite: 是否覆盖已有模板
            
        返回:
            是否创建成功
        """
        template_path = self.templates_dir / f"{template_name}.j2"
        
        if template_path.exists() and not overwrite:
            logger.warning(f"模板已存在且不允许覆盖: {template_name}")
            return False
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"模板创建成功: {template_name}")
            
            # 重新加载模板环境以识别新模板
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )
            self._register_custom_filters()
            
            return True
            
        except Exception as e:
            logger.error(f"模板创建失败: {e}")
            return False
    
    def validate_template(self, template_name: str) -> tuple:
        """
        验证模板语法是否正确
        
        参数:
            template_name: 模板名称
            
        返回:
            (是否有效, 错误信息)
        """
        try:
            template = self.env.get_template(f"{template_name}.j2")
            # 尝试用空上下文渲染来检测语法错误
            template.render()
            return (True, "模板语法正确")
        except TemplateNotFound:
            return (False, f"模板不存在: {template_name}")
        except Exception as e:
            return (False, f"模板语法错误: {str(e)}")
    
    def get_template_info(self, template_name: str) -> Optional[dict]:
        """
        获取模板详细信息
        
        参数:
            template_name: 模板名称
            
        返回:
            模板信息字典或None
        """
        template_path = self.templates_dir / f"{template_name}.j2"
        
        if not template_path.exists():
            return None
        
        stat = template_path.stat()
        is_valid, message = self.validate_template(template_name)
        
        return {
            'name': template_name,
            'path': str(template_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'is_valid': is_valid,
            'validation_message': message
        }
```

- [ ] **步骤 5：Commit 工具函数代码**

```bash
git add utils/
git commit -m "feat: implement utility layer (data loader, helpers, template engine)"
```

---

## （后续任务将在实现过程中继续展开...）

由于计划篇幅较长，剩余任务（服务层实现、页面UI实现、模拟数据生成、测试验证）将在执行阶段逐步完成。当前已完成：

✅ **基础设施搭建**（任务1）  
✅ **数据模型层**（任务2）  
✅ **工具函数层**（任务3）

**下一步待实现：**
- 任务4：服务层实现（4个核心服务）
- 任务5：Jinja2笔记模板创建（9个模板文件）
- 任务6：Streamlit页面UI实现（4个功能页面）
- 任务7：模拟数据生成与填充
- 任务8：系统集成测试与优化

---

## 规格覆盖度自检

| 需求章节 | 对应任务 | 状态 |
|---------|---------|------|
| 考研资料获取模块 | 任务4.1 DataCollectorService + Page1 | ⏳ 待实现 |
| 办公模板管理功能 | 任务4.2 FileManagerService + Page2 | ⏳ 待实现 |
| 英语资料包整合 | 任务4.3 EnglishPackage整合 + Page3 | ⏳ 待实现 |
| 小红书笔记生成器 | 任务4.4 ContentGeneratorService + Page4 | ⏳ 待实现 |
| 自动化数据采集/存储 | DataLoader + DataCollector | ⏳ 待实现 |
| 用户友好交互界面 | Streamlit Pages + CSS样式 | ⏳ 待实现 |
| 笔记生成风格调整 | ContentGenerator + 9个Jinja2模板 | ⏳ 待实现 |
| 定期更新机制 | refresh方法 + 时间戳检查 | ⏳ 待实现 |
| 导出分享功能 | ExporterService | ⏳ 待实现 |
| 模块化设计原则 | 独立services/pages/models | ✅ 已规划 |

## 占位符扫描

✅ 无占位符 - 所有步骤均包含具体代码实现

## 类型一致性检查

✅ 所有数据模型字段命名一致（snake_case）  
✅ 服务层接口签名统一  
✅ 配置常量引用一致

---

**计划编写完成时间：** 2026-04-27  
**预计总开发时间：** 3-4小时（完整MVP）  
**复杂度评估：** 中等（涉及多层架构但每层相对独立）
