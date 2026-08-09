"""
Analytics Dashboard

Embedded Microsoft Power BI Dashboard
"""

import streamlit as st
import streamlit.components.v1 as components

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Custom CSS
# ==========================================================

st.markdown(
    """
<style>

/* -------------------------------------------------- */
/* Hide Streamlit Elements */
/* -------------------------------------------------- */

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* -------------------------------------------------- */
/* Layout */
/* -------------------------------------------------- */

.main .block-container{

    max-width:99%;

    padding-top:0.5rem;

    padding-bottom:0rem;

}

/* Remove unnecessary top spacing */

section.main > div{
    padding-top:0rem;
}

/* Hide the anchor icon beside headings */

h1>a,
h2>a,
h3>a{
    display:none !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.title("Amazon Review Analytics")

st.sidebar.caption("Enterprise Product Search & Analytics Platform")

st.sidebar.markdown("---")

# ==========================================================
# Embedded Power BI Dashboard
# ==========================================================

powerbi_url = (
    "https://app.powerbi.com/reportEmbed?"
    "reportId=c8911bd6-0b82-41e3-9be1-187224fa9a94"
    "&autoAuth=true"
    "&ctid=56c1d497-700b-49cf-8f8d-3dd6b20d522f"
    "&navContentPaneEnabled=false"
    "&filterPaneEnabled=false"
    "&pageView=fitToWidth"
)

components.iframe(
    powerbi_url,
    height=980,
    scrolling=True,
)

st.caption("Powered by Microsoft Power BI")
