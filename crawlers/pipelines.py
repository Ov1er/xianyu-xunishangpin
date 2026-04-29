"""
数据处理管道
负责数据去重、验证、标准化、元数据补充
"""

import re
from datetime import datetime
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class DataPipeline:
    
    def __init__(self, data_type: str = ""):
        self.data_type = data_type
        self.data_key = self._get_data_key(data_type)
        self.stats = {
            'input_count': 0,
            'after_dedup': 0,
            'after_validation': 0,
            'output_count': 0
        }
    
    def _get_data_key(self, data_type: str) -> str:
        mapping = {
            'kaoyan': 'materials',
            'office': 'templates',
            'english': 'resources',
            'notes': 'notes'
        }
        return mapping.get(data_type, 'items')
    
    def process(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not raw_data:
            logger.warning("[Pipeline] 输入数据为空")
            return self._empty_result()
        
        self.stats['input_count'] = len(raw_data)
        logger.info(f"[Pipeline-{self.data_type}] 开始处理 {len(raw_data)} 条数据...")
        
        deduped = self.deduplicate(raw_data)
        self.stats['after_dedup'] = len(deduped)
        logger.info(f"  去重后: {len(deduped)} 条")
        
        standardized = self.standardize(deduped)
        validated = self.validate(standardized)
        self.stats['after_validation'] = len(validated)
        logger.info(f"  验证后: {len(validated)} 条")
        
        enriched = self.enrich_metadata(validated)
        result = self._build_output(enriched)
        self.stats['output_count'] = len(enriched)
        
        logger.info(f"[Pipeline-{self.data_type}] 处理完成: "
                   f"{self.stats['input_count']} → {self.stats['output_count']} 条")
        return result
    
    def deduplicate(self, data: List[Dict]) -> List[Dict]:
        seen_keys = set()
        unique_data = []
        for item in data:
            title = str(item.get('title', '')).strip().lower()
            url = str(item.get('source_url', '') or item.get('url', '')).strip()
            if not title:
                continue
            key = f"{title}|{url}"
            if key not in seen_keys:
                seen_keys.add(key)
                unique_data.append(item)
        removed = len(data) - len(unique_data)
        if removed > 0:
            logger.info(f"  去除重复: {removed} 条")
        return unique_data
    
    def standardize(self, data: List[Dict]) -> List[Dict]:
        standardized = []
        for item in data:
            std_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    value = value.strip()
                    value = re.sub(r'\s+', ' ', value)
                std_item[key] = value
            std_item = self._standardize_special_fields(std_item)
            standardized.append(std_item)
        return standardized
    
    def _standardize_special_fields(self, item: Dict) -> Dict:
        if not item.get('title'):
            item['title'] = '(未命名)'
        
        tags = item.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        item['tags'] = tags
        
        year = item.get('year')
        if year is not None:
            try:
                item['year'] = int(year)
            except (ValueError, TypeError):
                del item['year']
        
        rating = item.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
                item['rating'] = max(0.0, min(5.0, rating))
            except (ValueError, TypeError):
                del item['rating']
        
        return item
    
    def validate(self, data: List[Dict]) -> List[Dict]:
        validated = []
        invalid_count = 0
        required_fields = ['id', 'title']
        
        for item in data:
            missing = [f for f in required_fields if not item.get(f)]
            if missing:
                invalid_count += 1
                continue
            
            title = item.get('title', '')
            if len(title) < 2 or len(title) > 500:
                invalid_count += 1
                continue
            
            validated.append(item)
        
        if invalid_count > 0:
            logger.warning(f"  无效数据: {invalid_count} 条")
        return validated
    
    def enrich_metadata(self, data: List[Dict]) -> List[Dict]:
        enriched = []
        now = datetime.now().isoformat()
        
        for i, item in enumerate(data):
            enriched_item = dict(item)
            
            if not enriched_item.get('id'):
                import hashlib
                ts = datetime.now().strftime('%Y%m%d%H%M%S')
                h = hashlib.md5(f"{item['title']}{time.time()}".encode()).hexdigest()[:8]
                enriched_item['id'] = f"{self.data_type.upper()}_{ts}_{h}"
            
            if not enriched_item.get('crawl_time'):
                enriched_item['crawl_time'] = now
            
            if not enriched_item.get('source'):
                enriched_item['source'] = f"crawler_{self.data_type}"
            
            enriched_item['_index'] = i + 1
            enriched.append(enriched_item)
        
        return enriched
    
    def _build_output(self, data: List[Dict]) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            'metadata': {
                'version': '2.0.0',
                'last_updated': now,
                'total_count': len(data),
                'source': 'crawler',
                'pipeline_stats': self.stats.copy(),
                'data_type': self.data_type
            },
            self.data_key: data
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        return {
            'metadata': {
                'version': '2.0.0',
                'last_updated': datetime.now().isoformat(),
                'total_count': 0,
                'source': 'crawler',
                'data_type': self.data_type
            },
            self.data_key: []
        }
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()


import time
