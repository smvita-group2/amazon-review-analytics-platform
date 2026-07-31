import streamlit as st
from components.styles import load_css

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Amazon Review Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# ---------------------------------
# Hero Section
# ---------------------------------

st.markdown(
    "<h1 class='hero-title'>Amazon Review Analytics Platform</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='hero-subtitle'>AI Powered Product Review Intelligence</p>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class='hero-description'>
    Analyze millions of Amazon customer reviews using
    Big Data Analytics, Interactive Dashboards,
    and Hybrid RAG powered Product Search.
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------------------------
# Action Buttons
# ---------------------------------

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button("📊 Open Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with col2:
    if st.button("🔍 Product Search", use_container_width=True):
        st.switch_page("pages/2_Product_Search.py")
        
# ---------------------------------
# Supported Categories
# ---------------------------------

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <h2 class='category-title'>
        Supported Categories
    </h2>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="category-card">
        <div class="category-icon">🏠</div>
        <div class="category-name">Appliances</div>
        <div class="category-text">
            Explore customer reviews and insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="category-card">
        <div class="category-icon">🏀</div>
        <div class="category-name">Sports</div>
        <div class="category-text">
            Analyze sports product reviews.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown("""
    <div class="category-card">
        <div class="category-icon">🎧</div>
        <div class="category-name">Music & Audio</div>
        <div class="category-text">
            Discover audio product insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="category-card">
        <div class="category-icon">🎮</div>
        <div class="category-name">Video Games</div>
        <div class="category-text">
            Explore gaming product reviews.
        </div>
    </div>
    """, unsafe_allow_html=True)