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
