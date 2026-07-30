"""
Hybrid RAG Platform for Intelligent Product Search

Enterprise Streamlit Dashboard
"""

import streamlit as st

#from pipeline import Pipeline


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Hybrid RAG Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------

st.markdown(
    """
<style>

/* Hide Streamlit Branding */

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}


/* Main Container */

.main .block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1400px;
}


/* Sidebar */

section[data-testid="stSidebar"]{
    background-color:#111827;
}

section[data-testid="stSidebar"] *{
    color:white;
}


/* Hero Banner */

.hero{
    background:linear-gradient(135deg,#2563EB,#4F46E5);
    padding:35px;
    border-radius:18px;
    color:white;
    margin-bottom:25px;
    box-shadow:0px 6px 20px rgba(0,0,0,.15);
}

.hero h1{
    font-size:40px;
    margin-bottom:8px;
}

.hero p{
    font-size:18px;
    opacity:.95;
}


/* Metric Cards */

.metric-card{
    background:white;
    padding:20px;
    border-radius:15px;
    text-align:center;
    border:1px solid #ECECEC;
    box-shadow:0px 4px 12px rgba(0,0,0,.08);
}

.metric-title{
    color:#666;
    font-size:14px;
}

.metric-value{
    font-size:28px;
    font-weight:bold;
    color:#2563EB;
}


/* AI Response */

.answer-card{
    background:#F8FAFC;
    padding:25px;
    border-radius:18px;
    border-left:6px solid #2563EB;
    margin-top:15px;
    margin-bottom:20px;
    box-shadow:0px 4px 10px rgba(0,0,0,.05);
}


/* Product Cards */

.product-card{

    background:white;

    border-radius:16px;

    padding:20px;

    margin-bottom:18px;

    border:1px solid #E5E7EB;

    box-shadow:0px 4px 12px rgba(0,0,0,.08);

}


.product-title{

    font-size:22px;

    font-weight:bold;

    color:#1F2937;

}


.badge{

    display:inline-block;

    padding:4px 10px;

    border-radius:12px;

    background:#2563EB;

    color:white;

    font-size:12px;

    margin-right:6px;

    margin-top:8px;

}


.footer{

    text-align:center;

    color:#777;

    margin-top:60px;

    font-size:14px;

}


/* Search Button */

div.stButton > button{

    width:100%;

    height:52px;

    font-size:18px;

    border-radius:12px;

    background:#2563EB;

    color:white;

    border:none;

}

div.stButton > button:hover{

    background:#1D4ED8;

}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

CATEGORY_OPTIONS = [
    "Appliances",
    "Musical_Instruments",
    "Video_Games",
]

st.sidebar.markdown(
    """
# 🛒 Hybrid RAG Platform

### Intelligent Product Search

Enterprise Retrieval-Augmented Generation Platform

---
""",
)

category = st.sidebar.selectbox(
    "📂 Product Category",
    CATEGORY_OPTIONS,
)

st.sidebar.markdown("---")

st.sidebar.subheader("💡 Example Questions")

example_questions = [

    "Recommend a dishwasher under $500",

    "Which gaming headset has the best sound quality?",

    "Best beginner acoustic guitar",

    "Compare two similar products",

    "Which product has the highest ratings?",

]

for question in example_questions:

    st.sidebar.caption(f"• {question}")

st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ Retrieval Pipeline")

st.sidebar.success("Semantic Search")

st.sidebar.success("BM25 Search")

st.sidebar.success("Reciprocal Rank Fusion")

st.sidebar.success("CrossEncoder Reranking")

st.sidebar.success("Gemini 2.5 Flash")

st.sidebar.markdown("---")

st.sidebar.subheader("🛠 Technology Stack")

st.sidebar.markdown(
    """
- Python

- PySpark

- ChromaDB

- BM25

- Sentence Transformers

- CrossEncoder

- Google Gemini

- Streamlit
"""
)

st.sidebar.markdown("---")

st.sidebar.subheader("📊 System Status")

col1, col2 = st.sidebar.columns(2)

with col1:

    st.metric(
        "Backend",
        "Online",
    )

with col2:

    st.metric(
        "LLM",
        "Ready",
    )

st.sidebar.markdown("---")

st.sidebar.info(
    """
Hybrid RAG combines semantic retrieval,
keyword search, Reciprocal Rank Fusion,
and CrossEncoder reranking to improve
product search quality.
"""
)

# ---------------------------------------------------
# Hero Section
# ---------------------------------------------------

st.markdown(
    """
<div class="hero">

<h1>Hybrid RAG Platform for Intelligent Product Search</h1>

<p>
Search Amazon products using a Hybrid Retrieval-Augmented Generation pipeline
combining Semantic Search, BM25, Reciprocal Rank Fusion (RRF), CrossEncoder
Reranking and Google Gemini.
</p>

</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# Dashboard Metrics
# ---------------------------------------------------

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:

    st.markdown(
        """
<div class="metric-card">

<div class="metric-title">
Datasets
</div>

<div class="metric-value">
3
</div>

</div>
""",
        unsafe_allow_html=True,
    )

with metric2:

    st.markdown(
        """
<div class="metric-card">

<div class="metric-title">
Retrieval Strategy
</div>

<div class="metric-value">
Hybrid
</div>

</div>
""",
        unsafe_allow_html=True,
    )

with metric3:

    st.markdown(
        """
<div class="metric-card">

<div class="metric-title">
LLM
</div>

<div class="metric-value">
Gemini 2.5
</div>

</div>
""",
        unsafe_allow_html=True,
    )

with metric4:

    st.markdown(
        """
<div class="metric-card">

<div class="metric-title">
Pipeline
</div>

<div class="metric-value">
Production
</div>

</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# Search Section
# ---------------------------------------------------

st.subheader("🔎 Intelligent Product Search")

query = st.text_area(
    label="",
    placeholder="""
Examples:

• Recommend a quiet dishwasher under $500

• Which gaming controller has the highest ratings?

• Compare two beginner acoustic guitars.

• Which product has the best customer reviews?

• Suggest a gift for a gamer.
""",
    height=140,
)

left, right = st.columns([4, 1])

with left:

    st.caption(
        "Ask natural language questions about Amazon products."
    )

with right:

    search_clicked = st.button(
        "🚀 Search",
        use_container_width=True,
    )

st.markdown("---")


# ---------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------

import time

# Session State

if "result" not in st.session_state:

    st.session_state.result = None

if "execution_time" not in st.session_state:

    st.session_state.execution_time = None


if search_clicked:

    if not query.strip():

        st.warning(
            "Please enter a question before searching."
        )

        st.stop()

    try:

        start_time = time.perf_counter()

        with st.spinner(
            "Searching products and generating response..."
        ):

            pipeline = Pipeline(
                category=category,
            )

            result = pipeline.run(
                query=query,
            )

        end_time = time.perf_counter()

        st.session_state.result = result

        st.session_state.execution_time = (
            end_time - start_time
        )

        st.toast(
            "Search completed successfully!",
            icon="✅",
        )

    except Exception as error:

        st.session_state.result = None

        st.error(
            f"Application Error\n\n{error}"
        )

# ---------------------------------------------------
# Search Statistics
# ---------------------------------------------------

if st.session_state.result:

    execution_time = (
        st.session_state.execution_time
    )

    document_count = len(
        st.session_state.result["documents"]
    )

    st.subheader("📈 Search Statistics")

    stat1, stat2, stat3 = st.columns(3)

    with stat1:

        st.metric(
            "Retrieved Documents",
            document_count,
        )

    with stat2:

        st.metric(
            "Selected Category",
            category,
        )

    with stat3:

        st.metric(
            "Response Time",
            f"{execution_time:.2f} sec",
        )

    st.markdown("---")

# ---------------------------------------------------
# AI Response
# ---------------------------------------------------

if st.session_state.result:

    st.subheader("🤖 AI Generated Answer")

    st.markdown(
        f"""
<div class="answer-card">

{st.session_state.result["answer"]}

</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------
# Retrieved Products
# ---------------------------------------------------

if st.session_state.result:

    st.subheader("📦 Retrieved Products")

    documents = st.session_state.result["documents"]

    for index, product in enumerate(
        documents,
        start=1,
    ):

        product_name = product.get(
            "product_name",
            "Unknown Product",
        )

        category_name = product.get(
            "final_category",
            "Unknown",
        )

        sub_category = product.get(
            "sub_category",
            "Unknown",
        )

        store = product.get(
            "store",
            "Unknown",
        )

        price = product.get(
            "price",
            "N/A",
        )

        rating = product.get(
            "average_rating",
            "N/A",
        )

        reviews = product.get(
            "review_count",
            "N/A",
        )

        description = product.get(
            "product_document",
            "",
        )

        st.markdown(
            f"""
<div class="product-card">

<div class="product-title">

{index}. {product_name}

</div>

<span class="badge">{category_name}</span>

<span class="badge">{sub_category}</span>

<span class="badge">{store}</span>

</div>
""",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "⭐ Rating",
                rating,
            )

        with col2:

            st.metric(
                "📝 Reviews",
                reviews,
            )

        with col3:

            st.metric(
                "💲 Price",
                price,
            )

        with st.expander(
            "View Product Information",
        ):

            st.write(
                description
            )

        st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# Technology Overview
# ---------------------------------------------------

st.markdown("---")

st.subheader("🏗️ System Architecture")

col1, col2 = st.columns(2)

with col1:

    st.info(
        """
### Retrieval Pipeline

User Query

⬇

Semantic Search

⬇

BM25 Search

⬇

Reciprocal Rank Fusion

⬇

CrossEncoder Reranker

⬇

Top Relevant Documents
"""
    )

with col2:

    st.success(
        """
### Generation Pipeline

Retrieved Documents

⬇

Prompt Builder

⬇

Google Gemini 2.5 Flash

⬇

AI Generated Response
"""
    )

# ---------------------------------------------------
# Technology Stack
# ---------------------------------------------------

st.markdown("---")

st.subheader("🛠️ Technology Stack")

tech1, tech2, tech3, tech4 = st.columns(4)

with tech1:

    st.markdown(
        """
### Data Engineering

- PySpark
- Python
- ChromaDB
- BM25
"""
    )

with tech2:

    st.markdown(
        """
### Machine Learning

- Sentence Transformers
- MiniLM-L6-v2
- CrossEncoder
"""
    )

with tech3:

    st.markdown(
        """
### AI

- Google Gemini
- Hybrid RAG
- Prompt Engineering
"""
    )

with tech4:

    st.markdown(
        """
### Frontend

- Streamlit
- Custom CSS
- Interactive Dashboard
"""
    )

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
<div class="footer">

<h4>Hybrid RAG Platform for Intelligent Product Search</h4>

Enterprise Big Data Engineering Project

Powered by Hybrid Retrieval-Augmented Generation

Semantic Search • BM25 • Reciprocal Rank Fusion • CrossEncoder • Gemini 2.5 Flash

</div>
""",
    unsafe_allow_html=True,
)

