"""
Amazon Review Intelligence - Theme & Layout Module
Contains shared Amazon Light CSS tokens, top navbar, animated moving logo, and sidebar components.
"""

import streamlit as st


def inject_amazon_theme():
    """
    Inject global Amazon-inspired Light CSS system.
    Strictly forces high-contrast foreground text on st.tabs elements.
    """
    css_code = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Color System Tokens */
:root {
    --bg-page: #F7F9FC;
    --bg-card: #FFFFFF;
    --primary-orange: #FF9900;
    --primary-orange-hover: #E68A00;
    --primary-dark: #131921;
    --primary-dark-hover: #232F3E;
    --secondary-blue: #2563EB;
    --heading-color: #172033;
    --body-text: #475569;
    --muted-text: #64748B;
    --border-color: #D9E2EC;
    --light-orange: #FFF3E0;
    --success-green: #15803D;
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #F7F9FC !important;
    color: #475569 !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* PAGE TOP SPACING & COMPACT HEADER PADDING */
header {
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: 40px !important;
    z-index: 99999 !important;
}

[data-testid="stDecoration"] { display: none; }

.main .block-container {
    max-width: 1440px !important;
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 1.5rem !important;
}

/* HIDE DEPLOY BUTTON COMPLETELY */
[data-testid="stAppDeployButton"],
.stAppDeployButton,
header [data-testid="stAppDeployButton"],
button[data-testid="stAppDeployButton"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0px !important;
    height: 0px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* SIDEBAR COLLAPSE TOGGLE BUTTON */
header [data-testid="stBaseButton-header"],
[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"] {
    background-color: #131921 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
    z-index: 999999 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

header [data-testid="stBaseButton-header"] svg,
[data-testid="stSidebarCollapseButton"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    width: 18px !important;
    height: 18px !important;
}

header [data-testid="stBaseButton-header"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
    background-color: #FF9900 !important;
    color: #131921 !important;
}

header [data-testid="stBaseButton-header"]:hover svg,
[data-testid="stSidebarCollapseButton"]:hover svg {
    fill: #131921 !important;
    color: #131921 !important;
    stroke: #131921 !important;
}

/* Hide Default Sidebar Navigation */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Custom Sidebar Surface */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #D9E2EC !important;
    box-shadow: 2px 0 15px rgba(0, 0, 0, 0.02) !important;
}

/*
==================================================
STREAMLIT TABS TEXT VISIBILITY FIX (SCOPED STRICTLY TO ST.TABS)
==================================================
*/
[data-testid="stTabs"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-top: 8px !important;
    margin-bottom: 16px !important;
}

/* Selected Tab Underline Indicator (Amazon Orange, NO RED) */
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #FF9900 !important;
    height: 3px !important;
    border-radius: 2px !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #D9E2EC !important;
    gap: 6px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-end !important;
}

/*
INACTIVE TABS (#FFFFFF background / EXPLICIT #172033 DARK TEXT ON ALL CHILD ELEMENTS)
*/
[data-testid="stTabs"] [data-baseweb="tab"],
[data-testid="stTabs"] button[role="tab"] {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: 1px solid #D9E2EC !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 18px !important;
    transition: all 150ms ease !important;
    height: 42px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    opacity: 1 !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] *,
[data-testid="stTabs"] button[role="tab"] * {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/*
HOVER STATE (#FFF3E0 background / EXPLICIT #131921 DARK TEXT / NO RED)
*/
[data-testid="stTabs"] [data-baseweb="tab"]:hover,
[data-testid="stTabs"] button[role="tab"]:hover {
    background-color: #FFF3E0 !important;
    color: #131921 !important;
    -webkit-text-fill-color: #131921 !important;
    border-color: #FF9900 !important;
    opacity: 1 !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover *,
[data-testid="stTabs"] button[role="tab"]:hover * {
    color: #131921 !important;
    -webkit-text-fill-color: #131921 !important;
    opacity: 1 !important;
}

/*
ACTIVE SELECTED TAB (#FF9900 orange background / EXPLICIT #131921 DARK BOLD TEXT)
*/
[data-testid="stTabs"] [aria-selected="true"],
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background-color: #FF9900 !important;
    color: #131921 !important;
    -webkit-text-fill-color: #131921 !important;
    font-weight: 700 !important;
    border: 1px solid #FF9900 !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0 0 !important;
    opacity: 1 !important;
}

[data-testid="stTabs"] [aria-selected="true"] *,
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] *,
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {
    color: #131921 !important;
    -webkit-text-fill-color: #131921 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/*
CATEGORY SELECTBOX & DROPDOWN STYLING
*/
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label {
    color: #172033 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    padding: 2px 10px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #172033 !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    background-color: transparent !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
    border-color: #FF9900 !important;
    box-shadow: 0 0 0 3px rgba(255, 153, 0, 0.18) !important;
}

/* Dropdown Menu Container & Items */
[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
    padding: 4px !important;
}

[data-baseweb="menu"] [role="option"] {
    color: #172033 !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
}

[data-baseweb="menu"] [role="option"]:hover {
    background-color: #FFF3E0 !important;
    color: #131921 !important;
}

[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #FF9900 !important;
    color: #131921 !important;
    font-weight: 700 !important;
}

/* SEARCH INPUT STYLING */
[data-testid="stTextInput"] > div > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 14px !important;
    padding: 2px 12px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stTextInput"] input {
    color: #172033 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #64748B !important;
}

[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #FF9900 !important;
    box-shadow: 0 0 0 3px rgba(255, 153, 0, 0.18) !important;
}

/* SEARCH & CLEAR BUTTONS STYLING */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

/* Search Button (Primary - #FF9900) */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background-color: #FF9900 !important;
    color: #131921 !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(255, 153, 0, 0.25) !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #E68A00 !important;
    color: #131921 !important;
}

