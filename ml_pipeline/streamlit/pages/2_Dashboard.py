"""
Analytics Dashboard
Embedded Microsoft Power BI Dashboard with Amazon Review Intelligence Header
"""

import os
import sys

import streamlit as st
import streamlit.components.v1 as components

# Ensure parent directory is in python path for importing theme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from theme import (
    inject_amazon_theme,
    render_custom_sidebar,
    render_top_navbar,
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Analytics Dashboard - Amazon Review Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Amazon theme styles
inject_amazon_theme()

# Render custom sidebar with moving logo at the VERY TOP
render_custom_sidebar(active_page="Dashboard")

# Render top navbar with active Dashboard tab
render_top_navbar(active_tab="dashboard")

# ==========================================================
# Power BI Header & Embedded Frame
# ==========================================================

st.markdown(
    """<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);"><div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;"><div><h2 style="font-size: 22px; font-weight: 800; color: #172033; margin: 0;">📊 Business Analytics & Power BI Dashboard</h2><div style="font-size: 14px; color: #64748B; margin-top: 4px;">Explore product performance, rating distributions, customer sentiment, and business KPIs across 26.95M+ reviews.</div></div><div style="background: #ECFDF3; border: 1px solid #A7F3D0; color: #15803D; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 700;">● Power BI Live Sync</div></div></div>""",
    unsafe_allow_html=True,
)

# Default Organizational Report Embed URL
DEFAULT_POWERBI_URL = (
    "https://app.powerbi.com/reportEmbed?"
    "reportId=c8911bd6-0b82-41e3-9be1-187224fa9a94"
    "&autoAuth=true"
    "&ctid=56c1d497-700b-49cf-8f8d-3dd6b20d522f"
    "&navContentPaneEnabled=false"
    "&filterPaneEnabled=false"
    "&pageView=fitToWidth"
)

# Allow environment override for Public Embed URL (e.g. view?r=...)
powerbi_url = os.getenv("POWERBI_EMBED_URL", DEFAULT_POWERBI_URL)


# Render Power BI iframe with explicit permissions for Microsoft Entra ID authentication popups
powerbi_iframe_html = f"""
<iframe
    title="Amazon Review Intelligence Power BI Dashboard"
    width="100%"
    height="900"
    src="{powerbi_url}"
    frameborder="0"
    allowFullScreen="true"
    allow="fullscreen; geolocation; microphone; camera"
    sandbox="allow-downloads allow-forms allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation allow-modals">
</iframe>
"""

components.html(
    powerbi_iframe_html,
    height=910,
    scrolling=True,
)

st.markdown(
    """<div style="text-align: center; color: #64748B; font-size: 12px; margin-top: 15px;">Powered by Microsoft Power BI & Amazon Review Intelligence Platform</div>""",
    unsafe_allow_html=True,
)
