import streamlit as st
from pathlib import Path

from components.styles import load_css

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Amazon Review Analytics Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# LOAD CSS
# ==========================================================

st.markdown(load_css(), unsafe_allow_html=True)

# ==========================================================
# ASSETS
# ==========================================================

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"

LOGO = ASSETS / "Official logo amazon (1).jpg"

VIDEO_GAME = ASSETS / "Video game p1.png"
SPORT = ASSETS / "Sport.png"
APPLIANCE = ASSETS / "appliences.jpg"
MUSICAL = ASSETS / "Musical products.jpg"

# ==========================================================
# SESSION STATE
# ==========================================================

if "category" not in st.session_state:
    st.session_state.category = None

# ==========================================================
# HERO
# ==========================================================

# ---------- Header (Logo Top Left) ----------

col_logo, col_space = st.columns([1, 8])

with col_logo:
    st.image(str(LOGO), width=110)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Hero Title ----------

st.markdown(
"""
<h1 class="hero-title">
Amazon <span style="color:#FF9900;">Review</span><br>
Analytics Platform
</h1>
""",
unsafe_allow_html=True
)

# ---------- Subtitle ----------

st.markdown(
"""
<div class="hero-subtitle">
AI Powered Product Review Intelligence
</div>
""",
unsafe_allow_html=True
)

# ---------- Orange Line ----------

st.markdown(
"""
<div style="
width:140px;
height:4px;
margin:18px auto 30px auto;
background:linear-gradient(90deg,#7C3AED,#FF9900);
border-radius:20px;
">
</div>
""",
unsafe_allow_html=True
)

# ---------- Description ----------

st.markdown(
"""
<div class="hero-description">
Discover customer insights from millions of Amazon reviews.<br><br>

Search products, visualize analytics dashboards,<br><br>

and explore AI-powered recommendations using Hybrid RAG.
</div>
""",
unsafe_allow_html=True
)

# ==========================================================
# NAVIGATION
# ==========================================================

st.markdown(
"""
<div style="
text-align:center;
font-size:20px;
font-weight:700;
margin-top:30px;
margin-bottom:15px;">
Navigation
</div>
""",
unsafe_allow_html=True
)

page = st.segmented_control(
    "Navigation",
    [
        "🔍 Product Search",
        "📊 Dashboard"
    ],
    default="🔍 Product Search"
)

if page == "📊 Dashboard":
    st.switch_page("pages/1_Dashboard.py")

# ==========================================================
# SEARCH
# ==========================================================

search = st.text_input(

    "",

    placeholder="Search Amazon Products..."

)