"""
Hybrid RAG Platform for Intelligent Product Search

Enterprise Streamlit Dashboard
"""

import time

import streamlit as st

from ml_pipeline.common.constants import CATEGORIES
from ml_pipeline.evaluation.faithfulness import FaithfulnessEvaluator
from ml_pipeline.evaluation.retrieval_relevance import (
    RetrievalRelevanceEvaluator,
)
from ml_pipeline.pipeline import Pipeline

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
def load_pipeline(
    category: str,
) -> Pipeline:
    """
    Cache one Pipeline instance per category.
    """

    return Pipeline(
        category=category,
    )


@st.cache_resource(show_spinner=False)
def warmup() -> None:
    """
    Warm up the default category so the first search
    avoids most of the cold-start initialization.
    """

    load_pipeline(
        CATEGORIES[0],
    )


# Execute once when the application starts
warmup()


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

    padding-top:1rem;

    padding-bottom:1.5rem;

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

    padding:30px;

    color:white;

    margin-bottom:18px;

    box-shadow:0px 8px 25px rgba(0,0,0,.18);

}

.hero h1{

    font-size:38px;

    margin-bottom:8px;

}

.hero p{

    font-size:17px;

    opacity:.95;

}


/* ------------------------- */
/* Metric Cards */
/* ------------------------- */

.metric-card{

    background:white;

    border-radius:16px;

    padding:18px;

    border:1px solid #E5E7EB;

    box-shadow:0px 4px 14px rgba(0,0,0,.06);

    text-align:center;

}

.metric-title{

    color:#6B7280;

    font-size:13px;

    margin-bottom:6px;

}

.metric-value{

    font-size:28px;

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

    padding:20px;

    margin-bottom:16px;

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

    margin-top:8px;

    font-size:12px;

}


/* ------------------------- */
/* Footer */
/* ------------------------- */

.footer{

    text-align:center;

    color:#6B7280;

    margin-top:35px;

}


/* ------------------------- */
/* Buttons */
/* ------------------------- */