/* Clear Button (Secondary - #FFFFFF / #2563EB border / #172033 text) */
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border: 1px solid #2563EB !important;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #EFF6FF !important;
    color: #172033 !important;
    border-color: #2563EB !important;
}

/* METRICS CARDS IN AI GENERATED ANSWER */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #172033 !important;
    font-size: 24px !important;
    font-weight: 700 !important;
}

/* RETRIEVED CONTEXT EXPANDER LIGHT THEME */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    margin-top: 12px !important;
}

[data-testid="stExpander"] details summary {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] details summary * {
    color: #172033 !important;
}

[data-testid="stExpander"] details summary:hover {
    background-color: #F1F5F9 !important;
    color: #172033 !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    padding: 16px !important;
    border-top: 1px solid #D9E2EC !important;
}

.stCodeBlock, [data-testid="stCodeBlock"], pre {
    background-color: #F7F9FC !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 10px !important;
    color: #172033 !important;
}

.stCodeBlock code, pre code {
    color: #172033 !important;
    background: transparent !important;
    font-size: 13px !important;
}

/* Keyframe Animations */
@keyframes logoGlow {
    0% { transform: translateY(0px) scale(1); filter: drop-shadow(0 2px 4px rgba(255, 153, 0, 0.4)); }
    50% { transform: translateY(-3px) scale(1.02); filter: drop-shadow(0 6px 14px rgba(255, 153, 0, 0.6)); }
    100% { transform: translateY(0px) scale(1); filter: drop-shadow(0 2px 4px rgba(255, 153, 0, 0.4)); }
}

@keyframes smilePulse {
    0% { stroke-dashoffset: 120; opacity: 0.7; }
    50% { stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dashoffset: -120; opacity: 0.7; }
}

@keyframes orbFloat {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}

@keyframes ringSpin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pulseGreen {
    0% { box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.7); }
    70% { box-shadow: 0 0 0 8px rgba(21, 128, 61, 0); }
    100% { box-shadow: 0 0 0 0 rgba(21, 128, 61, 0); }
}

.moving-amazon-logo-container {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    animation: logoGlow 3.5s infinite ease-in-out;
    cursor: pointer;
}

.animated-smile-path {
    stroke-dasharray: 120;
    animation: smilePulse 3s infinite linear;
}

