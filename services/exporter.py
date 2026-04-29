"""
导出分享服务模块
支持多种格式的数据导出和内容分享功能
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils.helpers import log_execution_time, get_timestamp
from services.file_manager import FileManagementService

logger = logging.getLogger(__name__)


class ExporterService:
    """
    导出分享服务
    
    提供多种格式的内容导出和数据分享功能。
    """
    
    def __init__(self):
        """初始化导出服务"""
        self.file_manager = FileManagementService()
        logger.info("导出服务初始化完成")
    
    @log_execution_time
    def export_note_to_text(
        self,
        note_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        导出笔记为纯文本格式
        
        参数:
            note_data: 笔记数据字典（GeneratedNote.to_dict()的结果）
            filename: 文件名（可选，默认自动生成）
            
        返回:
            保存后的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"note_{note_data.get('version', 1)}_{timestamp}.txt"
        
        # 构建文本内容
        lines = [
            "=" * 50,
            f"小红书笔记 v{note_data.get('version', 1)}",
            "=" * 50,
            "",
            "【标题】",
            note_data.get('title', ''),
            "",
            "【正文】",
            note_data.get('body', ''),
            "",
            "【标签】",
            " ".join(note_data.get('tags', [])),
            "",
            "【配图建议】",
        ]
        
        # 添加配图建议
        for i, suggestion in enumerate(note_data.get('image_suggestions', []), 1):
            lines.append(f"  {i}. {suggestion}")
        
        lines.extend([
            "",
            "-" * 50,
            "【生成信息】",
            f"- 风格: {note_data.get('style', '')}",
            f"- 语气: {note_data.get('tone', '')}",
            f"- 字数: ~{note_data.get('char_count', 0)}字",
            f"- Emoji数: {note_data.get('emoji_count', 0)}",
            f"- 生成时间: {note_data.get('created_at', '')}",
            "=" * 50
        ])
        
        content = "\n".join(lines)
        
        # 保存文件
        saved_path = self.file_manager.save_generated_content(
            content, filename, subfolder="notes"
        )
        
        logger.info(f"笔记导出为文本: {saved_path}")
        return saved_path
    
    @log_execution_time
    def export_note_to_markdown(
        self,
        note_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        导出笔记为Markdown格式
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"note_{note_data.get('version', 1)}_{timestamp}.md"
        
        md_lines = [
            f"# {note_data.get('title', '小红书笔记')}",
            "",
            note_data.get('body', '').replace('\n', '\n\n'),
            "",
            "---",
            "",
            "**标签：** " + " ".join(note_data.get('tags', [])),
            "",
            "**配图建议：**",
        ]
        
        for suggestion in note_data.get('image_suggestions', []):
            md_lines.append(f"- {suggestion}")
        
        metadata = note_data.get('metadata', {})
        md_lines.extend([
            "",
            "*生成信息*",
            f"- **风格：** {note_data.get('style', '')} | **语气：** {note_data.get('tone', '')}",
            f"- **字数：** 约{note_data.get('char_count', 0)}字 | **Emoji：** {note_data.get('emoji_count', 0)}",
            f"- **生成于：** {note_data.get('created_at', get_timestamp())[:10]}"
        ])
        
        content = "\n".join(md_lines)
        
        saved_path = self.file_manager.save_generated_content(
            content, filename, subfolder="notes"
        )
        
        logger.info(f"笔记导出为Markdown: {saved_path}")
        return saved_path
    
    @log_execution_time
    def export_notes_batch(
        self,
        notes: List[Dict[str, Any]],
        format: str = "text",
        package_name: str = "notes_batch"
    ) -> str:
        """
        批量导出多个笔记
        
        参数:
            notes: 笔记数据列表
            format: 导出格式 ('text' | 'markdown' | 'json')
            package_name: 包名称
            
        返回:
            打包后的文件路径
        """
        if not notes:
            raise ValueError("笔记列表不能为空")
        
        exported_files = []
        
        for note in notes:
            if format == 'text':
                path = self.export_note_to_text(note)
            elif format == 'markdown':
                path = self.export_note_to_markdown(note)
            elif format == 'json':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"note_{note.get('version', 1)}_{timestamp}.json"
                content = json.dumps(note, ensure_ascii=False, indent=2)
                path = self.file_manager.save_generated_content(content, filename)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            exported_files.append(path)
        
        # 创建压缩包
        package_path = self.file_manager.create_export_package(
            exported_files,
            package_name=package_name,
            format="zip"
        )
        
        logger.info(f"批量导出完成，共{len(notes)}个笔记，打包至: {package_path}")
        return package_path
    
    @log_execution_time
    def export_data_to_dataframe(
        self,
        data_type: str,
        data: List[Dict],
        format: str = "csv"
    ) -> str:
        """
        将数据导出为结构化文件（CSV/Excel）
        
        参数:
            data_type: 数据类型标识
            data: 数据列表
            format: 导出格式 ('csv' | 'excel' | 'json')
            
        返回:
            文件路径
        """
        import pandas as pd
        
        if not data:
            raise ValueError("数据列表不能为空")
        
        df = pd.DataFrame(data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            filename = f"{data_type}_export_{timestamp}.csv"
            content = df.to_csv(index=False, encoding='utf-8-sig')
        elif format == 'excel':
            filename = f"{data_type}_export_{timestamp}.xlsx"
            content = None  # Excel需要特殊处理
        elif format == 'json':
            filename = f"{data_type}_export_{timestamp}.json"
            content = df.to_json(orient='records', force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        if format == 'excel':
            filepath = self.file_manager.base_dir / 'exports' / filename
            df.to_excel(filepath, index=False, engine='openpyxl')
            return str(filepath)
        else:
            return self.file_manager.save_generated_content(
                content, filename, subfolder="exports"
            )
    
    @log_execution_time
    def copy_to_clipboard(self, text: str) -> bool:
        """
        复制文本到剪贴板（用于一键复制功能）
        
        参数:
            text: 要复制的文本
            
        返回:
            是否成功
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.debug("文本已复制到剪贴板")
            return True
        except Exception as e:
            logger.warning(f"复制到剪贴板失败: {e}")
            return False
    
    @log_execution_time
    def generate_shareable_text(
        self,
        note_data: Dict[str, Any]
    ) -> str:
        """
        生成可直接分享的文本（适合粘贴到小红书）
        
        格式：标题 + 正文 + 标签（符合小红书发布格式）
        """
        title = note_data.get('title', '')
        body = note_data.get('body', '')
        tags = " ".join(note_data.get('tags', []))
        
        shareable_text = f"{title}\n\n{body}\n\n{tags}"
        
        return shareable_text
    
    @log_execution_time
    def create_summary_report(
        self,
        generation_session: List[Dict[str, Any]]
    ) -> str:
        """
        创建生成会话的摘要报告
        
        参数:
            generation_session: 本次生成的所有笔记列表
            
        返回:
            报告文件路径
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_lines = [
            "# 小红书笔记生成报告",
            f"\n**生成时间：** {timestamp}",
            f"\n**生成数量：** {len(generation_session)} 篇",
            "",
            "## 生成统计",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 总篇数 | {len(generation_session)} |",
            f"| 平均字数 | {sum(n.get('char_count', 0) for n in generation_session) // max(len(generation_session), 1)} |",
            f"| 平均Emoji数 | {sum(n.get('emoji_count', 0) for n in generation_session) // max(len(generation_session), 1)} |",
            f"| 使用风格 | {', '.join(set(n.get('style', '') for n in generation_session))} |",
            f"| 使用语气 | {', '.join(set(n.get('tone', '') for n in generation_session))} |",
            "",
            "## 生成的笔记列表",
            ""
        ]
        
        for i, note in enumerate(generation_session, 1):
            report_lines.append(f"### 笔记 {i} (v{note.get('version', 1)})")
            report_lines.append(f"- **标题：** {note.get('title', 'N/A')}")
            report_lines.append(f"- **风格：** {note.get('style', 'N/A')} | **语气：** {note.get('tone', 'N/A')}")
            report_lines.append(f"- **字数：** ~{note.get('char_count', 0)}字 | **标签数：** {len(note.get('tags', []))}")
            report_lines.append("")
        
        report_lines.extend([
            "---",
            "*报告由闲鱼虚拟产品工作流系统自动生成*"
        ])
        
        report_content = "\n".join(report_lines)
        filename = f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_path = self.file_manager.save_generated_content(
            report_content, filename, subfolder="reports"
        )
        
        logger.info(f"生成报告已保存: {report_path}")
        return report_path
