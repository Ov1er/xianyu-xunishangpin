"""
页面1：考研资料获取模块
提供考研资料的搜索、筛选、预览和管理功能
"""

import streamlit as st
import pandas as pd
from services.data_collector import DataCollectorService
from config import config

# 初始化服务
@st.cache_resource
def get_data_service():
    return DataCollectorService()

service = get_data_service()


def render_page():
    """渲染考研资料获取页面"""
    st.title("📚 考研资料获取中心")
    st.markdown("---")
    
    # ========== 搜索区域 ==========
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_keyword = st.text_input(
            "🔍 搜索资料",
            placeholder="输入关键词（如：政治、真题、肖秀荣...）",
            label_visibility="collapsed"
        )
    
    with col2:
        search_btn = st.button("🔎 搜索", use_container_width=True, type="primary")
    
    with col3:
        refresh_btn = st.button("🔄 刷新数据", use_container_width=True)
    
    # ========== 筛选条件 ==========
    st.markdown("### 📋 筛选条件")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        selected_subject = st.selectbox(
            "科目",
            options=["全部"] + config.KAOYAN_SUBJECTS,
            index=0,
            key="kaoyan_subject"
        )
    
    with filter_col2:
        selected_year = st.selectbox(
            "年份",
            options=["全部"] + [str(y) for y in config.KAOYAN_YEARS],
            index=0,
            key="kaoyan_year"
        )
    
    with filter_col3:
        selected_type = st.selectbox(
            "类型",
            options=["全部"] + config.KAOYAN_TYPES,
            index=0,
            key="kaoyan_type"
        )
    
    with filter_col4:
        selected_status = st.selectbox(
            "状态",
            options=["全部"] + config.KAOYAN_STATUSES,
            index=0,
            key="kaoyan_status"
        )
    
    # ========== 执行搜索或刷新 ==========
    if refresh_btn:
        with st.spinner("正在刷新数据..."):
            result = service.refresh_kaoyan_data()
            st.success(f"✅ {result['message']}")
    
    # 获取数据
    with st.spinner("加载资料数据..."):
        materials = service.search_kaoyan_materials(
            keyword=search_keyword,
            subject=selected_subject if selected_subject != "全部" else None,
            year=int(selected_year) if selected_year != "全部" else None,
            material_type=selected_type if selected_type != "全部" else None
        )
    
    # ========== 结果展示 ==========
    st.markdown(f"### 📊 搜索结果（共 {len(materials)} 条）")
    
    if not materials:
        st.info("😔 暂无符合条件的资料，请尝试调整筛选条件")
        
        # 显示统计信息作为空状态
        stats = service.get_kaoyan_statistics()
        if stats.get('total', 0) > 0:
            with st.expander("💡 查看所有资料统计", expanded=False):
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("资料总数", stats['total'])
                with stat_col2:
                    st.metric("平均评分", f"{stats.get('average_rating', 0)} ⭐")
                with stat_col3:
                    st.metric("总下载量", f"{stats.get('total_downloads', 0):,}")
        return
    
    # 数据表格展示
    df = pd.DataFrame(materials)
    
    # 选择要显示的列
    display_columns = ['title', 'subject', 'year', 'material_type', 'download_count', 'rating']
    available_columns = [col for col in display_columns if col in df.columns]
    
    # 格式化显示
    if 'rating' in df.columns:
        df['rating'] = df['rating'].apply(lambda x: f"{x}⭐" if pd.notna(x) else "-")
    if 'download_count' in df.columns:
        df['download_count'] = df['download_count'].apply(lambda x: f"{x:,}" if pd.notna(x) else "0")
    
    st.dataframe(
        df[available_columns] if available_columns else df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # ========== 操作按钮区 ==========
    st.markdown("### 🔧 操作选项")
    
    op_col1, op_col2, op_col3, op_col4 = st.columns(4)
    
    with op_col1:
        export_json = st.download_button(
            "📥 导出JSON",
            data=service.export_data('kaoyan', format='json'),
            file_name="kaoyan_materials.json",
            mime="application/json",
            use_container_width=True
        )
    
    with op_col2:
        export_csv = st.download_button(
            "📥 导出CSV",
            data=service.export_data('kaoyan', format='csv'),
            file_name="kaoyan_materials.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with op_col3:
        view_stats = st.button("📈 查看统计", use_container_width=True)
    
    with op_col4:
        batch_export = st.button("📦 批量导出", use_container_width=True)
    
    # ========== 统计信息展示 ==========
    if view_stats:
        with st.expander("📊 详细统计分析", expanded=True):
            stats = service.get_kaoyan_statistics()
            
            stat_row1, stat_row2 = st.columns(2)
            
            with stat_row1:
                st.metric("资料总数", stats.get('total', 0))
            
            with stat_row2:
                st.metric("平均评分", f"{stats.get('average_rating', 0)} ⭐")
            
            # 按科目分布
            st.markdown("#### 📚 按科目分布")
            subject_stats = stats.get('by_subject', {})
            if subject_stats:
                subject_df = pd.DataFrame([
                    {'科目': k, '数量': v} for k, v in subject_stats.items()
                ])
                st.bar_chart(subject_df.set_index('科目'), height=200)
            
            # 按年份分布
            st.markdown("#### 📅 按年份分布")
            year_stats = stats.get('by_year', {})
            if year_stats:
                year_df = pd.DataFrame([
                    {'年份': str(k), '数量': v} for k, v in year_stats.items()
                ])
                st.line_chart(year_df.set_index('年份'), height=200)
            
            # 按类型分布
            st.markdown("#### 📋 按类型分布")
            type_stats = stats.get('by_type', {})
            if type_stats:
                type_df = pd.DataFrame([
                    {'类型': k, '数量': v} for k, v in type_stats.items()
                ])
                st.dataframe(type_df, hide_index=True, use_container_width=True)
    
    # ========== 详情查看功能 ==========
    st.markdown("### 🔍 查看详情")
    
    if len(materials) > 0:
        selected_id = st.selectbox(
            "选择要查看的资料",
            options=[m['id'] for m in materials],
            format_func=lambda x: next((m['title'] for m in materials if m['id'] == x), ''),
            key="kaoyan_detail_select"
        )
        
        if selected_id:
            detail = service.get_kaoyan_by_id(selected_id)
            
            if detail:
                with st.container(border=True):
                    st.markdown(f"#### 📖 {detail.get('title', 'N/A')}")
                    
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**科目：** {detail.get('subject', '-')}")
                        st.write(f"**年份：** {detail.get('year', '-')}")
                        st.write(f"**类型：** {detail.get('material_type', '-')}")
                    
                    with detail_col2:
                        st.write(f"**格式：** {detail.get('file_format', '-')}")
                        st.write(f"**大小：** {detail.get('file_size', '-')}")
                        st.write(f"**下载量：** {detail.get('download_count', 0):,}")
                    
                    st.markdown("**详细描述：**")
                    st.write(detail.get('description', '暂无描述'))
                    
                    st.markdown("**标签：**")
                    tags = detail.get('tags', [])
                    if tags:
                        tag_badges = " ".join([f"`{tag}`" for tag in tags])
                        st.markdown(tag_badges)
                    
                    # 操作按钮
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("⬇️ 下载此资料", use_container_width=True, type="primary"):
                            st.success(f"✅ 已开始下载: {detail.get('title', '')}")
                    
                    with btn_col2:
                        if st.button("❤️ 收藏", use_container_width=True):
                            st.info("已添加到收藏夹")


# 页面入口
if __name__ == "__main__":
    render_page()