div.stButton > button{

    width:100%;

    height:48px;

    font-size:17px;

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
# Default Category
# ==========================================================

if "category" not in st.session_state:

    st.session_state.category = CATEGORIES[0]

category = st.session_state.category

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
Google Gemini 3.5 Flash-lite.

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
    ("Category", category.replace("_", " ")),
    ("Retrieval", "Hybrid RAG"),
    ("LLM", "Gemini 3.5 Flash-L"),
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

category = st.selectbox(
    "📂 Product Category",
    CATEGORIES,
    key="category",
)

if category == "Appliances":

    placeholder = (
        "Ask anything about appliances... "
        "(e.g. best refrigerator water filter, quiet dishwasher)"
    )

    examples = [
        "Whirlpool refrigerator water filter",
        "Dishwasher replacement basket",
        "Products that improve water quality",
    ]


elif category == "Video_Games":

    placeholder = (
        "Ask anything about video games... "
        "(e.g. highest rated PS5 game, Nintendo Switch racing game)"
    )

    examples = [
        "Best PS5 controller",
        "Highest rated PlayStation game",
        "Nintendo Switch racing game",
    ]


elif category == "Musical_Instruments":

    placeholder = (
        "Ask anything about musical instruments... "
        "(e.g. best acoustic guitar, beginner keyboard)"
    )

    examples = [
        "Best acoustic guitar",
        "Beginner keyboard",
        "Studio microphone",
    ]


st.caption("💡 Example Searches: " + " • ".join(examples))

query = st.text_input(
    label="Product Search",
    label_visibility="collapsed",
    placeholder=placeholder,
)

left, middle, right = st.columns([6, 1, 1])

with left:

    st.caption(
        "Search products using Hybrid RAG "
        "(Semantic Search + BM25 + RRF + CrossEncoder)."
    )

with middle:

    search_clicked = st.button(
        "🔍 Search",
        type="primary",
        use_container_width=True,
    )

with right:

    clear_clicked = st.button(
        "🗑️ Clear",
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
                text="Preparing Search...",
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

    documents = result.get(
        "documents",
        [],
    )

    products_tab, answer_tab, evaluation_tab, architecture_tab = st.tabs(
        [
            "📦 Retrieved Products",
            "💬 AI Generated Answer",
            "📊 Evaluation",
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

        total_tokens = result.get(
            "total_tokens",
            0,
        )

        with st.container(border=True):

            st.markdown(answer)

        st.markdown("")

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Retrieved Products",
                len(documents),
            )

        with c2:

            st.metric(
                "Category",
                category.replace("_", " "),
            )

        with c3:

            st.metric(
                "Response Time",
                f"{execution_time:.2f} sec",
            )

        with c4:

            st.metric(
                "Tokens Consumed",
                f"{int(total_tokens):,}",
            )

    # ==========================================================
    # Evaluation Tab
    # ==========================================================

    with evaluation_tab:

        st.subheader("📊 RAG Evaluation")

        st.write(
            "Evaluate whether the generated answer is "
            "supported by the retrieved product context."
        )

        if st.button(
            "🔍 Evaluate Faithfulness",
            type="primary",
        ):

            with st.spinner("Evaluating response faithfulness..."):

                faithfulness_result = FaithfulnessEvaluator.evaluate(
                    answer=answer,
                    documents=documents,
                )

            # ======================================================
            # Evaluation Results
            # ======================================================

            score = faithfulness_result.get(
                "score",
            )

            supported_claims = faithfulness_result.get(
                "supported_claims",
                0,
            )

            total_claims = faithfulness_result.get(
                "total_claims",
                0,
            )

            unsupported_claims = faithfulness_result.get(
                "unsupported_claims",
                [],
            )

            claim_analysis = faithfulness_result.get(
                "claim_analysis",
                [],
            )

            # ======================================================
            # Faithfulness Score
            # ======================================================

            st.markdown("### Faithfulness Score")

            if score is not None:

                st.metric(
                    "Faithfulness",
                    f"{score:.1f}%",
                )

            else:

                st.info(
                    "No factual claims were detected, "
                    "so a faithfulness score cannot be calculated."
                )

            # ======================================================
            # Claim Metrics
            # ======================================================

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Supported Claims",
                    supported_claims,
                )

            with c2:

                st.metric(
                    "Total Claims",
                    total_claims,
                )

            # ======================================================
            # Formula
            # ======================================================

            if total_claims > 0:

                st.markdown("### Calculation")

                st.code(
                    f"""Faithfulness = Supported Claims / Total Claims × 100

= {supported_claims} / {total_claims} × 100

= {score:.2f}%
""".strip(),
                    language="text",
                )

            # ======================================================
            # Claim Analysis
            # ======================================================

            if claim_analysis:

                st.markdown("### Claim Analysis")

                for claim in claim_analysis:

                    claim_text = claim.get(
                        "claim",
                        "",
                    )

                    supported = claim.get(
                        "supported",
                        False,
                    )

                    evidence = claim.get(
                        "evidence",
                        "",
                    )

                    if supported:

                        st.success(
                            f"✓ Supported\n\n"
                            f"**Claim:** {claim_text}\n\n"
                            f"**Evidence:** {evidence}"
                        )

                    else:

                        st.error(
                            f"✗ Unsupported\n\n"
                            f"**Claim:** {claim_text}\n\n"
                            f"**Evidence:** "
                            f"{evidence if evidence else'No supporting evidence found'}"
                        )

        # ==========================================================
        # Retrieval Relevance
        # ==========================================================

        st.markdown("---")

        st.subheader("🎯 Retrieval Relevance")

        st.write(
            "Evaluates whether the top 5 retrieved products "
            "are relevant to the user's query."
        )

        if st.button(
            "🔍 Evaluate Retrieval Relevance",
            type="secondary",
        ):

            with st.spinner("Evaluating retrieved products..."):

                relevance_result = RetrievalRelevanceEvaluator.evaluate(
                    query=query,
                    documents=documents[:5],
                )

            relevance_score = relevance_result.get(
                "score",
            )

            relevant_products = relevance_result.get(
                "relevant_products",
                0,
            )

            total_products = relevance_result.get(
                "total_products",
                0,
            )

            product_analysis = relevance_result.get(
                "product_analysis",
                [],
            )

            # ======================================================
            # Relevance Score
            # ======================================================

            st.markdown("### Retrieval Relevance Score")

            if relevance_score is not None:

                st.metric(
                    "Retrieval Relevance",
                    f"{relevance_score:.1f}%",
                )

            else:

                st.info("Retrieval relevance could not be calculated.")

            # ======================================================
            # Product Metrics
            # ======================================================

            r1, r2 = st.columns(2)

            with r1:

                st.metric(
                    "Relevant Products",
                    relevant_products,
                )

            with r2:

                st.metric(
                    "Retrieved Products",
                    total_products,
                )

            # ======================================================
            # Formula
            # ======================================================

            if total_products > 0:

                st.markdown("### Calculation")

                st.code(
                    f"""Retrieval Relevance =
Relevant Products / Retrieved Products × 100

= {relevant_products} / {total_products} × 100

= {relevance_score:.2f}%
""".strip(),
                    language="text",
                )

            # ======================================================
            # Product Analysis
            # ======================================================

            if product_analysis:

                st.markdown("### Product Analysis")

                for product in product_analysis:

                    product_index = product.get(
                        "product_index",
                        0,
                    )

                    product_title = product.get(
                        "product_title",
                        "Unknown Product",
                    )

                    relevant = product.get(
                        "relevant",
                        False,
                    )

                    reason = product.get(
                        "reason",
                        "",
                    )

                    if relevant:

                        st.success(
                            f"✓ Relevant\n\n"
                            f"**Product {product_index}:** "
                            f"{product_title}\n\n"
                            f"**Reason:** {reason}"
                        )

                    else:

                        st.error(
                            f"✗ Not Relevant\n\n"
                            f"**Product {product_index}:** "
                            f"{product_title}\n\n"
                            f"**Reason:** {reason}"
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

                        m1, m2 = st.columns(2)

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
        Google Gemini 3.5 Flash-lite LLM
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
