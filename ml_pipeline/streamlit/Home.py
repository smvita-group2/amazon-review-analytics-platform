"""
Amazon Review Intelligence Platform
Home Page - Modern Amazon Theme with Animated Moving Logo
"""

import streamlit as st
import streamlit.components.v1 as components

from theme import (
    get_3d_orb_graphic_html,
    get_moving_amazon_logo_svg,
    inject_amazon_theme,
    render_custom_sidebar,
    render_top_navbar,
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Amazon Review Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS styles
inject_amazon_theme()

# Render custom sidebar with moving logo at the VERY TOP
render_custom_sidebar(active_page="Home")

# Render top fixed navigation bar
render_top_navbar(active_tab="home")

# ==========================================================
# Main Content Area
# ==========================================================

col_main, col_right = st.columns([2.2, 1], gap="large")

with col_main:
    # Hero Title & Subtitle
    st.markdown(
        """<div style="margin-bottom: 20px;"><div class="hero-title-main">Amazon <span class="hero-title-accent">Review Intelligence</span></div><div class="hero-subtitle-text">AI-powered product discovery and review intelligence using Hybrid RAG.</div></div>""",
        unsafe_allow_html=True,
    )

    # Tech Pills Row
    st.markdown(
        """<div class="tech-pill-container"><div class="tech-pill">🔑 Semantic Search</div><div class="tech-pill">🔤 BM25 Search</div><div class="tech-pill">🔀 RRF Fusion</div><div class="tech-pill">🔍 CrossEncoder Reranking</div><div class="tech-pill">🗄️ ChromaDB</div><div class="tech-pill">✦ Gemini 3.5 Flash-lite</div></div>""",
        unsafe_allow_html=True,
    )

    # 1. Category Selection Above Search Bar
    st.markdown(
        """<div style="font-size: 13.5px; font-weight: 700; color: #172033; margin-bottom: 8px;">📂 Select Category:</div>""",
        unsafe_allow_html=True,
    )

    cat_options = ["Appliances", "Musical_Instruments", "Video_Games", "Sports_and_Outdoors"]
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = cat_options[0]

    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    for idx, (col, cat) in enumerate(zip([c_col1, c_col2, c_col3, c_col4], cat_options)):
        label = cat.replace("_", " ")
        is_selected = (st.session_state.selected_category == cat)
        btn_kind = "primary" if is_selected else "secondary"
        with col:
            if st.button(label, key=f"cat_select_{cat}", type=btn_kind, use_container_width=True):
                st.session_state.selected_category = cat
                st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # 2. Search Bar Input
    search_val = st.session_state.get("search_query_value", "")
    current_cat_display = st.session_state.selected_category.replace("_", " ")

    search_query = st.text_input(
        label="Search Input",
        value=search_val,
        placeholder=f"Search in {current_cat_display} (e.g. products, reviews, or ask anything)...",
        key="home_search_input",
        label_visibility="collapsed",
    )

    # Trigger navigation to Product Search page if query is entered
    if search_query and search_query != search_val:
        st.session_state["search_query_initial"] = search_query
        st.session_state["category"] = st.session_state.selected_category
        st.switch_page("pages/1_Product_Search.py")

    # 3. Clickable Example Query Chips Below Search Bar
    st.markdown(
        """<div style="font-size: 13px; color: #64748B; margin-top: 10px; margin-bottom: 6px; font-weight: 600;">💡 Click an example search query to run:</div>""",
        unsafe_allow_html=True,
    )

    ex_col1, ex_col2, ex_col3 = st.columns(3)
    examples = ["best noise cancelling headphones", "quiet dishwasher", "gaming laptop under $1000"]

    for idx, (col, ex) in enumerate(zip([ex_col1, ex_col2, ex_col3], examples)):
        with col:
            if st.button(f'"{ex}"', key=f"ex_btn_{idx}", use_container_width=True):
                st.session_state["search_query_initial"] = ex
                st.session_state["category"] = st.session_state.selected_category
                st.switch_page("pages/1_Product_Search.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Key Metrics Banner
    st.markdown(
        """<div class="metrics-bar-card"><div class="metric-item"><div class="metric-value">4</div><div class="metric-label">Categories</div></div><div class="metric-item"><div class="metric-value">2</div><div class="metric-label">Platform Modules</div></div><div class="metric-item"><div class="metric-value" style="color: #146EB4;">Gemini 3.5 Flash-lite</div><div class="metric-label">AI Model</div></div></div>""",
        unsafe_allow_html=True,
    )

    # Two Main Feature Cards Side by Side
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown(
            """<div class="feature-card"><div><div class="feature-header"><div class="feature-icon-box icon-blue">🔍</div><div class="feature-title">Product Search</div></div><div class="feature-desc">AI-powered product discovery using Hybrid RAG.</div><ul class="feature-list"><li class="feature-list-item"><span class="check-blue">✓</span> Semantic Search with Sentence Transformers</li><li class="feature-list-item"><span class="check-blue">✓</span> Keyword Search with BM25</li><li class="feature-list-item"><span class="check-blue">✓</span> Reciprocal Rank Fusion (RRF)</li><li class="feature-list-item"><span class="check-blue">✓</span> CrossEncoder Reranking</li><li class="feature-list-item"><span class="check-blue">✓</span> ChromaDB Vector Database</li><li class="feature-list-item"><span class="check-blue">✓</span> Google Gemini 3.5 Flash-lite AI</li></ul></div></div>""",
            unsafe_allow_html=True,
        )

        if st.button("Start Product Search →", key="btn_start_search", type="primary", use_container_width=True):
            st.switch_page("pages/1_Product_Search.py")

    with c2:
        st.markdown(
            """<div class="feature-card"><div><div class="feature-header"><div class="feature-icon-box icon-green">📊</div><div class="feature-title">Analytics Dashboard</div></div><div class="feature-desc">Business intelligence and insights with Power BI.</div><ul class="feature-list"><li class="feature-list-item"><span class="check-green">✓</span> Interactive Power BI Dashboards</li><li class="feature-list-item"><span class="check-green">✓</span> Product Performance Analytics</li><li class="feature-list-item"><span class="check-green">✓</span> Customer Review Insights</li><li class="feature-list-item"><span class="check-green">✓</span> Ratings & Sentiment Analysis</li><li class="feature-list-item"><span class="check-green">✓</span> Business KPIs & Metrics</li><li class="feature-list-item"><span class="check-green">✓</span> Trend Analysis & Reporting</li></ul></div></div>""",
            unsafe_allow_html=True,
        )

        if st.button("Open Analytics Dashboard →", key="btn_open_dash", type="secondary", use_container_width=True):
            st.switch_page("pages/2_Dashboard.py")

with col_right:
    # 3D Animated Orb Graphic
    st.markdown(get_3d_orb_graphic_html(), unsafe_allow_html=True)

    # System Status Side Card
    st.markdown(
        """<div class="side-widget-card"><div class="side-widget-title"><span>⚡</span> System Status</div><div class="status-row"><div class="status-name"><span style="color:#15803D;">●</span> Hybrid RAG Pipeline</div><div class="status-tag">Operational</div></div><div class="status-row"><div class="status-name"><span style="color:#15803D;">●</span> ChromaDB</div><div class="status-tag">Connected</div></div><div class="status-row"><div class="status-name"><span style="color:#15803D;">●</span> BM25 Index</div><div class="status-tag">Loaded</div></div><div class="status-row"><div class="status-name"><span style="color:#15803D;">●</span> Gemini 3.5 Flash-lite</div><div class="status-tag">Connected</div></div><div class="status-row"><div class="status-name"><span style="color:#15803D;">●</span> Power BI Service</div><div class="status-tag">Connected</div></div></div>""",
        unsafe_allow_html=True,
    )

    # Platform Statistics 2x2 Grid
    st.markdown(
        """<div class="side-widget-card"><div class="side-widget-title"><span>📈</span> Platform Statistics</div><div class="stats-grid-2x2"><div class="stat-subcard"><div class="stat-subval">3.2M+</div><div class="stat-sublbl">Products</div></div><div class="stat-subcard"><div class="stat-subval">15M+</div><div class="stat-sublbl">Reviews</div></div><div class="stat-subcard"><div class="stat-subval">4</div><div class="stat-sublbl">Categories</div></div><div class="stat-subcard"><div class="stat-subval">2</div><div class="stat-sublbl">Modules</div></div></div></div>""",
        unsafe_allow_html=True,
    )

# Supported Categories Section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """<div style="text-align: center; margin-bottom: 16px;"><h3 style="font-size: 18px; font-weight: 700; color: #172033; margin: 0;">Supported Categories</h3></div>""",
    unsafe_allow_html=True,
)

cat_c1, cat_c2, cat_c3, cat_c4 = st.columns(4)

with cat_c1:
    st.markdown('<div class="category-pill-card cat-appliances">🧺 Appliances</div>', unsafe_allow_html=True)
with cat_c2:
    st.markdown('<div class="category-pill-card cat-instruments">🎸 Musical Instruments</div>', unsafe_allow_html=True)
with cat_c3:
    st.markdown('<div class="category-pill-card cat-games">🎮 Video Games</div>', unsafe_allow_html=True)
with cat_c4:
    st.markdown('<div class="category-pill-card cat-sports">🏀 Sports & Outdoors</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    """<div class="platform-footer"><b>Amazon Review Intelligence Platform</b><br>Built with ❤️ using AWS • PySpark • ChromaDB • Streamlit • Gemini 3.5 Flash-lite<br><span style="font-size: 12px; opacity: 0.8;">© 2024 All rights reserved.</span></div>""",
    unsafe_allow_html=True,
)
