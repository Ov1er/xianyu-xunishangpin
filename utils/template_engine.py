"""
Jinja2模板引擎封装
专门用于小红书笔记内容的模板化生成
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Jinja2模板引擎封装
    
    提供简化的模板加载和渲染接口，
    支持多风格、多语气的笔记模板管理。
    
    使用示例:
        >>> engine = TemplateEngine('utils/templates')
        >>> result = engine.render('干货分享_亲切姐妹风', context)
    """
    
    def __init__(self, templates_dir: str = 'utils/templates'):
        """
        初始化模板引擎
        
        参数:
            templates_dir: 模板文件目录路径
        """
        self.templates_dir = Path(templates_dir)
        
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(f"模板目录不存在，已创建: {self.templates_dir}")
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # 注册自定义过滤器
        self._register_custom_filters()
        
        logger.info(f"模板引擎初始化完成，模板目录: {self.templates_dir}")
    
    def _register_custom_filters(self):
        """注册自定义Jinja2过滤器"""
        
        def emoji_bullet(content: str, emoji: str = "✅") -> str:
            """添加emoji项目符号"""
            return f"{emoji} {content}"
        
        def bold_text(text: str) -> str:
            """加粗文本"""
            return f"**{text}**"
        
        def highlight_text(text: str) -> str:
            """高亮文本（用于重点标注）"""
            return f"`{text}`"
        
        self.env.filters['emoji_bullet'] = emoji_bullet
        self.env.filters['bold'] = bold_text
        self.env.filters['highlight'] = highlight_text
    
    def render(
        self,
        template_name: str,
        context: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        渲染指定模板
        
        参数:
            template_name: 模板名称（不含扩展名）
            context: 模板上下文变量
            **kwargs: 额外的上下文变量
            
        返回:
            渲染后的字符串
            
        异常:
            TemplateNotFoundError: 模板不存在
        """
        template_file = f"{template_name}.j2"
        
        try:
            template = self.env.get_template(template_file)
            
            # 合并上下文
            merged_context = {**context, **kwargs}
            
            result = template.render(**merged_context)
            logger.debug(f"模板渲染成功: {template_name}")
            return result
            
        except TemplateNotFound:
            logger.error(f"模板不存在: {template_file}")
            raise FileNotFoundError(f"模板文件未找到: {template_file}")
        except Exception as e:
            logger.error(f"模板渲染失败: {template_file} - {e}")
            raise
    
    def render_with_fallback(
        self,
        template_name: str,
        context: Dict[str, Any],
        fallback_template: str = None,
        **kwargs
    ) -> str:
        """
        带回退机制的模板渲染
        
        如果主模板不存在，使用回退模板
        """
        try:
            return self.render(template_name, context, **kwargs)
        except FileNotFoundError:
            if fallback_template:
                logger.warning(f"主模板不存在，使用回退模板: {fallback_template}")
                return self.render(fallback_template, context, **kwargs)
            raise
    
    def get_available_templates(self) -> List[str]:
        """
        获取所有可用模板列表
        
        返回:
            模板名称列表（不含扩展名）
        """
        templates = []
        
        if self.templates_dir.exists():
            for file in self.templates_dir.glob('*.j2'):
                templates.append(file.stem)
        
        templates.sort()
        logger.debug(f"发现{len(templates)}个模板: {templates}")
        return templates
    
    def get_templates_by_style(self, style: str) -> List[str]:
        """
        获取指定风格的所有模板
        
        参数:
            style: 笔记风格（如"干货分享"、"经验分享"、"种草推荐"）
            
        返回:
            该风格下的模板列表
        """
        all_templates = self.get_available_templates()
        return [t for t in all_templates if t.startswith(style)]
    
    def create_template(
        self,
        template_name: str,
        content: str,
        overwrite: bool = False
    ) -> bool:
        """
        创建新模板文件
        """
        template_path = self.templates_dir / f"{template_name}.j2"
        
        if template_path.exists() and not overwrite:
            logger.warning(f"模板已存在且不允许覆盖: {template_name}")
            return False
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"模板创建成功: {template_name}")
            
            # 重新加载模板环境以识别新模板
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )
            self._register_custom_filters()
            
            return True
            
        except Exception as e:
            logger.error(f"模板创建失败: {e}")
            return False
    
    def validate_template(self, template_name: str) -> tuple:
        """
        验证模板语法是否正确
        """
        try:
            template = self.env.get_template(f"{template_name}.j2")
            template.render()
            return (True, "模板语法正确")
        except TemplateNotFound:
            return (False, f"模板不存在: {template_name}")
        except Exception as e:
            return (False, f"模板语法错误: {str(e)}")
    
    def get_template_info(self, template_name: str) -> Optional[dict]:
        """
        获取模板详细信息
        """
        template_path = self.templates_dir / f"{template_name}.j2"
        
        if not template_path.exists():
            return None
        
        stat = template_path.stat()
        is_valid, message = self.validate_template(template_name)
        
        return {
            'name': template_name,
            'path': str(template_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'is_valid': is_valid,
            'validation_message': message
        }
