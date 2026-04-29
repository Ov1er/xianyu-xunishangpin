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
        file_path = self.data_dir / self.DATA_FILES[data_type].split('/')[-1]
        return file_path.exists()
    
    @staticmethod
    def _count_records(data: dict) -> int:
        """统计数据中的记录总数"""
        count = 0
        for key, value in data.items():
            if key != 'metadata' and isinstance(value, list):
                count += len(value)
        return count
