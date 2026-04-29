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
        source_content_type: 来源资料类型（kaoyan/office/english）
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
            f"- 生成于：{self.created_time.strftime('%Y-%m-%d %H:%M')}"
        ]
        return "\n".join(md_lines)
