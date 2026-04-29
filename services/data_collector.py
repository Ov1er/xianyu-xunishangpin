"""
数据采集服务模块
负责从各数据源获取和整理资料（当前为模拟数据采集）
"""

import logging
import random
from datetime import datetime
from typing import List, Optional, Dict, Any

import pandas as pd

from utils.data_loader import DataLoader
from utils.helpers import generate_unique_id, get_timestamp, log_execution_time
from config import config

logger = logging.getLogger(__name__)


class DataCollectorService:
    """
    数据采集服务
    
    负责从各数据源获取和整理资料，
    当前版本使用模拟数据，预留真实数据接口。
    """
    
    def __init__(self):
        """初始化数据采集服务"""
        self.data_loader = DataLoader()
        logger.info("数据采集服务初始化完成")
    
    # ========== 考研资料相关方法 ==========
    
    @log_execution_time
    def search_kaoyan_materials(
        self,
        keyword: str = "",
        subject: Optional[str] = None,
        year: Optional[int] = None,
        material_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索考研资料
        
        参数:
            keyword: 搜索关键词（在标题、描述、标签中搜索）
            subject: 科目筛选（政治/英语/数学等）
            year: 年份筛选（2026/2025等）
            material_type: 类型筛选（真题/大纲/指南等）
            status: 状态筛选（最新/热门/精选等）
            
        返回:
            匹配的资料列表（字典格式）
        """
        try:
            df = self.data_loader.load_as_dataframe('kaoyan', 'materials')
            
            if df.empty:
                return []
            
            # 应用筛选条件
            if keyword:
                mask = (
                    df['title'].str.contains(keyword, case=False, na=False) |
                    df['description'].str.contains(keyword, case=False, na=False) |
                    df['tags'].apply(lambda x: keyword.lower() in str(x).lower())
                )
                df = df[mask]
            
            if subject and subject in config.KAOYAN_SUBJECTS:
                df = df[df['subject'] == subject]
            
            if year and year in config.KAOYAN_YEARS:
                df = df[df['year'] == year]
            
            if material_type and material_type in config.KAOYAN_TYPES:
                df = df[df['material_type'] == material_type]
            
            logger.debug(f"考研资料搜索完成，结果数: {len(df)}")
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"搜索考研资料失败: {e}")
            return []
    
    @log_execution_time
    def get_kaoyan_by_id(self, material_id: str) -> Optional[Dict]:
        """
        根据ID获取单个考研资料详情
        
        参数:
            material_id: 资料ID
            
        返回:
            资料详情字典或None
        """
        try:
            data = self.data_loader.load('kaoyan')
            
            for material in data.get('materials', []):
                if material.get('id') == material_id:
                    return material
            
            logger.warning(f"未找到考研资料: ID={material_id}")
            return None
            
        except Exception as e:
            logger.error(f"获取考研资料失败: {e}")
            return None
    
    @log_execution_time
    def refresh_kaoyan_data(self) -> Dict[str, Any]:
        """
        刷新/更新考研资料数据（模拟定时采集）
        
        当前实现：模拟添加新数据或更新时间戳
        真实场景：调用爬虫/API获取最新数据
        
        返回:
            操作结果字典 {'success': bool, 'added': int, 'updated': int, 'message': str}
        """
        try:
            result = {
                'success': True,
                'added': 0,
                'updated': 0,
                'message': '数据刷新成功（模拟模式）',
                'timestamp': get_timestamp()
            }
            
            # 更新元数据中的最后更新时间
            data = self.data_loader.load('kaoyan')
            data['metadata']['last_updated'] = get_timestamp()
            self.data_loader.save('kaoyan', data)
            
            logger.info(f"考研数据刷新完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"刷新考研数据失败: {e}")
            return {
                'success': False,
                'added': 0,
                'updated': 0,
                'message': f'刷新失败: {str(e)}',
                'timestamp': get_timestamp()
            }
    
    @log_execution_time
    def get_kaoyan_statistics(self) -> Dict[str, Any]:
        """
        获取考研资料的统计信息
        
        返回:
            统计信息字典（按科目、年份、类型分布等）
        """
        try:
            df = self.data_loader.load_as_dataframe('kaoyan', 'materials')
            
            if df.empty:
                return {
                    'total': 0,
                    'by_subject': {},
                    'by_year': {},
                    'by_type': {},
                    'average_rating': 0,
                    'total_downloads': 0
                }
            
            stats = {
                'total': len(df),
                'by_subject': df['subject'].value_counts().to_dict(),
                'by_year': df['year'].value_counts().to_dict(),
                'by_type': df['material_type'].value_counts().to_dict(),
                'average_rating': round(df['rating'].mean(), 2),
                'total_downloads': int(df['download_count'].sum())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取考研统计失败: {e}")
            return {}
    
    # ========== 办公模板相关方法 ==========
    
    @log_execution_time
    def search_office_templates(
        self,
        keyword: str = "",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索办公模板
        """
        try:
            df = self.data_loader.load_as_dataframe('office', 'templates')
            
            if df.empty:
                return []
            
            # 关键词搜索
            if keyword:
                mask = (
                    df['name'].str.contains(keyword, case=False, na=False) |
                    df['description'].str.contains(keyword, case=False, na=False) |
                    df['tags'].apply(lambda x: keyword.lower() in str(x).lower()) |
                    df['category'].str.contains(keyword, case=False, na=False)
                )
                df = df[mask]
            
            # 分类筛选
            if category and category in config.OFFICE_CATEGORIES:
                df = df[df['category'] == category]
            
            # 难度筛选
            if difficulty and difficulty in config.OFFICE_DIFFICULTIES:
                df = df[df['difficulty'] == difficulty]
            
            # 标签筛选
            if tags:
                mask = df['tags'].apply(
                    lambda x: any(tag in str(x) for tag in tags)
                )
                df = df[mask]
            
            logger.debug(f"办公模板搜索完成，结果数: {len(df)}")
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"搜索办公模板失败: {e}")
            return []
    
    @log_execution_time
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """按分类获取模板列表"""
        return self.search_office_templates(category=category)
    
    @log_execution_time
    def get_hot_templates(self, limit: int = 10) -> List[Dict]:
        """
        获取热门模板（基于下载量排序）
        
        参数:
            limit: 返回数量限制
            
        返回:
            热门模板列表
        """
        try:
            df = self.data_loader.load_as_dataframe('office', 'templates')
            
            if df.empty:
                return []
            
            # 按下载量和评分综合排序
            df['score'] = df['download_count'] * 0.7 + df['rating'] * df['download_count'].max() * 0.3
            hot_df = df.nlargest(limit, 'score')
            
            return hot_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"获取热门模板失败: {e}")
            return []
    
    @log_execution_time
    def get_office_statistics(self) -> Dict[str, Any]:
        """获取办公模板的统计信息"""
        try:
            df = self.data_loader.load_as_dataframe('office', 'templates')
            
            if df.empty:
                return {'total': 0, 'by_category': {}, 'premium_count': 0}
            
            stats = {
                'total': len(df),
                'by_category': df['category'].value_counts().to_dict(),
                'premium_count': len(df[df['is_premium'] == True]),
                'average_rating': round(df['rating'].mean(), 2),
                'total_downloads': int(df['download_count'].sum())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取办公统计失败: {e}")
            return {}
    
    # ========== 英语资料相关方法 ==========
    
    @log_execution_time
    def get_english_package_info(self) -> Dict[str, Any]:
        """
        获取英语资料包的元信息（总览）
        
        返回:
            资料包配置字典
        """
        try:
            data = self.data_loader.load('english')
            package_config = data.get('package_config', {})
            
            # 如果没有配置，生成默认配置
            if not package_config:
                resources = data.get('resources', [])
                package_config = {
                    'package_name': '2026考研英语全套资料',
                    'version': '1.0',
                    'total_size': '2.3GB',
                    'total_files': len(resources),
                    'last_updated': get_timestamp(),
                    'description': '包含词汇、语法、阅读、写作、听力、真题等全方位资源'
                }
            
            return package_config
            
        except Exception as e:
            logger.error(f"获取英语资料包信息失败: {e}")
            return {}
    
    @log_execution_time
    def get_english_resources_by_category(
        self, category: str
    ) -> List[Dict]:
        """
        按类别获取英语资源列表
        
        参数:
            category: 类别标识（vocab/grammar/reading/writing/listening/past_exams）
            
        返回:
            该类别下的资源列表
        """
        try:
            data = self.data_loader.load('english')
            resources = data.get('resources', [])
            
            filtered = [r for r in resources if r.get('category') == category]
            
            logger.debug(f"英语资源[{category}]查询完成，数量: {len(filtered)}")
            return filtered
            
        except Exception as e:
            logger.error(f"获取英语资源失败: {e}")
            return []
    
    @log_execution_time
    def get_english_resource_detail(
        self, resource_id: str
    ) -> Optional[Dict]:
        """获取英语资源详情"""
        try:
            data = self.data_loader.load('english')
            
            for resource in data.get('resources', []):
                if resource.get('id') == resource_id:
                    return resource
            
            return None
            
        except Exception as e:
            logger.error(f"获取英语资源详情失败: {e}")
            return None
    
    # ========== 通用方法 ==========
    
    @log_execution_time
    def export_data(
        self,
        data_type: str,
        format: str = "json",
        filters: Optional[Dict] = None
    ) -> bytes:
        """
        导出数据为指定格式
        
        参数:
            data_type: 数据类型 ('kaoyan' | 'office' | 'english')
            format: 导出格式 ('json' | 'csv' | 'excel')
            filters: 筛选条件
            
        返回:
            文件字节数据
        """
        try:
            data_key = {
                'kaoyan': 'materials',
                'office': 'templates',
                'english': 'resources'
            }.get(data_type, '')
            
            df = self.data_loader.load_as_dataframe(data_type, data_key)
            
            if format == 'json':
                return df.to_json(orient='records', force_ascii=False).encode('utf-8')
            elif format == 'csv':
                return df.to_csv(index=False).encode('utf-8-sig')
            elif format == 'excel':
                return df.to_excel(engine='openpyxl', index=False)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
                
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            raise
    
    @log_execution_time
    def get_statistics(self, data_type: str) -> Dict[str, Any]:
        """获取指定数据类型的统计信息"""
        stats_map = {
            'kaoyan': self.get_kaoyan_statistics,
            'office': self.get_office_statistics,
            'english': self.get_english_package_info
        }
        
        func = stats_map.get(data_type)
        if func:
            return func()
        
        return self.data_loader.get_statistics(data_type)
