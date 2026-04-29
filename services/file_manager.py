"""
文件管理服务模块
处理文件的存储、预览、下载和打包操作
"""

import os
import zipfile
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

from utils.helpers import format_file_size, log_execution_time
from config import config

logger = logging.getLogger(__name__)


class FileManagementService:
    """
    文件管理服务
    
    负责处理系统中所有文件的存储、预览、下载等操作。
    """
    
    def __init__(self):
        """初始化文件管理服务"""
        self.base_dir = Path(config.FILES_DIR)
        self._ensure_directories()
        logger.info("文件管理服务初始化完成")
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            'templates',
            'english',
            'exports',
            'generated'
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @log_execution_time
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件详细信息
        
        参数:
            file_path: 文件路径（相对或绝对）
            
        返回:
            文件信息字典
        """
        try:
            # 处理相对路径
            if not os.path.isabs(file_path):
                full_path = self.base_dir / file_path
            else:
                full_path = Path(file_path)
            
            if not full_path.exists():
                return {
                    'exists': False,
                    'name': os.path.basename(file_path),
                    'error': '文件不存在'
                }
            
            stat = full_path.stat()
            
            return {
                'exists': True,
                'name': full_path.name,
                'path': str(full_path),
                'size': stat.st_size,
                'size_formatted': format_file_size(stat.st_size),
                'format': full_path.suffix.lower(),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_file': full_path.is_file(),
                'is_dir': full_path.is_dir()
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return {'exists': False, 'error': str(e)}
    
    @log_execution_time
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        if not os.path.isabs(file_path):
            full_path = self.base_dir / file_path
        else:
            full_path = Path(file_path)
        
        return full_path.exists()
    
    @log_execution_time
    def list_files_in_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        列出目录下的所有文件
        
        参数:
            directory: 目录路径（相对于base_dir）
            extensions: 文件扩展名过滤（如['.pdf', '.docx']）
            recursive: 是否递归子目录
            
        返回:
            文件信息列表
        """
        try:
            dir_path = self.base_dir / directory
            
            if not dir_path.exists():
                logger.warning(f"目录不存在: {dir_path}")
                return []
            
            files = []
            
            if recursive:
                pattern = '**/*'
            else:
                pattern = '*'
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    # 扩展名过滤
                    if extensions:
                        if file_path.suffix.lower() not in extensions:
                            continue
                    
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path.relative_to(self.base_dir)),
                        'size': file_path.stat().st_size,
                        'size_formatted': format_file_size(file_path.stat().st_size),
                        'format': file_path.suffix.lower(),
                        'modified': file_path.stat().st_mtime
                    })
            
            # 按名称排序
            files.sort(key=lambda x: x['name'])
            
            logger.debug(f"列出目录[{directory}]完成，文件数: {len(files)}")
            return files
            
        except Exception as e:
            logger.error(f"列出目录失败: {e}")
            return []
    
    @log_execution_time
    def create_export_package(
        self,
        file_paths: List[str],
        package_name: str = "export",
        format: str = "zip"
    ) -> str:
        """
        创建导出包（打包多个文件）
        
        参数:
            file_paths: 要打包的文件路径列表
            package_name: 包名称
            format: 打包格式 ('zip' | 'tar')
            
        返回:
            打包后的文件路径
        """
        try:
            exports_dir = self.base_dir / 'exports'
            exports_dir.mkdir(exist_ok=True)
            
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format == "zip":
                package_filename = f"{package_name}_{timestamp}.zip"
                package_path = exports_dir / package_filename
                
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in file_paths:
                        if not os.path.isabs(file_path):
                            full_path = self.base_dir / file_path
                        else:
                            full_path = Path(file_path)
                        
                        if full_path.exists():
                            zipf.write(full_path, full_path.name)
                            logger.debug(f"添加到压缩包: {full_path.name}")
                        else:
                            logger.warning(f"文件不存在，跳过: {file_path}")
                
                logger.info(f"导出包创建成功: {package_path}")
                return str(package_path)
                
            elif format == "tar":
                import tarfile
                
                package_filename = f"{package_name}_{timestamp}.tar.gz"
                package_path = exports_dir / package_filename
                
                with tarfile.open(package_path, 'w:gz') as tar:
                    for file_path in file_paths:
                        if not os.path.isabs(file_path):
                            full_path = self.base_dir / file_path
                        else:
                            full_path = Path(file_path)
                        
                        if full_path.exists():
                            tar.add(full_path, arcname=full_path.name)
                
                logger.info(f"导出包创建成功: {package_path}")
                return str(package_path)
                
            else:
                raise ValueError(f"不支持的打包格式: {format}")
                
        except Exception as e:
            logger.error(f"创建导出包失败: {e}")
            raise
    
    @log_execution_time
    def save_generated_content(
        self,
        content: str,
        filename: str,
        subfolder: str = "notes"
    ) -> str:
        """
        保存生成的内容到文件
        
        参数:
            content: 内容文本
            filename: 文件名
            subfolder: 子文件夹名称
            
        返回:
            保存后的完整路径
        """
        try:
            save_dir = self.base_dir / 'generated' / subfolder
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"内容保存成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存内容失败: {e}")
            raise
    
    @log_execution_time
    def get_directory_size(self, directory: str) -> Dict[str, Any]:
        """
        获取目录大小统计
        
        参数:
            directory: 目录路径
            
        返回:
            大小统计字典
        """
        try:
            dir_path = self.base_dir / directory
            
            if not dir_path.exists():
                return {'total_size': 0, 'total_files': 0}
            
            total_size = 0
            total_files = 0
            
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    total_files += 1
            
            return {
                'total_size': total_size,
                'total_size_formatted': format_file_size(total_size),
                'total_files': total_files
            }
            
        except Exception as e:
            logger.error(f"获取目录大小失败: {e}")
            return {'total_size': 0, 'total_files': 0}
    
    @log_execution_time
    def cleanup_old_exports(self, max_age_days: int = 7) -> int:
        """
        清理过期的导出文件
        
        参数:
            max_age_days: 最大保留天数
            
        返回:
            清理的文件数量
        """
        try:
            from datetime import datetime, timedelta
            
            exports_dir = self.base_dir / 'exports'
            cleaned_count = 0
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            for file_path in exports_dir.iterdir():
                if file_path.is_file():
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"清理过期文件: {file_path.name}")
            
            logger.info(f"清理完成，删除{cleaned_count}个过期文件")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期文件失败: {e}")
            return 0
