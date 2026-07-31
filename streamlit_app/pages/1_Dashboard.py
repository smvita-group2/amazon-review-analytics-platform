import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------
# Header
# ---------------------------------
st.title("📊 Amazon Review Analytics Dashboard")

st.write(
    "Explore customer review insights using the interactive Power BI dashboard."
)

# ---------------------------------
# Power BI Dashboard
# ---------------------------------

components.html(
    """
    <iframe
        title="AmazonReview"
        width="100%"
        height="850"
        src="https://app.powerbi.com/reportEmbed?reportId=c8911bd6-0b82-41e3-9be1-187224fa9a94&autoAuth=true&ctid=56c1d497-700b-49cf-8f8d-3dd6b20d522f"
        frameborder="0"
        allowfullscreen="true">
    </iframe>
    """,
    height=900,
)