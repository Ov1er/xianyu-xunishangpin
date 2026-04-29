"""
页面3：考研英语资料包整合模块
提供英语资料的分类浏览、详情查看和下载功能
"""

import streamlit as st
from services.data_collector import DataCollectorService
from config import config

@st.cache_resource
def get_data_service():
    return DataCollectorService()

service = get_data_service()


def render_page():
    """渲染英语资料包页面"""
    st.title("📖 考研英语资料包 v2026")
    st.markdown("---")
    
    # ========== 资料包总览 ==========
    package_info = service.get_english_package_info()
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 资料名称", package_info.get('package_name', '2026考研英语全套资料'))
        
        with col2:
            st.metric("📁 文件总数", package_info.get('total_files', 0))
        
        with col3:
            st.metric("💾 总大小", package_info.get('total_size', '0GB'))
        
        with col4:
            st.metric("🕐 最后更新", package_info.get('last_updated', '-')[:10])
    
    st.markdown(package_info.get('description', '包含词汇、语法、阅读、写作、听力、真题等全方位资源'))
    
    # 下载完整包按钮
    dl_col1, dl_col2 = st.columns([1, 1])
    
    with dl_col1:
        if st.button("⬇️ 下载完整资料包", use_container_width=True, type="primary"):
            st.success("✅ 已开始下载完整资料包（模拟）")
    
    with dl_col2:
        if st.button("📋 查看详细目录", use_container_width=True):
            st.info("请使用下方分类浏览查看详细内容")
    
    st.markdown("---")
    
    # ========== 分类导航 ==========
    st.markdown("### 🗂️ 分类浏览")
    
    categories = config.ENGLISH_CATEGORIES
    
    cat_cols = st.columns(len(categories))
    selected_category_id = None
    
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            icon = cat.get('icon', '📚')
            name = cat.get('name', '')
            desc = cat.get('description', '')
            
            btn_label = f"{icon} {name}"
            if st.button(btn_label, use_container_width=True, key=f"eng_cat_{i}"):
                selected_category_id = cat.get('id')
                st.rerun()
    
    # 显示当前选中的分类详情
    if selected_category_id:
        _render_category_detail(selected_category_id)
    else:
        # 默认显示第一个分类
        if categories:
            _render_category_detail(categories[0].get('id'))


def _render_category_detail(category_id: str):
    """渲染指定分类的资源列表"""
    
    # 获取分类信息
    category_info = next(
        (c for c in config.ENGLISH_CATEGORIES if c['id'] == category_id),
        None
    )
    
    if not category_info:
        st.error("未找到该分类信息")
        return
    
    icon = category_info.get('icon', '📚')
    name = category_info.get('name', '')
    desc = category_info.get('description', '')
    
    st.markdown(f"### {icon} {name}")
    st.caption(desc)
    
    # 获取该分类下的资源
    resources = service.get_english_resources_by_category(category_id)
    
    if not resources:
        st.info(f"😔 暂无「{name}」类资源")
        return
    
    st.markdown(f"**共 {len(resources)} 个资源**")
    
    # 资源列表展示
    for resource in resources:
        with st.container(border=True):
            res_col1, res_col2, res_col3 = st.columns([3, 1, 1])
            
            with res_col1:
                priority_icon = {
                    "⭐ 必看": "⭐",
                    "✓ 推荐": "✓",
                    "○ 选学": "○"
                }.get(resource.get('priority', '✓ 推荐'), "○")
                
                st.markdown(f"**{priority_icon} {resource.get('title', 'N/A')}**")
                
                desc = resource.get('description', '')
                if desc:
                    st.caption(desc[:100] + ("..." if len(desc) > 100 else ""))
                
                tags_info = []
                diff = resource.get('difficulty', '强化阶段')
                hours = resource.get('study_hours', 0)
                
                if diff:
                    tags_info.append(diff)
                if hours > 0:
                    tags_info.append(f"建议{hours}小时")
                
                if tags_info:
                    st.markdown(" | ".join([f"`{t}`" for t in tags_info]))
            
            with res_col2:
                file_size = resource.get('file_size', '0MB')
                file_format = resource.get('file_format', '-')
                st.caption(f"📁 {file_size}\n`{file_format}`")
            
            with res_col3:
                dl_btn = st.button(
                    "⬇️ 下载",
                    key=f"dl_eng_{resource.get('id')}",
                    type="primary",
                    use_container_width=True
                )
                
                if dl_btn:
                    st.success(f"✅ 已下载: {resource.get('title', '')}")


if __name__ == "__main__":
    render_page()
