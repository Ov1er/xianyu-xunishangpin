"""
页面4：小红书笔记智能生成器 ⭐核心亮点模块
提供基于模板的小红书风格笔记自动生成功能
"""

import streamlit as st
import json
from services.data_collector import DataCollectorService
from services.content_generator import ContentGeneratorService
from services.exporter import ExporterService
from config import config

@st.cache_resource
def get_services():
    return {
        'data': DataCollectorService(),
        'generator': ContentGeneratorService(),
        'exporter': ExporterService()
    }

services = get_services()


def render_page():
    """渲染小红书笔记生成器页面"""
    st.title("✍️ 小红书笔记智能生成器")
    st.markdown("---")
    
    # ========== 第一步：选择素材来源 ==========
    st.markdown("### 📦 第一步：选择素材来源")
    
    source_type = st.radio(
        "选择资料类型",
        ["📚 考研资料", "📝 办公模板", "📖 英语资料包"],
        horizontal=True,
        key="source_type"
    )
    
    source_id = None
    source_content = None
    
    if "考研" in source_type:
        materials = services['data'].search_kaoyan_materials()[:20]  # 限制显示数量
        if materials:
            options = {m['id']: f"{m['title'][:30]}... ({m.get('subject', '')})" for m in materials}
            source_id = st.selectbox(
                "选择考研资料",
                options=list(options.keys()),
                format_func=lambda x: options[x],
                key="kaoyan_source"
            )
            if source_id:
                source_content = services['data'].get_kaoyan_by_id(source_id)
                if source_content:
                    source_content['type'] = 'kaoyan'
                    source_content['key_points'] = _extract_points_from_description(source_content.get('description', ''))
                    source_content['benefit'] = f"助力{source_content.get('subject', '')}备考，提升学习效率"
    
    elif "办公" in source_type:
        templates = services['data'].search_office_templates()[:20]
        if templates:
            options = {t['id']: f"{t['name']} ({t.get('category', '')})" for t in templates}
            source_id = st.selectbox(
                "选择办公模板",
                options=list(options.keys()),
                format_func=lambda x: options[x],
                key="office_source"
            )
            if source_id:
                source_content = next((t for t in templates if t['id'] == source_id), None)
                if source_content:
                    source_content['type'] = 'office'
                    source_content['key_points'] = [
                        f"包含{source_content.get('category', '')}相关内容",
                        f"适合{source_content.get('difficulty', '')}用户",
                        f"已帮助{source_content.get('download_count', 0):,}人"
                    ]
                    source_content['benefit'] = f"提升{source_content.get('category', '')}工作效率"
    
    elif "英语" in source_type:
        resources = services['data'].get_english_resources_by_category('vocab')[:10]
        resources += services['data'].get_english_resources_by_category('grammar')[:10]
        
        if resources:
            options = {r['id']: f"{r['title']} [{r.get('category', '')}]" for r in resources}
            source_id = st.selectbox(
                "选择英语资源",
                options=list(options.keys()),
                format_func=lambda x: options[x],
                key="english_source"
            )
            if source_id:
                source_content = services['data'].get_english_resource_detail(source_id)
                if source_content:
                    source_content['type'] = 'english'
                    source_content['key_points'] = [source_content.get('description', '')]
                    source_content['benefit'] = f"提升英语{source_content.get('category', '')}能力"
    
    # 显示选中的素材信息
    if source_content:
        with st.container(border=True):
            st.markdown("**📋 当前选中素材：**")
            st.write(f"- **标题：** {source_content.get('title', 'N/A')}")
            st.write(f"- **分类：** {source_content.get('category', source_content.get('subject', 'N/A'))}")
            
            desc = source_content.get('description', '')
            if desc and len(desc) > 100:
                desc = desc[:100] + "..."
            st.write(f"- **描述：** {desc}")
            
            points = source_content.get('key_points', [])
            if points:
                st.write(f"- **要点：** {' | '.join(points[:3])}")
    
    st.markdown("---")
    
    # ========== 第二步：生成风格设置 ==========
    st.markdown("### 🎨 第二步：生成风格设置")
    
    style_col1, style_col2, style_col3 = st.columns(3)
    
    with style_col1:
        st.markdown("**📝 笔记风格**")
        available_styles = services['generator'].get_available_styles()
        style_options = {s['id']: s['name'] for s in available_styles}
        
        selected_style = st.selectbox(
            "选择风格",
            options=list(style_options.keys()),
            format_func=lambda x: f"{style_options[x]} - {next((s['description'] for s in available_styles if s['id'] == x), '')}",
            index=0,
            key="note_style"
        )
        selected_style_name = style_options[selected_style]
    
    with style_col2:
        st.markdown("**😊 语气调性**")
        available_tones = services['generator'].get_available_tones()
        tone_options = {t['id']: t['name'] for t in available_tones}
        
        selected_tone = st.selectbox(
            "选择语气",
            options=list(tone_options.keys()),
            format_func=lambda x: f"{tone_options[x]} - {next((t['description'] for t in available_tones if t['id'] == x), '')}",
            index=0,
            key="note_tone"
        )
        selected_tone_name = tone_options[selected_tone]
    
    with style_col3:
        st.markdown("**👥 目标受众**")
        audiences = config.NOTE_TARGET_AUDIENCES
        
        selected_audiences = st.multiselect(
            "选择目标人群（可多选）",
            options=audiences,
            default=["考研党", "大学生"][:2],
            key="target_audience"
        )
    
    # 高级设置
    with st.expander("⚙️ 高级设置", expanded=False):
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            title_length = st.slider(
                "标题长度",
                min_value=1,
                max_value=3,
                value=2,
                format="%d (短/中/长)",
                help="短: 15字以内 | 中: 25字以内 | 长: 35字以内"
            )
            title_length_map = {1: "short", 2: "medium", 3: "long"}
        
        with adv_col2:
            num_versions = st.slider(
                "生成版本数",
                min_value=1,
                max_value=3,
                value=1,
                help="生成多个不同版本供选择"
            )
    
    st.markdown("---")
    
    # ========== 第三步：一键生成 ==========
    st.markdown("### ✨ 第三步：一键生成")
    
    gen_col1, gen_col2, gen_col3 = st.columns([2, 1, 1])
    
    with gen_col1:
        generate_btn = st.button(
            "🚀 生成笔记",
            use_container_width=True,
            type="primary",
            disabled=(not source_content)
        )
    
    with gen_col2:
        preview_mode = st.checkbox("实时预览模式", value=True, key="preview_mode")
    
    with gen_col3:
        auto_copy = st.checkbox("自动复制到剪贴板", value=False, key="auto_copy")
    
    # 执行生成
    generated_notes = []
    
    if generate_btn and source_content:
        # 参数验证
        is_valid, msg = services['generator'].validate_generation_params(
            selected_style_name,
            selected_tone_name,
            num_versions
        )
        
        if not is_valid:
            st.error(f"⚠️ 参数验证失败: {msg}")
            return
        
        with st.spinner(f"正在生成 {num_versions} 个版本的笔记..."):
            try:
                generated_notes = services['generator'].generate_xiaohongshu_note(
                    source_content=source_content,
                    style=selected_style_name,
                    tone=selected_tone_name,
                    target_audience=selected_audiences,
                    title_length=title_length_map[title_length],
                    num_versions=num_versions
                )
                
                st.success(f"✅ 成功生成 {len(generated_notes)} 篇笔记！")
                
            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
                return
    
    # ========== 结果展示区域 ==========
    if generated_notes:
        st.markdown("---")
        st.markdown(f"### 📝 生成结果（共 {len(generated_notes)} 版本）")
        
        for i, note in enumerate(generated_notes):
            version_num = note.get('version', i+1)
            
            with st.expander(f"📌 **版本 {version_num}:** {note.get('title', 'N/A')}", expanded=(i==0)):
                
                # 元数据展示
                meta_col1, meta_col2, meta_col3 = st.columns(3)
                with meta_col1:
                    st.caption(f"风格: {note.get('style', '-')} | 语气: {note.get('tone', '-')}")
                with meta_col2:
                    st.caption(f"字数: ~{note.get('char_count', 0)} | Emoji: {note.get('emoji_count', 0)}")
                with meta_col3:
                    st.caption(f"标签数: {len(note.get('tags', []))}")
                
                # 标题
                st.markdown(f"#### 📌 {note.get('title', 'N/A')}")
                
                # 正文内容
                body = note.get('body', '')
                if preview_mode:
                    st.text_area(
                        "正文预览（可编辑）",
                        value=body,
                        height=300,
                        key=f"body_preview_{i}"
                    )
                else:
                    st.markdown(body)
                
                # 标签
                tags = note.get('tags', [])
                if tags:
                    st.markdown("**🏷️ 推荐标签：**")
                    tag_str = " ".join(tags)
                    st.code(tag_str, language=None)
                
                # 配图建议
                image_suggestions = note.get('image_suggestions', [])
                if image_suggestions:
                    st.markdown("**🖼️ 配图建议：**")
                    for j, suggestion in enumerate(image_suggestions, 1):
                        st.write(f"  {j}. {suggestion}")
                
                # 操作按钮
                action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                
                with action_col1:
                    copy_text_btn = st.button(
                        "📋 复制文本",
                        key=f"copy_{i}",
                        use_container_width=True
                    )
                    if copy_text_btn:
                        shareable_text = services['exporter'].generate_shareable_text(note)
                        success = services['exporter'].copy_to_clipboard(shareable_text)
                        if success:
                            st.success("✅ 已复制到剪贴板！可直接粘贴到小红书")
                        else:
                            st.warning("⚠️ 复制失败，请手动复制")
                
                with action_col2:
                    export_txt_btn = st.button(
                        "💾 保存文本",
                        key=f"save_txt_{i}",
                        use_container_width=True
                    )
                    if export_txt_btn:
                        path = services['exporter'].export_note_to_text(note)
                        st.success(f"✅ 已保存: {path}")
                
                with action_col3:
                    export_md_btn = st.button(
                        "📄 导出Markdown",
                        key=f"save_md_{i}",
                        use_container_width=True
                    )
                    if export_md_btn:
                        path = services['exporter'].export_note_to_markdown(note)
                        st.success(f"✅ 已导出: {path}")
                
                with action_col4:
                    regenerate_btn = st.button(
                        "🔄 重新生成",
                        key=f"regen_{i}",
                        use_container_width=True
                    )
                    if regenerate_btn:
                        st.rerun()
        
        # 底部操作区
        st.markdown("---")
        st.markdown("### 🔧 批量操作")
        
        batch_col1, batch_col2, batch_col3 = st.columns(3)
        
        with batch_col1:
            export_all_btn = st.download_button(
                "📦 导出所有版本",
                data=json.dumps(generated_notes, ensure_ascii=False, indent=2),
                file_name="generated_notes.json",
                mime="application/json",
                use_container_width=True
            )
        
        with batch_col2:
            report_btn = st.button(
                "📊 生成报告",
                use_container_width=True
            )
            if report_btn:
                report_path = services['exporter'].create_summary_report(generated_notes)
                st.success(f"✅ 报告已生成: {report_path}")
        
        with batch_col3:
            if st.button("🗑️ 清空结果", use_container_width=True):
                generated_notes.clear()
                st.rerun()


def _extract_points_from_description(description: str, max_points: int = 5) -> list:
    """从描述中提取关键要点"""
    if not description:
        return [""]
    
    separators = ['。', '；', ';', '\n', '|']
    points = []
    current = ""
    
    for char in description:
        current += char
        if char in separators:
            point = current.strip()
            if len(point) > 5:
                points.append(point)
            current = ""
    
    if current.strip():
        points.append(current.strip())
    
    return points[:max_points] if points else [description[:50]]


if __name__ == "__main__":
    render_page()
