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
