"""
Home Page

Landing page for the Amazon Review Analytics Platform.
"""

import streamlit as st

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Amazon Review Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CSS
# ==========================================================

st.markdown(
    """
<style>

/* -------------------------------------------------- */
/* Hide Streamlit Branding */
/* -------------------------------------------------- */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

/* Keep header visible so the sidebar toggle works */

header{
    background:transparent;
}

/* Hide only the Deploy button */

[data-testid="stDecoration"]{
    display:none;
}

/* -------------------------------------------------- */
/* Layout */
/* -------------------------------------------------- */

.main .block-container{

    max-width:1400px;

    padding-top:2rem;

    padding-bottom:2rem;

}

/* -------------------------------------------------- */
/* Hero */
/* -------------------------------------------------- */

.hero{

    background:linear-gradient(
        135deg,
        #2563EB,
        #4F46E5
    );

    border-radius:18px;

    padding:45px;

    color:white;

    margin-bottom:25px;

    box-shadow:0px 8px 25px rgba(0,0,0,.18);

}

.hero h1{

    margin:0;

    font-size:42px;

    font-weight:700;

}

.hero p{

    margin-top:15px;

    font-size:18px;

    opacity:.95;

    line-height:1.7;

}

/* -------------------------------------------------- */
/* Footer */
/* -------------------------------------------------- */

.footer{

    text-align:center;

    color:#6B7280;

    margin-top:40px;

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

st.sidebar.info("""
Navigate between the available platform modules
using the menu below.
""")


# ==========================================================
# Hero
# ==========================================================

st.markdown(
    """
<div class="hero">

<h1>Amazon Review Analytics Platform</h1>

<p>

Enterprise Product Search and Analytics Platform powered by
Hybrid Retrieval-Augmented Generation (Hybrid RAG),
Sentence Transformers,
BM25,
Reciprocal Rank Fusion (RRF),
CrossEncoder Reranking
and
Google Gemini 3.5 Flash.

</p>

</div>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# Platform Overview
# ==========================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Categories",
        "4",
    )

with c2:

    st.metric(
        "Platform Modules",
        "2",
    )

with c3:

    st.metric(
        "AI Model",
        "Gemini 3.5 Flash",
    )

st.markdown("---")

st.header("Platform Modules")

st.caption("Select a module to continue.")

# ==========================================================
# Product Search Module
# ==========================================================

with st.container(border=True):

    left, right = st.columns(
        [4, 1],
        vertical_alignment="center",
    )

    with left:

        st.subheader("Product Search")

        st.write("""
Search Amazon products using an enterprise
Hybrid Retrieval-Augmented Generation (Hybrid RAG)
pipeline that combines semantic retrieval,
keyword search and large language models.
""")

        st.markdown("**Technology Stack**")

        c1, c2 = st.columns(2)

        with c1:

            st.write("• Sentence Transformers")

            st.write("• BM25 Retrieval")

            st.write("• Reciprocal Rank Fusion")

        with c2:

            st.write("• CrossEncoder Reranking")

            st.write("• Google Gemini 3.5 Flash")

            st.write("• ChromaDB")

    with right:

        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button(
            "Launch Module",
            key="search",
            type="primary",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/1_Product_Search.py",
            )

# ==========================================================
# Dashboard Module
# ==========================================================

with st.container(border=True):

    left, right = st.columns(
        [4, 1],
        vertical_alignment="center",
    )

    with left:

        st.subheader("Analytics Dashboard")

        st.write("""
Explore interactive Power BI dashboards for
customer reviews, product performance,
ratings analysis and business insights.
""")

        st.markdown("**Capabilities**")

        c1, c2 = st.columns(2)

        with c1:

            st.write("• Interactive Reports")

            st.write("• Customer Insights")

            st.write("• Product Analytics")

        with c2:

            st.write("• Ratings & Reviews")

            st.write("• Business KPIs")

            st.write("• Trend Analysis")

    with right:

        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button(
            "Launch Module",
            key="dashboard",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/2_Dashboard.py",
            )
# ==========================================================
# Footer
# ==========================================================

st.markdown("---")

st.markdown(
    """
<div class="footer">

<b>Amazon Review Analytics Platform</b>

<br>

Enterprise Big Data Engineering Project

</div>
""",
    unsafe_allow_html=True,
)