.top-navbar {
    background: #131921 !important;
    border-radius: 14px !important;
    padding: 10px 20px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    color: #FFFFFF !important;
    margin-top: 0px !important;
    margin-bottom: 18px !important;
    gap: 16px !important;
    box-shadow: 0 8px 24px -4px rgba(19, 25, 33, 0.2) !important;
}

.nav-brand {
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
    flex-shrink: 0 !important;
}

.nav-title-group {
    display: flex !direction: column !important;
}

.nav-title {
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    line-height: 1.1 !important;
}

.nav-subtitle {
    font-size: 11px !important;
    color: #94A3B8 !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
}

.nav-center-tabs {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: rgba(255, 255, 255, 0.08) !important;
    padding: 4px 8px !important;
    border-radius: 10px !important;
}

.nav-tab-item {
    padding: 7px 18px !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    text-decoration: none !important;
    color: #CBD5E1 !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    white-space: nowrap !important;
}

.nav-tab-item:hover {
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.15) !important;
    text-decoration: none !important;
}

.nav-tab-item.active {
    background: #FF9900 !important;
    color: #131921 !important;
    box-shadow: 0 4px 12px rgba(255, 153, 0, 0.35) !important;
    text-decoration: none !important;
}

.nav-right-status {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    flex-shrink: 0 !important;
}

.status-badge-online {
    background: rgba(21, 128, 61, 0.2) !important;
    border: 1px solid rgba(21, 128, 61, 0.4) !important;
    color: #4ADE80 !important;
    padding: 5px 12px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.status-dot-pulse {
    width: 7px !important;
    height: 7px !important;
    background-color: #22C55E !important;
    border-radius: 50% !important;
    animation: pulseGreen 2s infinite !important;
}

.hero-title-main {
    font-size: 40px;
    font-weight: 800;
    color: #131921;
    letter-spacing: -1px;
    line-height: 1.15;
    margin-bottom: 8px;
}

.hero-title-accent {
    color: #FF9900;
}

.hero-subtitle-text {
    font-size: 16px;
    color: #64748B;
    font-weight: 500;
    margin-bottom: 18px;
}

.tech-pill-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
}

.tech-pill {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    display: flex;
    align-items: center;
    gap: 6px;
}

.metrics-bar-card {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 14px;
    padding: 16px 24px;
    display: grid;
    grid-template-columns: 1fr 1fr 1.5fr;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    margin-bottom: 24px;
}

.metric-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-right: 1px solid #F1F5F9;
}

.metric-item:last-child {
    border-right: none;
}

.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #172033;
    line-height: 1.1;
}

.metric-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 600;
    margin-top: 4px;
}

.feature-card {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.feature-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}

.feature-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.icon-blue {
    background: #EAF3FB;
    color: #146EB4;
}

.icon-green {
    background: #ECFDF3;
    color: #15803D;
}

.feature-title {
    font-size: 19px;
    font-weight: 700;
    color: #172033;
    margin: 0;
}

.feature-desc {
    font-size: 13.5px;
    color: #64748B;
    margin-bottom: 18px;
    line-height: 1.5;
}

.feature-list {
    list-style: none;
    padding: 0;
    margin: 0 0 20px 0;
}

.feature-list-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13.5px;
    color: #334155;
    font-weight: 500;
    margin-bottom: 8px;
}

