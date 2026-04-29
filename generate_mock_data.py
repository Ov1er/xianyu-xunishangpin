"""
模拟数据生成器
用于生成系统所需的测试数据（考研资料、办公模板、英语资源）
"""

import sys
import io

# 设置stdout编码为UTF-8（解决Windows控制台中文显示问题）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


class MockDataGenerator:
    """模拟数据生成器"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 预定义的数据池
        self.kaoyan_subjects = ["政治", "英语", "数学一", "数学二", "数学三", "专业课"]
        self.kaoyan_types = ["历年真题", "考试大纲", "复习指南", "学霸笔记", "模拟试题"]
        self.kaoyan_statuses = ["最新发布", "热门推荐", "编辑精选", "经典必备"]
        
        self.office_categories = ["PPT模板", "Word模板", "Excel模板", "简历模板", "合同范本", "报告模板"]
        self.office_subcategories = {
            "PPT模板": ["工作汇报", "年终总结", "项目答辩", "培训课件"],
            "Word模板": ["求职简历", "合同协议", "公文写作"],
            "Excel模板": ["财务报表", "项目管理", "数据分析"],
            "简历模板": ["应届生", "社招", "实习"],
            "合同范本": ["租赁合同", "劳务合同", "合作协议"],
            "报告模板": ["调研报告", "分析报告", "总结报告"]
        }
        
        self.english_categories = [
            {"id": "vocab", "name": "词汇", "icon": "📚"},
            {"id": "grammar", "name": "语法", "icon": "📝"},
            {"id": "reading", "name": "阅读", "icon": "📖"},
            {"id": "writing", "name": "写作", "icon": "✍️"},
            {"id": "listening", "name": "听力", "icon": "🎧"},
            {"id": "past_exams", "name": "历年真题", "icon": "📋"}
        ]
    
    def generate_id(self, prefix: str) -> str:
        """生成唯一ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        return f"{prefix}{timestamp}{random_part}"
    
    def generate_kaoyan_data(self, count: int = 128) -> dict:
        """生成考研资料模拟数据"""
        materials = []
        
        titles_pool = {
            "政治": [
                "2026考研政治全套资料（真题+解析+思维导图）",
                "肖秀荣1000题详细解答与知识点梳理",
                "考研政治核心考点背诵手册",
                "政治选择题技巧大全",
                "分析题答题模板与高分范例",
                "时政热点汇总与命题预测",
                "马原重点章节精讲",
                "史纲时间线与事件对照表"
            ],
            "英语": [
                "2026考研英语一历年真题及详解",
                "考研英语核心词汇5500（乱序版）",
                "长难句分析与语法精讲",
                "阅读理解满分攻略",
                "写作万能模板（大作文+小作文）",
                "翻译技巧与真题演练",
                "完形填空专项训练",
                "新题型解题方法"
            ],
            "数学一": [
                "2026数学一历年真题试卷集",
                "高等数学复习全书（强化版）",
                "线性代数核心考点总结",
                "概率论与数理统计精要",
                "数学一660题刷题本",
                "公式定理速查手册",
                "易错题整理与分析",
                "冲刺阶段模拟卷（8套）"
            ],
            "数学二": [
                "2026数学二真题分类汇编",
                "考研数学二复习指南",
                "高数基础过关1000题",
                "线代30天突破计划",
                "概率论快速入门教程",
                "数学二常考题型归纳",
                "计算能力强化训练",
                "考前押题卷（5套）"
            ],
            "数学三": [
                "2026数学三全科复习资料包",
                "经济类联考数学备考攻略",
                "微积分在经济学中的应用",
                "数学三真题深度解析",
                "线性代数经济学案例",
                "概率论统计模型精讲",
                "数学三冲刺预测卷",
                "公式记忆口诀大全"
            ],
            "专业课": [
                "408计算机学科专业基础综合",
                "管理学原理核心笔记",
                "教育学311考点全覆盖",
                "法律硕士(非法学)备考指南",
                "心理学347知识框架图",
                "西医综合复习资料包",
                "新闻传播学理论精编",
                "金融学431复习全书"
            ]
        }
        
        descriptions_pool = [
            "包含最新的考试大纲解读和命题趋势分析，帮助考生把握复习方向。",
            "汇集了历年高频考点，配有详细解析和记忆技巧，提高复习效率。",
            "由名师团队精心编写，内容全面系统，适合各阶段考生使用。",
            "基于大数据分析，提炼出最可能考到的知识点，针对性极强。",
            "配套视频讲解，扫码即可观看，学习更加便捷高效。",
            "采用思维导图形式呈现，逻辑清晰，便于理解和记忆。"
        ]
        
        for i in range(count):
            subject = random.choice(self.kaoyan_subjects)
            year = random.choice([2026, 2025, 2024, 2023])
            mat_type = random.choice(self.kaoyan_types)
            
            title_options = titles_pool.get(subject, ["通用" + subject + "备考资料"])
            title = random.choice(title_options)
            
            file_sizes = [f"{random.randint(10, 500)}MB", f"{random.randint(1, 20)}GB"]
            file_formats = ["PDF", "ZIP", "WORD", "RAR"]
            
            tags_base = [subject, str(year), mat_type]
            extra_tags_list = [
                ["肖秀荣", "张宇", "汤家凤", "李永乐"],
                ["真题", "模拟", "冲刺", "基础"],
                ["必背", "核心", "高频", "重点"],
                ["2026最新", "电子版", "可打印", "高清"]
            ]
            extra_tags = random.sample(extra_tags_list, k=2)
            
            material = {
                "id": self.generate_id("KY"),
                "title": title,
                "subject": subject,
                "year": year,
                "material_type": mat_type,
                "description": random.choice(descriptions_pool),
                "file_path": f"files/kaoyan/{subject}/{year}/material_{i}.zip",
                "file_size": random.choice(file_sizes),
                "file_format": random.choice(file_formats),
                "download_count": random.randint(50, 15000),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "tags": tags_base + list(extra_tags),
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "source": "simulated"
            }
            materials.append(material)
        
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": count,
                "source": "simulated"
            },
            "materials": materials
        }
    
    def generate_office_data(self, count: int = 256) -> dict:
        """生成办公模板模拟数据"""
        templates = []
        
        names_pool = {
            "PPT模板": [
                    "年度工作汇报PPT模板（商务风格）",
                    "年终总结暨新年计划演示文稿",
                    "项目答辩/开题报告PPT模板",
                    "企业培训课件设计模板",
                    "商业计划书BP路演模板",
                    "产品发布会PPT设计稿",
                    "季度销售数据分析报告",
                    "公司介绍/企业文化展示"
            ],
            "Word模板": [
                        "应届生求职简历模板（简洁风）",
                        "资深职场人简历模板（经验导向）",
                        "英文CV/Resume模板（外企适用）",
                        "房屋租赁合同标准范本",
                        "劳动合同书（完整版）",
                        "保密协议与竞业限制条款",
                        "技术服务合同协议",
                        "合作协议书（多方签署）"
            ],
            "Excel模板": [
                            "财务报表自动化模板（含公式）",
                            "项目管理进度跟踪表",
                            "库存管理系统（自动计算）",
                            "员工考勤与薪资核算表",
                            "客户关系管理CRM表格",
                            "数据分析仪表板Dashboard",
                            "预算编制与执行监控表",
                            "固定资产管理台账"
            ],
            "简历模板": [
                        "互联网大厂校招简历模板",
                        "公务员/事业单位报考简历",
                        "留学生归国求职简历",
                        "转行跳槽简历（突出迁移能力）",
                        "设计/创意类岗位作品集简历",
                        "技术岗项目经历详述型简历",
                        "管培生/储备干部申请简历",
                        "实习经历丰富型简历"
            ],
            "合同范本": [
                            "房屋租赁合同（房东版）",
                            "房屋租赁合同（租客版）",
                            "兼职/实习劳务协议",
                            "技术服务外包合同",
                            "联合开发合作协议",
                            "股权投资协议书",
                            "品牌授权经销合同",
                            "软件许可使用协议"
            ],
            "报告模板": [
                        "市场调研分析报告模板",
                        "用户研究报告（UX方向）",
                        "竞品分析对比报告格式",
                        "项目验收报告文档",
                        "离职/交接工作报告",
                        "周报/月报工作汇报模板",
                        "可行性研究报告框架",
                        "事故/问题调查分析报告"
            ]
        }
        
        for i in range(count):
            category = random.choice(self.office_categories)
            subcategories = self.office_subcategories.get(category, [])
            subcategory = random.choice(subcategories) if subcategories else ""
            
            name_options = names_pool.get(category, [f"{category}通用模板"])
            name = random.choice(name_options)
            
            difficulties = ["入门级", "进阶级", "高级定制"]
            weights = [0.4, 0.4, 0.2]
            difficulty = random.choices(difficulties, weights=weights, k=1)[0]
            
            template = {
                "id": self.generate_id("OT"),
                "name": name,
                "category": category,
                "subcategory": subcategory,
                "description": f"适用于{subcategory}场景的专业{category}，包含完整的结构框架和示例内容，可直接编辑使用。",
                "preview_image": f"assets/previews/template_{i}.png",
                "file_path": f"files/templates/{category}/{name}.pptx",
                "file_format": ".pptx" if category == "PPT模板" else (".docx" if category in ["Word模板", "简历模板", "合同范本", "报告模板"] else ".xlsx"),
                "file_size": f"{random.randint(1, 15)}MB",
                "tags": [category, subcategory, difficulty, "实用", "高质量"] if random.random() > 0.3 else [category, subcategory],
                "difficulty": difficulty,
                "download_count": random.randint(100, 20000),
                "rating": round(random.uniform(4.2, 5.0), 1),
                "is_premium": random.random() > 0.7,
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            }
            templates.append(template)
        
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": count
            },
            "templates": templates
        }
    
    def generate_english_data(self, resource_count: int = 156) -> dict:
        """生成英语资源模拟数据"""
        resources = []
        
        resource_names = {
            "vocab": [
                    "2026考研英语核心词汇5500词（乱序版）",
                    "词根词缀记忆法完全手册",
                    "高频词汇速记表（按频率排序）",
                    "真题词汇统计报告（2015-2025）",
                    "词汇默写本（英译中+中译英）",
                    "恋练有词：考研词汇视频课程",
                    "红宝书考研英语词汇（精缩版）",
                    "朱伟恋恋有词5500词"
            ],
            "grammar": [
                        "考研英语语法精讲（长难句分析）",
                        "语法体系框架图（思维导图版）",
                        "从句法到篇章：语法进阶教程",
                        "常见语法错误纠正手册",
                        "虚拟语气专项突破",
                        "倒装句式与强调句型",
                        "定语从句全解（限制性vs非限制性）",
                        "名词性从句实战应用"
            ],
            "reading": [
                        "阅读理解A节真题训练200篇",
                        "阅读理解B节新题型攻略",
                        "阅读速度提升训练计划",
                        "主旨大意题解题技巧",
                        "细节事实题定位方法",
                        "推理判断题逻辑链",
                        "态度观点题识别标志",
                        "例证题与篇章结构分析"
            ],
            "writing": [
                        "大作文万能模板（社会热点类）",
                        "大作文万能模板（个人品质类）",
                        "小作文（应用文）模板合集",
                        "写作常用高级词汇替换表",
                        "经典句型与连接词大全",
                        "图表作文描述模板",
                        "书信类应用文格式规范",
                        "写作常见错误与修正指南"
            ],
            "listening": [
                        "听力专项训练（对话部分）",
                        "听力专项训练（短文部分）",
                        "听力填空题技巧与练习",
                        "BBC新闻听力素材库",
                        "VOA慢速英语听力合集",
                        "雅思/托福听力迁移训练",
                        "听力场景词汇分类记忆",
                        "数字与拼写敏感度训练"
            ],
            "past_exams": [
                            "2015-2025年英语一真题及解析",
                            "2015-2025年英语二真题及解析",
                            "近十年阅读理解真题分类汇编",
                            "翻译真题（英译汉+汉译英）合集",
                            "写作真题范文与评分标准",
                            "完形填空真题深度解析",
                            "新题型真题演练（摘要/翻译）",
                            "真题词汇复现率统计分析"
            ]
        }
        
        for cat_info in self.english_categories:
            cat_id = cat_info["id"]
            cat_name = cat_info["name"]
            
            # 每个类别生成约26个资源
            num_resources = resource_count // len(self.english_categories)
            
            names = resource_names.get(cat_id, [f"{cat_name}资源{i}" for i in range(num_resources)])
            
            for i in range(min(num_resources, len(names))):
                name = names[i] if i < len(names) else f"{cat_name}进阶资料{i}"
                
                difficulties = ["基础阶段", "强化阶段", "冲刺阶段"]
                priorities = ["⭐ 必看", "✓ 推荐", "○ 选学"]
                
                resource = {
                    "id": self.generate_id("ER"),
                    "package_name": "2026考研英语全套资料",
                    "category": cat_id,
                    "title": name,
                    "description": f"针对{cat_name}的专项学习资料，包含详细的讲解、练习和答案解析，帮助考生系统性提升{cat_name}能力。",
                    "file_path": f"files/english/{cat_id}/{name.replace(' ', '_')}.pdf",
                    "file_size": f"{random.randint(5, 80)}MB",
                    "file_format": "PDF",
                    "difficulty": random.choice(difficulties),
                    "priority": random.choice(priorities),
                    "study_hours": random.choice([0, 5, 10, 15, 20, 30]),
                    "related_resources": []
                }
                resources.append(resource)
        
        package_config = {
            "package_name": "2026考研英语全套资料",
            "version": "2026.1",
            "total_size": "2.3GB",
            "total_files": len(resources),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": "包含词汇、语法、阅读、写作、听力、真题等全方位资源，助力考研英语取得理想成绩",
            "categories": self.english_categories
        }
        
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": len(resources)
            },
            "resources": resources,
            "package_config": package_config
        }
    
    def generate_notes_data(self, count: int = 89) -> dict:
        """生成笔记记录模拟数据"""
        notes = []
        
        styles = ["干货分享", "经验分享", "种草推荐"]
        tones = ["亲切姐妹风", "专业导师风", "幽默吐槽风"]
        
        sample_titles = [
            "考研政治从40分到80分，我只用了这份资料！💯",
            "吐血整理！考研英语最完整资料，建议收藏",
            "别再花冤枉钱了！这个资源真的绝绝子🥳",
            "挖到宝了！这个办公神器谁懂啊😭",
            "谁懂啊！居然可以这么简单搞定PPT",
            "按头安利！这个资料包太好用了❤️‍🔥",
            "真香预警！让我效率提升300%✨",
            "我不允许还有人不知道这个！！📢"
        ]
        
        sample_tags = [
            "#考研", "#考研资料", "#2026考研", "#干货分享",
            "#好物推荐", "#办公室生存指南", "#PPT模板",
            "#英语学习", "#学习方法", "#建议收藏",
            "#真香警告", "#宝藏资源", "#避坑指南"
        ]
        
        for i in range(count):
            note = {
                "note_id": self.generate_id("NT"),
                "version": random.randint(1, 3),
                "title": random.choice(sample_titles) if random.random() > 0.3 else f"第{i}篇笔记标题",
                "body": "这是一条生成的笔记正文内容..." * random.randint(5, 20),
                "tags": random.sample(sample_tags, k=random.randint(5, 12)),
                "image_suggestions": [
                    "封面图：使用醒目的大标题+渐变背景色",
                    "内页图：展示资料的目录或效果预览",
                    "结尾图：引导关注或联系方式"
                ],
                "source_content_id": self.generate_id("KY"),
                "source_content_type": random.choice(["kaoyan", "office", "english"]),
                "style": random.choice(styles),
                "tone": random.choice(tones),
                "target_audience": random.sample(
                    ["考研党", "大学生", "职场新人", "宝妈群体"], 
                    k=random.randint(1, 3)
                ),
                "char_count": random.randint(300, 1200),
                "emoji_count": random.randint(10, 35),
                "created_at": (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                "metadata": {}
            }
            notes.append(note)
        
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_count": count
            },
            "notes": notes
        }
    
    def generate_all(self):
        """生成所有模拟数据"""
        print("=" * 50)
        print("开始生成模拟数据...")
        print("=" * 50)
        
        # 生成考研数据
        print("\n[1/4] 生成考研资料数据...")
        kaoyan_data = self.generate_kaoyan_data(128)
        with open(self.data_dir / "kaoyan_data.json", 'w', encoding='utf-8') as f:
            json.dump(kaoyan_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 考研资料: {len(kaoyan_data['materials'])} 条")
        
        # 生成办公模板数据
        print("[2/4] 生成办公模板数据...")
        office_data = self.generate_office_data(256)
        with open(self.data_dir / "office_data.json", 'w', encoding='utf-8') as f:
            json.dump(office_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 办公模板: {len(office_data['templates'])} 条")
        
        # 生成英语资料数据
        print("[3/4] 生成英语资料数据...")
        english_data = self.generate_english_data(156)
        with open(self.data_dir / "english_data.json", 'w', encoding='utf-8') as f:
            json.dump(english_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 英语资源: {len(english_data['resources'])} 条")
        
        # 生成笔记数据
        print("[4/4] 生成笔记记录数据...")
        notes_data = self.generate_notes_data(89)
        with open(self.data_dir / "notes_data.json", 'w', encoding='utf-8') as f:
            json.dump(notes_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 笔记记录: {len(notes_data['notes'])} 条")
        
        print("\n" + "=" * 50)
        print("✅ 所有模拟数据生成完成！")
        print("=" * 50)
        print(f"\n总数据量:")
        print(f"  - 考研资料: {len(kaoyan_data['materials'])} 条")
        print(f"  - 办公模板: {len(office_data['templates'])} 条")
        print(f"  - 英语资源: {len(english_data['resources'])} 条")
        print(f"  - 笔记记录: {len(notes_data['notes'])} 条")
        print(f"\n数据目录: {self.data_dir.absolute()}")
        print("=" * 50)


if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.generate_all()
