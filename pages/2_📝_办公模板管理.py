"""
页面2：办公模板管理模块
提供办公模板的分类浏览、搜索、预览和下载功能
"""

import streamlit as st
import pandas as pd
from services.data_collector import DataCollectorService
from config import config

@st.cache_resource
def get_data_service():
    return DataCollectorService()

service = get_data_service()


def render_page():
    """渲染办公模板管理页面"""
    st.title("📝 办公模板管理中心")
    st.markdown("---")
    
    # ========== 分类导航 ==========
    st.markdown("### 🗂️ 模板分类")
    
    categories = config.OFFICE_CATEGORIES
    
    # 创建分类按钮
    category_cols = st.columns(len(categories))
    selected_category = None
    
    for i, cat in enumerate(categories):
        with category_cols[i]:
            if st.button(cat, use_container_width=True, key=f"cat_{i}"):
                selected_category = cat
                st.rerun()
    
    if not selected_category:
        selected_category = "全部"
    
    st.markdown(f"**当前选择：** {selected_category}")
    
    # ========== 搜索区域 ==========
    search_col1, search_col2 = st.columns([4, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 快速搜索",
            placeholder="输入名称、标签或描述...",
            label_visibility="collapsed"
        )
    
    with search_col2:
        search_btn = st.button("🔍 搜索", use_container_width=True, type="primary")
    
    # ========== 难度筛选 ==========
    difficulty_col1, difficulty_col2, difficulty_col3 = st.columns(3)
    
    with difficulty_col1:
        diff_all = st.checkbox("全部难度", value=True, key="diff_all")
    
    with difficulty_col2:
        show_premium = st.checkbox("仅显示精品", value=False, key="show_premium")
    
    with difficulty_col3:
        sort_by = st.selectbox(
            "排序方式",
            ["默认", "下载量", "评分", "最新"],
            key="sort_by"
        )
    
    # ========== 获取数据 ==========
    with st.spinner(f"正在加载{selected_category}类模板..."):
        templates = service.search_office_templates(
            keyword=search_query,
            category=selected_category if selected_category != "全部" else None
        )
        
        # 应用筛选
        if show_premium:
            templates = [t for t in templates if t.get('is_premium', False)]
        
        # 应用排序
        if sort_by == "下载量":
            templates.sort(key=lambda x: x.get('download_count', 0), reverse=True)
        elif sort_by == "评分":
            templates.sort(key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == "最新":
            templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # ========== 结果展示 ==========
    total_count = len(templates)
    premium_count = len([t for t in templates if t.get('is_premium', False)])
    
    st.markdown(f"### 🎨 模板列表（共 {total_count} 个，其中精品 {premium_count} 个）")
    
    if not templates:
        st.info("😔 暂无符合条件的模板，请尝试其他分类或搜索词")
        return
    
    # 网格卡片展示（每行3个）
    cols_per_row = 3
    
    for i in range(0, len(templates), cols_per_row):
        row_templates = templates[i:i+cols_per_row]
        cols = st.columns(len(row_templates))
        
        for j, template in enumerate(row_templates):
            with cols[j]:
                with st.container(border=True, height=280):
                    # 模板图标和名称
                    icon = "⭐" if template.get('is_premium') else "📄"
                    st.markdown(f"**{icon} {template.get('name', 'N/A')}**")
                    
                    # 分类和子分类
                    cat_info = f"{template.get('category', '')}"
                    subcat = template.get('subcategory', '')
                    if subcat:
                        cat_info += f" > {subcat}"
                    st.caption(cat_info)
                    
                    # 描述（截断）
                    desc = template.get('description', '暂无描述')
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    st.caption(desc)
                    
                    # 评分和下载量
                    rating = template.get('rating', 5.0)
                    downloads = template.get('download_count', 0)
                    st.markdown(f"⭐ {rating} | 📥 {downloads:,}")
                    
                    # 难度标签
                    difficulty = template.get('difficulty', '入门级')
                    diff_color = {
                        '入门级': '🟢',
                        '进阶级': '🟡',
                        '高级定制': '🔴'
                    }.get(difficulty, '⚪')
                    st.caption(f"难度: {diff_color} {difficulty}")
                    
                    # 操作按钮
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        preview_btn = st.button(
                            "👁️ 预览",
                            key=f"preview_{template.get('id')}",
                            use_container_width=True
                        )
                    with btn_col2:
                        download_btn = st.button(
                            "⬇️ 下载",
                            key=f"download_{template.get('id')}",
                            type="primary",
                            use_container_width=True
                        )
    
    # ========== 统计信息 ==========
    with st.expander("📊 模板统计信息"):
        stats = service.get_office_statistics()
        
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("模板总数", stats.get('total', 0))
        with stat_cols[1]:
            st.metric("精品数量", stats.get('premium_count', 0))
        with stat_cols[2]:
            st.metric("平均评分", f"{stats.get('average_rating', 0)} ⭐")
        with stat_cols[3]:
            st.metric("总下载量", f"{stats.get('total_downloads', 0):,}")
        
        # 按分类统计
        st.markdown("**按分类分布：**")
        by_cat = stats.get('by_category', {})
        if by_cat:
            cat_df = pd.DataFrame([
                {'分类': k, '模板数': v} for k, v in by_cat.items()
            ])
            st.dataframe(cat_df.set_index('分类'), use_container_width=True)
    
    # ========== 批量操作 ==========
    st.markdown("### 🔧 批量操作")
    
    batch_col1, batch_col2, batch_col3 = st.columns(3)
    
    with batch_col1:
        export_all = st.download_button(
            "📥 导出全部模板数据",
            data=service.export_data('office', format='json'),
            file_name="all_templates.json",
            mime="application/json",
            use_container_width=True
        )
    
    with batch_col2:
        view_hot = st.button("🔥 查看热门模板TOP10", use_container_width=True)
    
    with batch_col3:
        cleanup = st.button("🧹 清理过期导出文件", use_container_width=True)
    
    if view_hot:
        hot_templates = service.get_hot_templates(limit=10)
        if hot_templates:
            st.markdown("#### 🔥 TOP10 热门模板")
            for i, tmpl in enumerate(hot_templates, 1):
                st.write(f"{i}. **{tmpl.get('name', '')}** - ⭐{tmpl.get('rating', 0)} | 📥{tmpl.get('download_count', 0):,}")


if __name__ == "__main__":
    render_page()
