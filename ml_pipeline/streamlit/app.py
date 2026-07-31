"""
Hybrid RAG Platform for Intelligent Product Search

Enterprise Streamlit Dashboard
"""

import os
import sys
import time

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_pipeline.pipeline import Pipeline  # noqa: E402

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Hybrid RAG Product Search",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# Cache Heavy Objects
# ==========================================================


@st.cache_resource(show_spinner=False)
def load_pipeline(category: str):
    """
    Cache one Pipeline instance per category.
    """
    return Pipeline(category=category)


# ==========================================================
# Session State
# ==========================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "execution_time" not in st.session_state:
    st.session_state.execution_time = None


# ==========================================================
# Custom CSS
# ==========================================================

st.markdown(
    """
<style>

/* ------------------------- */
/* Hide Streamlit Branding */
/* ------------------------- */

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}


/* ------------------------- */
/* Layout */
/* ------------------------- */

.main .block-container{

    max-width:1450px;

    padding-top:2rem;

    padding-bottom:2rem;

}


/* ------------------------- */
/* Sidebar */
/* ------------------------- */

section[data-testid="stSidebar"]{

    background:#111827;

}

section[data-testid="stSidebar"] *{

    color:white;

}


/* ------------------------- */
/* Hero */
/* ------------------------- */

.hero{

    background:linear-gradient(
        135deg,
        #2563EB,
        #4F46E5
    );

    border-radius:20px;

    padding:40px;

    color:white;

    margin-bottom:30px;

    box-shadow:0px 8px 25px rgba(0,0,0,.18);

}

.hero h1{

    font-size:40px;

    margin-bottom:10px;

}

.hero p{

    font-size:18px;

    opacity:.95;

}


/* ------------------------- */
/* Metric Cards */
/* ------------------------- */

.metric-card{

    background:white;

    border-radius:16px;

    padding:22px;

    border:1px solid #E5E7EB;

    box-shadow:0px 4px 14px rgba(0,0,0,.06);

    text-align:center;

}

.metric-title{

    color:#6B7280;

    font-size:14px;

}

.metric-value{

    font-size:30px;

    font-weight:bold;

    color:#2563EB;

}



/* ------------------------- */
/* Product Card */
/* ------------------------- */

.product-card{

    background:white;

    border-radius:18px;

    border:1px solid #E5E7EB;

    padding:22px;

    margin-bottom:20px;

    box-shadow:0px 5px 14px rgba(0,0,0,.08);

}

.product-title{

    font-size:22px;

    font-weight:700;

    color:#1F2937;

}


/* ------------------------- */
/* Badge */
/* ------------------------- */

.badge{

    display:inline-block;

    padding:5px 12px;

    border-radius:12px;

    background:#2563EB;

    color:white;

    margin-right:8px;

    margin-top:10px;

    font-size:12px;

}


/* ------------------------- */
/* Footer */
/* ------------------------- */

.footer{

    text-align:center;

    color:#6B7280;

    margin-top:60px;

}


/* ------------------------- */
/* Buttons */
/* ------------------------- */

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


# ==========================================================
# Sidebar
# ==========================================================

category = "Appliances"

st.sidebar.title("🛒 Hybrid RAG")

st.sidebar.caption("Amazon Appliances Product Search Platform")

st.sidebar.markdown("---")

st.sidebar.success("📂 Category")

st.sidebar.write("**Appliances**")

st.sidebar.markdown("---")

st.sidebar.subheader("💡 Example Queries")

examples = [
    "best black dishwasher",
    "energy efficient refrigerator",
    "front load washing machine",
    "quiet microwave oven",
    "stainless steel gas range",
]

for item in examples:

    st.sidebar.caption(f"• {item}")

st.sidebar.markdown("---")

st.sidebar.subheader("⚙ Retrieval Pipeline")

st.sidebar.success("Sentence Transformers Embeddings")

st.sidebar.success("Semantic Search (ChromaDB)")

st.sidebar.success("BM25 Keyword Search")

st.sidebar.success("Reciprocal Rank Fusion (RRF)")

st.sidebar.success("CrossEncoder Reranking")

st.sidebar.success("Google Gemini 2.5 Flash")

st.sidebar.markdown("---")

st.sidebar.info("""
Search Amazon appliance products using a Hybrid Retrieval-Augmented
Generation (Hybrid RAG) pipeline.

The system combines semantic retrieval with keyword search, fuses both
result sets using Reciprocal Rank Fusion (RRF), reranks the candidates
with a CrossEncoder model, and generates grounded responses using
Google Gemini 2.5 Flash based only on the retrieved product information.
""")

# ==========================================================
# Hero
# ==========================================================

st.markdown(
    """
<div class="hero">

<h1>🛒 Amazon Product Search using Hybrid RAG</h1>

<p>

Intelligent product discovery powered by Semantic Search, BM25,
Reciprocal Rank Fusion (RRF), CrossEncoder reranking and
Google Gemini 2.5 Flash.

</p>

</div>
""",
    unsafe_allow_html=True,
)
# ==========================================================
# Dashboard Metrics
# ==========================================================

m1, m2, m3, m4 = st.columns(4)

cards = [
    ("Category", "Appliances"),
    ("Retrieval", "Hybrid"),
    ("LLM", "Gemini 2.5"),
    ("Status", "Online"),
]

for column, (title, value) in zip(
    [m1, m2, m3, m4],
    cards,
):

    with column:

        st.markdown(
            f"""
<div class="metric-card">

<div class="metric-title">

{title}

</div>

<div class="metric-value">

{value}

</div>

</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# Search Section
# ==========================================================

st.subheader("🔎 Intelligent Product Search")

query = st.text_input(
    label="",
    placeholder="Ask anything about products... (e.g. black dishwasher under $500)",
)

left, middle, right = st.columns([6, 1, 1])

with left:

    st.caption("Natural language product search powered by Hybrid RAG.")

with middle:

    search_clicked = st.button(
        "🔍 Search",
        use_container_width=True,
    )

with right:

    clear_clicked = st.button(
        "🗑 Clear",
        use_container_width=True,
    )


if clear_clicked:

    st.session_state.result = None

    st.session_state.execution_time = None

    st.rerun()


st.markdown("---")


# ==========================================================
# Pipeline Execution
# ==========================================================

if search_clicked:

    if not query.strip():

        st.warning("Please enter a question before searching.")

        st.stop()

    start = time.perf_counter()

    try:

        with st.spinner("Running Hybrid RAG Pipeline..."):

            progress = st.progress(0)

            progress.progress(
                10,
                text="Loading Pipeline...",
            )

            pipeline = load_pipeline(
                category,
            )

            progress.progress(
                30,
                text="Semantic Search...",
            )

            progress.progress(
                50,
                text="BM25 Retrieval...",
            )

            progress.progress(
                65,
                text="Reciprocal Rank Fusion...",
            )

            progress.progress(
                80,
                text="CrossEncoder Reranking...",
            )

            result = pipeline.run(
                query=query,
            )

            progress.progress(
                100,
                text="Generating Answer...",
            )

            progress.empty()

        end = time.perf_counter()

        st.session_state.result = result

        st.session_state.execution_time = end - start

        st.toast(
            "Search Completed",
            icon="✅",
        )

    except Exception as error:

        st.session_state.result = None

        st.error(error)


# ==========================================================
# Results
# ==========================================================

if st.session_state.result:

    result = st.session_state.result
    execution_time = st.session_state.execution_time

    documents = result.get("documents", [])

    answer_tab, products_tab, architecture_tab = st.tabs(
        [
            "💬 AI Answer",
            "📦 Retrieved Products",
            "🏗 Architecture",
        ]
    )

    # ==========================================================
    # AI Answer Tab
    # ==========================================================

    with answer_tab:

        st.subheader("💬 AI Generated Answer")

        answer = result.get(
            "answer",
            "No answer generated.",
        )

        with st.container(border=True):

            st.markdown(answer)

        st.markdown("")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Retrieved Products",
                len(documents),
            )

        with c2:

            st.metric(
                "Category",
                "Appliances",
            )

        with c3:

            st.metric(
                "Response Time",
                f"{execution_time:.2f} sec",
            )

    # ==========================================================
    # Products Tab
    # ==========================================================

    with products_tab:

        st.subheader("📦 Retrieved Products")

        if not documents:

            st.info("No products found.")

        else:

            for index, product in enumerate(
                documents,
                start=1,
            ):

                metadata = product.get(
                    "metadata",
                    {},
                )

                title = metadata.get(
                    "product_title",
                    "Unknown Product",
                )

                store = metadata.get(
                    "store",
                    "Unknown",
                )

                category_name = metadata.get(
                    "main_category",
                    "Unknown",
                )

                sub_category = metadata.get(
                    "sub_category",
                    "Unknown",
                )

                rating = metadata.get(
                    "product_average_rating",
                    0,
                )

                review_count = metadata.get(
                    "product_review_count",
                    0,
                )

                image_url = metadata.get(
                    "product_image_url",
                    "",
                )

                relevance = product.get(
                    "rerank_score",
                    0,
                )

                document = product.get(
                    "document",
                    "",
                )

                with st.container(border=True):

                    left, right = st.columns([1, 3])

                    with left:

                        if image_url:

                            st.image(
                                image_url,
                                width="stretch",
                            )

                        else:

                            st.image(
                                "https://placehold.co/300x300?text=No+Image",
                                width="stretch",
                            )

                    with right:

                        st.markdown(f"### {index}. {title}")

                        st.caption(f"🏪 {store}")

                        st.caption(f"📂 {category_name}")

                        st.caption(f"📁 {sub_category}")

                        m1, m2, m3 = st.columns(3)

                        with m1:

                            st.metric(
                                "⭐ Rating",
                                f"{float(rating):.1f}",
                            )

                        with m2:

                            st.metric(
                                "📝 Reviews",
                                f"{int(review_count):,}",
                            )

                        with m3:

                            st.metric(
                                "🎯 Match",
                                f"{float(relevance):.1f}%",
                            )

                    with st.expander(
                        "🔍 Retrieved Context (RAG)",
                        expanded=False,
                    ):

                        st.code(
                            document,
                            language="text",
                        )

    # ==========================================================
    # Architecture Tab
    # ==========================================================

    with architecture_tab:

        st.subheader("🏗 Hybrid RAG Architecture")

        st.code(
            """
                    User Query
                         │
                         ▼
         Sentence Transformers Embeddings
                         │
                         ▼
           Semantic Search (ChromaDB)
                         │
                         ▼
             BM25 Keyword Search
                         │
                         ▼
      Reciprocal Rank Fusion (RRF)
                         │
                         ▼
         CrossEncoder Reranker
                         │
                         ▼
             Prompt Builder
                         │
                         ▼
        Google Gemini 2.5 Flash
                         │
                         ▼
              Generated Answer
""",
            language="text",
        )

# ==========================================================
# Footer
# ==========================================================

st.markdown("---")

st.markdown(
    """
<div class="footer">

<h3>Hybrid RAG Platform for Intelligent Product Search</h3>

<p>
Enterprise Big Data Engineering Project
</p>


</div>
""",
    unsafe_allow_html=True,
)
