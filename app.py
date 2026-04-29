"""
Streamlit 应用主入口
负责全局配置、侧边栏和主页面的渲染
"""

import streamlit as st
from config import config


def main():
    """应用主函数"""
    
    # ========== 页面基础配置 ==========
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state=config.SIDEBAR_STATE
    )
    
    # ========== 注入自定义CSS样式 ==========
    _inject_custom_styles()
    
    # ========== 渲染侧边栏 ==========
    _render_sidebar()
    
    # ========== 渲染主页面（首页） ==========
    _render_main_page()


def _inject_custom_styles():
    """注入自定义CSS样式"""
    try:
        with open(f"{config.ASSETS_DIR}/styles.css", "r", encoding="utf-8") as f:
            custom_css = f.read()
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def _render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # Logo区域
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; margin: 0;">🚀</h1>
            <h3 style="margin: 5px 0;">工作流系统</h3>
            <p style="color: #666; font-size: 0.9rem;">v{config.APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 系统状态仪表盘
        st.subheader("📊 系统状态")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("资料总数", "540+", "+12 今日")
        with col2:
            st.metric("生成笔记", "89", "本周")
        
        st.metric("导出次数", "234", "累计")
        
        st.markdown("---")
        
        # 快速导航提示
        st.caption("💡 使用顶部Tab切换功能模块")
        
        st.markdown("---")
        
        # 版本信息
        st.caption(f"© 2026 {config.APP_NAME}")
        st.caption(f"版本 {config.APP_VERSION}")


def _render_main_page():
    """渲染主页面（系统概览）"""
    st.title("🚀 闲鱼虚拟产品自动化工作流系统")
    st.markdown(f"### v{config.APP_VERSION} - 高效 · 智能 · 自动化")
    st.markdown("---")
    
    # 功能卡片介绍
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("""
        ### 📚 考研资料
        
        自动检索、筛选、整理最新考研相关资料
        
        ✓ 历年真题  
        ✓ 复习指南  
        ✓ 考试大纲  
        ✓ 学霸笔记
        """)
    
    with col2:
        st.success("""
        ### 📝 办公模板
        
        收集、分类和提供各类常用办公模板
        
        ✓ PPT模板  
        ✓ Word模板  
        ✓ Excel模板  
        ✓ 简历模板
        """)
    
    with col3:
        st.warning("""
        ### 📖 英语资料包
        
        整合考研英语全方位学习资源
        
        ✓ 核心词汇  
        ✓ 语法精讲  
        ✓ 阅读训练  
        ✓ 写作模板
        """)
    
    with col4:
        st.error("""
        ### ✍️ 笔记生成
        
        自动生成小红书风格推广笔记
        
        ✓ 多风格切换  
        ✓ 多版本输出  
        ✓ 智能标签  
        ✓ 配图建议
        """)
    
    st.markdown("---")
    
    # 使用说明
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
        ### 快速上手指南
        
        1. **浏览资料** → 点击上方Tab进入各功能模块
        2. **筛选查找** → 使用搜索和筛选条件定位目标资料
        3. **预览详情** → 点击查看详细信息和文件列表
        4. **下载导出** → 一键下载单个文件或批量导出
        5. **生成笔记** → 在笔记生成器中选择素材并生成推广内容
        
        ### 特色功能
        
        - 🔍 **智能搜索**：支持关键词模糊匹配
        - 📦 **批量操作**：多选后一键导出
        - ✍️ **AI生成**：模板化生成小红书风格笔记
        - 🔄 **定期更新**：手动触发数据刷新
        """)


if __name__ == "__main__":
    main()
