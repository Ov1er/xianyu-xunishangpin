"""
内容生成服务模块
小红书笔记智能生成引擎（基于模板化方法）
"""

import random
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils.template_engine import TemplateEngine
from utils.helpers import generate_unique_id, get_timestamp, extract_keywords, log_execution_time
from config import config

logger = logging.getLogger(__name__)


class ContentGeneratorService:
    """
    小红书笔记内容生成服务
    
    基于模板化方法生成符合小红书平台风格的内容，
    支持多种风格、语气和目标受众的灵活组合。
    """
    
    def __init__(self):
        """初始化内容生成服务"""
        self.template_engine = TemplateEngine(config.TEMPLATES_DIR)
        logger.info("内容生成服务初始化完成")
    
    @log_execution_time
    def generate_xiaohongshu_note(
        self,
        source_content: Dict[str, Any],
        style: str = "干货分享",
        tone: str = "亲切姐妹风",
        target_audience: List[str] = None,
        title_length: str = "medium",
        num_versions: int = 1
    ) -> List[Dict[str, Any]]:
        """
        生成小红书推广笔记
        
        参数:
            source_content: 来源资料信息字典
                {
                    'title': '资料标题',
                    'description': '描述',
                    'category': '分类',
                    'tags': ['标签1', '标签2'],
                    'key_points': ['要点1', '要点2'],
                    'benefit': '核心价值'
                }
            style: 笔记风格 ('干货分享' | '经验分享' | '种草推荐')
            tone: 语气调性 ('亲切姐妹风' | '专业导师风' | '幽默吐槽风')
            target_audience: 目标受众列表
            title_length: 标题长度偏好 ('short' | 'medium' | 'long')
            num_versions: 生成版本数 (1-3)
            
        返回:
            生成的笔记列表，每个元素包含：
            {
                'version': int,
                'title': str,
                'body': str,
                'tags': List[str],
                'image_suggestions': List[str],
                'metadata': dict
            }
        """
        results = []
        
        # 默认目标受众
        if not target_audience:
            target_audience = ["考研党", "大学生"]
        
        for version_num in range(num_versions):
            try:
                # 1. 生成标题
                title = self._generate_title(
                    source_content, style, title_length, version_num
                )
                
                # 2. 生成正文（使用Jinja2模板）
                body = self._generate_body(
                    source_content, style, tone, target_audience
                )
                
                # 3. 推荐标签
                tags = self._recommend_tags(
                    source_content, style, target_audience
                )
                
                # 4. 配图建议
                image_suggestions = self._suggest_images(
                    source_content, style
                )
                
                # 统计元数据
                char_count = len(body)
                emoji_count = self._count_emojis(body)
                
                note = {
                    'note_id': generate_unique_id('NT'),
                    'version': version_num + 1,
                    'title': title,
                    'body': body,
                    'tags': tags,
                    'image_suggestions': image_suggestions,
                    'source_content_id': source_content.get('id', ''),
                    'source_content_type': source_content.get('type', ''),
                    'style': style,
                    'tone': tone,
                    'target_audience': target_audience,
                    'char_count': char_count,
                    'emoji_count': emoji_count,
                    'created_at': get_timestamp(),
                    'metadata': {
                        'generation_method': 'template',
                        'template_used': f"{style}_{tone}",
                        'word_count': self._estimate_word_count(body)
                    }
                }
                
                results.append(note)
                logger.debug(f"笔记版本{version_num + 1}生成完成")
                
            except Exception as e:
                logger.error(f"生成笔记版本{version_num + 1}失败: {e}")
                continue
        
        return results
    
    def _generate_title(
        self,
        content: Dict[str, Any],
        style: str,
        length: str,
        version: int
    ) -> str:
        """
        生成吸引人的标题
        
        从预定义的标题模板库中随机选择并填充变量
        """
        # 获取对应风格的模板列表
        style_key = self._map_style_to_key(style)
        templates = config.TITLE_TEMPLATES.get(style_key, [])
        
        if not templates:
            templates = ["{topic}推荐！{benefit}✨"]
        
        # 根据版本号选择不同模板（避免重复）
        template_index = (version * 7) % len(templates)
        template = templates[template_index]
        
        # 准备变量值
        topic = content.get('title', '优质资料')
        benefit = content.get('benefit', '超实用')
        target = random.choice(['考研人', '大学生', '职场新人', '姐妹们'])
        number = random.choice([3, 5, 7, 10])
        start = random.choice(['0', '小白', '迷茫'])
        end = random.choice(['大神', '高手', '轻松搞定'])
        goal = content.get('benefit', '高效学习').replace('超', '')
        
        # 填充模板
        title = template.format(
            topic=topic[:20],  # 截断过长的主题
            benefit=benefit[:15],
            target=target,
            number=number,
            start=start,
            end=end,
            goal=goal
        )
        
        # 确保标题长度合适
        max_lengths = {'short': 15, 'medium': 25, 'long': 35}
        max_len = max_lengths.get(length, 25)
        
        if len(title) > max_len:
            title = title[:max_len-3] + "..."
        
        return title
    
    def _generate_body(
        self,
        content: Dict[str, Any],
        style: str,
        tone: str,
        audience: List[str]
    ) -> str:
        """
        使用Jinja2模板渲染正文

        尝试使用对应的风格+语气组合模板，
        如果不存在则使用回退逻辑生成。
        """
        # 将ID转换为中文模板名
        template_name = self._resolve_template_name(style, tone)

        # 准备模板上下文
        context = self._prepare_template_context(content, style, tone, audience)

        try:
            # 尝试从模板文件渲染
            body = self.template_engine.render(template_name, context)
            return body
            
        except FileNotFoundError:
            # 模板不存在，使用内置回退逻辑
            logger.info(f"模板[{template_name}]不存在，使用内置生成")
            return self._fallback_generate_body(content, style, tone, audience)

    def _resolve_template_name(self, style: str, tone: str) -> str:
        """
        将风格和语气ID转换为中文模板文件名

        支持两种格式：
        - ID格式：ganhuo_qinjie -> 干货分享_亲切姐妹风
        - 中文格式：干货分享_亲切姐妹风（直接返回）
        """
        # 风格ID到中文名称的映射
        style_map = {
            'ganhuo': '干货分享',
            'jingyan': '经验分享',
            'zhongcao': '种草推荐'
        }

        # 语气ID到中文名称的映射
        tone_map = {
            'qinjie': '亲切姐妹风',
            'zhuanye': '专业导师风',
            'youmo': '幽默吐槽风'
        }

        # 如果已经是中文格式，直接返回
        if style in style_map.values() or tone in tone_map.values():
            return f"{style}_{tone}"

        # 转换ID为中文
        style_cn = style_map.get(style, style)
        tone_cn = tone_map.get(tone, tone)

        return f"{style_cn}_{tone_cn}"

    def _prepare_template_context(
        self,
        content: Dict[str, Any],
        style: str,
        tone: str,
        audience: List[str]
    ) -> Dict[str, Any]:
        """准备模板渲染所需的上下文变量"""
        
        # 提取关键要点
        key_points = content.get('key_points', [])
        if not key_points:
            key_points = self._extract_key_points_from_description(content.get('description', ''))
        
        # 格式化要点列表（用于模板中的循环）
        formatted_points = []
        for i, point in enumerate(key_points[:6], 1):  # 最多6个要点
            formatted_points.append({
                'index': i,
                'text': point,
                'emoji': random.choice(['✅', '📌', '💡', '⭐', '🎯', '🔥'])
            })
        
        context = {
            # 内容相关
            'title': content.get('title', ''),
            'description': content.get('description', ''),
            'category': content.get('category', ''),
            'benefit': content.get('benefit', '超实用'),
            
            # 要点列表
            'key_points': key_points,
            'formatted_points': formatted_points,
            'points_count': len(formatted_points),
            
            # 受众相关
            'audience': audience,
            'audience_str': '、'.join(audience[:3]),
            'primary_audience': audience[0] if audience else '大家',
            
            # 风格和语气
            'style': style,
            'tone': tone,
            
            # 时间相关
            'current_date': datetime.now().strftime('%Y年%m月'),
            'greeting': self._get_greeting_by_tone(tone),
            
            # 随机元素（增加变化）
            'random_emoji': random.choice(['🔥', '💖', '✨', '🎉', '💪', '🚀']),
            'emphasis_word': random.choice(['真的', '超级', '绝对', '必须', '一定']),
        }
        
        return context
    
    def _fallback_generate_body(
        self,
        content: Dict[str, Any],
        style: str,
        tone: str,
        audience: List[str]
    ) -> str:
        """
        内置的正文生成回退逻辑
        当Jinja2模板不可用时使用
        """
        
        # 获取关键要点
        key_points = content.get('key_points', [])
        if not key_points:
            key_points = self._extract_key_points_from_description(content.get('description', ''))
        
        # 根据语气选择开头和结尾
        openings = {
            '亲切姐妹风': f"家人们！今天要给你们分享一个宝藏{content.get('category', '资源')}！",
            '专业导师风': f"在{content.get('category', '该领域')}深耕多年，我整理了这份核心资料。",
            '幽默吐槽风': f"说实话，这个{content.get('category', '东西')}真的让我惊呆了😂"
        }
        
        closings = {
            '亲切姐妹风': f"需要的{audience[0] if audience else '姐妹们'}记得{random.choice(['点赞收藏', '关注我', '评论区扣1'])}哦~ ❤️",
            '专业导师风': "希望这份资料能帮助你少走弯路，高效达成目标。",
            '幽默吐槽风': "别犹豫了，冲就完事了！🏃‍♀️💨"
        }
        
        # 构建正文
        lines = [
            openings.get(tone, openings['亲切姐妹风']),
            "",
            f"📦 **{content.get('title', '精选资料')}**",
            "",
        ]
        
        # 添加要点
        if key_points:
            lines.append("✅ **包含内容：**")
            for point in key_points[:8]:  # 最多8个要点
                emoji = random.choice(['✓', '★', '●', '▸'])
                lines.append(f"{emoji} {point}")
            lines.append("")
        
        # 添加价值说明
        benefit = content.get('benefit', '')
        if benefit:
            value_templates = {
                '亲切姐妹风': f"💡 **为什么推荐？**\n{benefit}，亲测好用！",
                '专业导师风': f"**核心价值：**\n{benefit}",
                '幽默吐槽风': f"**划重点：**\n{benefit}（这波不亏！）"
            }
            lines.append(value_templates.get(tone, value_templates['亲切姐妹风']))
            lines.append("")
        
        # 添加行动号召
        cta_templates = {
            '亲切姐妹风': f"👇 **获取方式**\n看主页/评论区，或者直接滴滴我~",
            '专业导师风': "**下一步：**\n立即开始使用，让效率提升200%。",
            '幽默吐槽风': "**还等什么？**\n早用早享受，晚用悔断肠！"
        }
        lines.append(cta_templates.get(tone, cta_templates['亲切姐妹风']))
        lines.append("")
        lines.append(closings.get(tone, closings['亲切姐妹风']))
        
        return "\n".join(lines)
    
    def _recommend_tags(
        self,
        content: Dict[str, Any],
        style: str,
        audience: List[str]
    ) -> List[str]:
        """
        智能推荐话题标签
        
        基于内容匹配热门标签库 + 添加通用标签
        """
        tags = []
        
        # 1. 从内容中提取关键词作为标签
        content_text = f"{content.get('title', '')} {content.get('description', '')}"
        keywords = extract_keywords(content_text, top_n=5)
        tags.extend([f"#{kw}" for kw in keywords[:3]])
        
        # 2. 根据分类匹配热门标签
        category = content.get('category', '').lower()
        category_tag_map = {
            '考研': '考研',
            '办公': '办公',
            '英语': '英语',
            '政治': '考研',
            '数学': '考研',
            'ppt': '办公',
            'word': '办公',
            'excel': '办公',
            '简历': '职场',
            '词汇': '英语',
            '语法': '英语',
            '阅读': '英语',
            '写作': '英语'
        }
        
        mapped_category = None
        for key, value in category_tag_map.items():
            if key in category:
                mapped_category = value
                break
        
        if mapped_category and mapped_category in config.HOT_TAGS:
            hot_tags_for_category = config.HOT_TAGS[mapped_category][:3]
            tags.extend(hot_tags_for_category)
        
        # 3. 添加通用热门标签
        universal_tags = config.HOT_TAGS.get('通用', [])[:2]
        tags.extend(universal_tags)
        
        # 4. 添加风格相关标签
        style_tags = {
            '干货分享': ['#干货分享', '#建议收藏'],
            '经验分享': ['#真实经历', '#避坑指南'],
            '种草推荐': ['#好物推荐', '#宝藏资源']
        }
        tags.extend(style_tags.get(style, ['#干货分享']))
        
        # 5. 去重并限制数量
        unique_tags = list(dict.fromkeys(tags))  # 保持顺序的去重
        final_tags = unique_tags[:12]  # 小红书通常12-20个标签
        
        logger.debug(f"推荐标签: {final_tags}")
        return final_tags
    
    def _suggest_images(
        self,
        content: Dict[str, Any],
        style: str
    ) -> List[str]:
        """
        根据内容类型给出配图建议
        """
        suggestions = []
        category = content.get('category', '').lower()
        title = content.get('title', '')
        
        # 基础建议（适用于所有类型）
        base_suggestions = [
            f"封面图：使用醒目的大标题「{title[:10]}...」+ 渐变背景色",
            "内页图1：展示资料的目录结构或内容截图",
            "内页图2：展示部分实际内容或效果预览"
        ]
        suggestions.extend(base_suggestions)
        
        # 根据类别的特定建议
        if any(kw in category for kw in ['考研', '考试', '学习']):
            suggestions.extend([
                "加分项：添加「使用前后对比」图",
                "加分项：展示学习计划表或思维导图"
            ])
        elif any(kw in category for kw in ['办公', 'ppt', 'word', 'excel']):
            suggestions.extend([
                "加分项：展示模板的实际应用效果图",
                "加分项：制作「Before/After」对比图"
            ])
        elif any(kw in category for kw in ['英语', '语言']):
            suggestions.extend([
                "加分项：单词量统计图表或进度追踪图",
                "加分项：学习方法流程图"
            ])
        
        # 结尾建议
        ending_suggestions = [
            "结尾图：引导关注的二维码或联系方式",
            "结尾图：「点赞+收藏」提示卡片"
        ]
        suggestions.extend(ending_suggestions)
        
        return suggestions[:8]  # 限制数量
    
    # ========== 辅助方法 ==========
    
    @staticmethod
    def _map_style_to_key(style: str) -> str:
        """将中文风格映射到配置键名"""
        mapping = {
            '干货分享': 'ganhuo',
            '经验分享': 'jingyan',
            '种草推荐': 'zhongcao'
        }
        return mapping.get(style, 'ganhuo')
    
    @staticmethod
    def _get_greeting_by_tone(tone: str) -> str:
        """根据语气返回合适的问候语"""
        greetings = {
            '亲切姐妹风': '哈喽姐妹们～',
            '专业导师风': '你好，',
            '幽默吐槽风': '嘿，朋友们！'
        }
        return greetings.get(tone, '哈喽～')
    
    @staticmethod
    def _extract_key_points_from_description(description: str, max_points: int = 5) -> List[str]:
        """从描述文本中提取关键要点"""
        if not description:
            return [""]
        
        # 按句号、分号、换行分割
        separators = ['。', '；', ';', '\n', '|', ',']
        points = []
        current = ""
        
        for char in description:
            current += char
            if char in separators:
                point = current.strip()
                if len(point) > 5:  # 过滤太短的片段
                    points.append(point)
                current = ""
        
        # 添加最后一个片段
        if current.strip():
            points.append(current.strip())
        
        return points[:max_points] if points else [description[:50]]
    
    @staticmethod
    def _count_emojis(text: str) -> int:
        """统计文本中的emoji数量"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # map & transport
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        
        return len(emoji_pattern.findall(text))
    
    @staticmethod
    def _estimate_word_count(text: str) -> int:
        """估算字数（中英文混合）"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    # ========== 公共接口方法 ==========
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """获取所有可用的笔记风格配置"""
        return config.NOTE_STYLES
    
    def get_available_tones(self) -> List[Dict[str, str]]:
        """获取所有可用的语气调性配置"""
        return config.NOTE_TONES
    
    def get_available_audiences(self) -> List[str]:
        """获取所有可选的目标受众"""
        return config.NOTE_TARGET_AUDIENCES
    
    def validate_generation_params(
        self,
        style: str,
        tone: str,
        num_versions: int
    ) -> tuple:
        """
        验证生成参数的有效性
        
        返回:
            (is_valid: bool, message: str)
        """
        valid_styles = [s['name'] for s in config.NOTE_STYLES]
        valid_tones = [t['name'] for t in config.NOTE_TONES]
        
        if style not in valid_styles:
            return (False, f"无效的风格: {style}，可选: {valid_styles}")
        
        if tone not in valid_tones:
            return (False, f"无效的语气: {tone}，可选: {valid_tones}")
        
        if not 1 <= num_versions <= 3:
            return (False, "版本数必须在1-3之间")
        
        return (True, "参数验证通过")
