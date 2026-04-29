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
