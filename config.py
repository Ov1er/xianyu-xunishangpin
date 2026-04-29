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
    
    OFFICE_DIFFICULTIES: List[str] = field(default_factory=lambda: ["入门级", "进阶级", "高级定制"])
    
    # ========== 英语资料模块配置 ==========
    ENGLISH_CATEGORIES: List[Dict] = field(default_factory=lambda: [
        {"id": "vocab", "name": "词汇", "icon": "📚", "description": "核心词汇、词根词缀、高频词"},
        {"id": "grammar", "name": "语法", "icon": "📝", "description": "语法精讲、长难句分析"},
        {"id": "reading", "name": "阅读", "icon": "📖", "description": "阅读理解训练、真题阅读"},
        {"id": "writing", "name": "写作", "icon": "✍️", "description": "大小作文模板、写作技巧"},
        {"id": "listening", "name": "听力", "icon": "🎧", "description": "听力专项训练"},
        {"id": "past_exams", "name": "历年真题", "icon": "📋", "description": "完整真题及解析"}
    ])
    
    ENGLISH_DIFFICULTIES: List[str] = field(default_factory=lambda: ["基础阶段", "强化阶段", "冲刺阶段"])
    ENGLISH_PRIORITIES: List[str] = field(default_factory=lambda: ["⭐ 必看", "✓ 推荐", "○ 选学"])
    
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