.check-blue { color: #146EB4; font-weight: 800; }
.check-green { color: #15803D; font-weight: 800; }

.side-widget-card {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.side-widget-title {
    font-size: 15px;
    font-weight: 700;
    color: #172033;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #F8FAFC;
    font-size: 13.5px;
}

.status-row:last-child {
    border-bottom: none;
}

.status-name {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #334155;
    font-weight: 500;
}

.status-tag {
    color: #15803D;
    font-weight: 600;
    font-size: 12.5px;
}

.stats-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.stat-subcard {
    background: #F7F9FC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
}

.stat-subval {
    font-size: 20px;
    font-weight: 800;
    color: #146EB4;
}

.stat-sublbl {
    font-size: 12px;
    color: #64748B;
    font-weight: 600;
}

.category-pill-card {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    padding: 10px 18px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
}

.cat-appliances { background: #EAF3FB; color: #146EB4; border-color: #B8D5EE; }
.cat-instruments { background: #FDF4FF; color: #7E22CE; border-color: #F5D0FE; }
.cat-games { background: #ECFDF3; color: #15803D; border-color: #A7F3D0; }
.cat-sports { background: #FFF7ED; color: #B45309; border-color: #FFEDD5; }

.platform-footer {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 35px;
    padding-top: 18px;
    border-top: 1px solid #D9E2EC;
}
</style>"""
    st.markdown(css_code, unsafe_allow_html=True)


def get_moving_amazon_logo_svg(width=135, height=36):
    """
    Returns HTML for the animated moving Amazon logo SVG.
    """
    return f"""<div class="moving-amazon-logo-container"><svg width="{width}" height="{height}" viewBox="0 0 135 36" fill="none" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0, 2)"><text x="0" y="24" font-family="'Plus Jakarta Sans', 'Inter', sans-serif" font-weight="800" font-size="25" fill="#FFFFFF" letter-spacing="-0.5px">amazon</text><path class="animated-smile-path" d="M 10 27 Q 48 37 84 23" stroke="#FF9900" stroke-width="3.5" stroke-linecap="round" fill="none"/><path d="M 81 19 L 88 24 L 84 28 Z" fill="#FF9900"/></g></svg></div>"""


def get_3d_orb_graphic_html():
    """
    Returns HTML for the 3D animated floating Amazon orbital graphic.
    """
    return """<div style="position: relative; width: 100%; height: 260px; display: flex; align-items: center; justify-content: center; animation: orbFloat 4s infinite ease-in-out;"><div style="position: absolute; width: 210px; height: 210px; border-radius: 50%; border: 2px dashed rgba(20, 110, 180, 0.3); animation: ringSpin 22s linear infinite;"></div><div style="width: 160px; height: 160px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #FFFFFF 0%, #F0F9FF 50%, #E0F2FE 85%, #BAE6FD 100%); box-shadow: 0 20px 45px rgba(20, 110, 180, 0.2), inset 0 -12px 24px rgba(20, 110, 180, 0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px solid #FFFFFF;"><div style="font-size: 72px; font-weight: 900; color: #131921; font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1; position: relative;">a<div style="position: absolute; bottom: -10px; left: -12px; width: 68px; height: 22px;"><svg viewBox="0 0 68 22" fill="none"><path d="M 5 9 Q 34 20 60 9" stroke="#FF9900" stroke-width="4.5" stroke-linecap="round"/><path d="M 56 4 L 64 10 L 59 15 Z" fill="#FF9900"/></svg></div></div></div><div style="position: absolute; top: 10px; left: 25px; background: #FF9900; color: #131921; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(255, 153, 0, 0.4); font-size: 17px;">🔍</div><div style="position: absolute; top: 20px; right: 20px; background: #146EB4; color: white; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(20, 110, 180, 0.4); font-size: 17px;">💬</div><div style="position: absolute; bottom: 15px; right: 30px; background: #FF9900; color: #131921; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(255, 153, 0, 0.4); font-size: 16px;">⭐</div><div style="position: absolute; bottom: 25px; left: 20px; background: #15803D; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(21, 128, 61, 0.4); font-size: 16px;">🛒</div></div>"""


def render_top_navbar(active_tab="home"):
    """
    Renders the fixed dark top navigation bar with Home, Product Search & Analytics Dashboard.
    """
    logo_html = get_moving_amazon_logo_svg()

    home_active = "active" if active_tab == "home" else ""
    search_active = "active" if active_tab == "search" else ""
    dash_active = "active" if active_tab == "dashboard" else ""

    navbar_html = f"""<div class="top-navbar"><div class="nav-brand">{logo_html}<div class="nav-title-group"><div class="nav-title">Review Intelligence</div><div class="nav-subtitle">AI-Powered Product Search & Analytics</div></div></div><div class="nav-center-tabs"><a href="/" target="_self" class="nav-tab-item {home_active}"><span>🏠</span> Home</a><a href="/Product_Search" target="_self" class="nav-tab-item {search_active}"><span>🔍</span> Product Search</a><a href="/Dashboard" target="_self" class="nav-tab-item {dash_active}"><span>📊</span> Analytics Dashboard</a></div><div class="nav-right-status"><div class="status-badge-online"><div class="status-dot-pulse"></div>Online</div><div style="background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 20px; font-size: 13px; cursor: pointer;">☀️ 🌙</div></div></div>"""
    st.markdown(navbar_html, unsafe_allow_html=True)


def render_custom_sidebar(active_page="Home"):
    """
    Renders custom sidebar with Amazon logo at top, Home, Product Search & Analytics Dashboard links.
    """
    with st.sidebar:
        # 1. Amazon Logo Card AT THE VERY TOP OF THE SIDEBAR
        logo_svg = get_moving_amazon_logo_svg(width=130, height=34)
        sidebar_logo_html = f"""<div style="background: #131921; padding: 18px; border-radius: 14px; margin-bottom: 20px; text-align: center; box-shadow: 0 8px 20px rgba(19, 25, 33, 0.15);">{logo_svg}<div style="color: #94A3B8; font-size: 11px; margin-top: 6px; font-weight: 700; letter-spacing: 0.6px;">REVIEW INTELLIGENCE</div></div>"""
        st.markdown(sidebar_logo_html, unsafe_allow_html=True)

        # 2. Navigation Links (Home, Product Search, Analytics Dashboard)
        st.caption("NAVIGATION")

        h_type = "primary" if active_page == "Home" else "secondary"
        s_type = "primary" if active_page == "Product_Search" else "secondary"
        d_type = "primary" if active_page == "Dashboard" else "secondary"

        if st.button(
            "🏠  Home", key="nav_sb_home", type=h_type, use_container_width=True
        ):
            st.switch_page("Home.py")

        if st.button(
            "🔍  Product Search",
            key="nav_sb_search",
            type=s_type,
            use_container_width=True,
        ):
            st.switch_page("pages/1_Product_Search.py")

        if st.button(
            "📊  Analytics Dashboard",
            key="nav_sb_dash",
            type=d_type,
            use_container_width=True,
        ):
            st.switch_page("pages/2_Dashboard.py")

        st.markdown(
            "<hr style='margin: 16px 0; border: none; border-top: 1px solid #D9E2EC;'>",
            unsafe_allow_html=True,
        )

        # 3. System Status
        st.caption("SYSTEM STATUS")

        status_items = [
            ("Hybrid RAG Pipeline", "Operational"),
            ("ChromaDB", "Connected"),
            ("BM25 Index", "Loaded"),
            ("Gemini 3.5 Flash-lite", "Connected"),
            ("Power BI Service", "Connected"),
        ]

        for name, status in status_items:
            row_html = f"""<div style="display: flex; align-items: center; justify-content: space-between; padding: 5px 0; font-size: 13px;"><div style="display: flex; align-items: center; gap: 8px; color: #334155; font-weight: 500;"><span style="color: #15803D; font-size: 10px;">●</span> {name}</div><div style="color: #15803D; font-weight: 600; font-size: 12px;">{status}</div></div>"""
            st.markdown(row_html, unsafe_allow_html=True)

        st.markdown(
            "<hr style='margin: 16px 0; border: none; border-top: 1px solid #D9E2EC;'>",
            unsafe_allow_html=True,
        )

        # 4. About Platform
        about_html = """<div style="background: #F7F9FC; border: 1px solid #D9E2EC; padding: 14px; border-radius: 12px; text-align: center;"><div style="font-size: 13px; font-weight: 700; color: #172033; margin-bottom: 4px;">ℹ️ About Platform</div><div style="font-size: 11.5px; color: #64748B; line-height: 1.4;">Enterprise Hybrid RAG platform for Amazon reviews using Gemini 3.5 & ChromaDB.</div></div>"""
        st.markdown(about_html, unsafe_allow_html=True)
