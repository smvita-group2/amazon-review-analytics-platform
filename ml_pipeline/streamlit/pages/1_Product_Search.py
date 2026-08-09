"""
Hybrid RAG Platform for Intelligent Product Search
Amazon Review Intelligence Theme
Connected directly to real production backend RAG pipeline & evaluation modules.
"""

import os
import sys
import time
import streamlit as st

# Ensure parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from theme import (
    inject_amazon_theme,
    render_custom_sidebar,
    render_top_navbar,
)

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
    page_title="Product Search - Amazon Review Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Amazon CSS Theme
inject_amazon_theme()

# Render custom sidebar with moving logo at the VERY TOP
render_custom_sidebar(active_page="Product_Search")

# Render top navbar with active Product Search tab
render_top_navbar(active_tab="search")


# Cache Heavy Pipeline Objects
@st.cache_resource(show_spinner=False)
def load_pipeline(category: str) -> Pipeline:
    """Cache one Pipeline instance per category."""
    return Pipeline(category=category)


@st.cache_resource(show_spinner=False)
def warmup() -> None:
    """Warm up default category on startup."""
    try:
        load_pipeline(CATEGORIES[0])
    except Exception as e:
        print(f"Warmup notice: {e}")


# Warmup default category
warmup()


# Session State Setup
if "result" not in st.session_state:
    st.session_state.result = None

if "execution_time" not in st.session_state:
    st.session_state.execution_time = None

if "category" not in st.session_state:
    st.session_state.category = CATEGORIES[0]

initial_query = st.session_state.get("search_query_initial", "")

# ==========================================================
# Hero Header Banner
# ==========================================================

st.markdown(
    """<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);"><div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;"><div><h1 style="font-size: 24px; font-weight: 800; color: #131921; margin: 0; display: flex; align-items: center; gap: 10px;">🛒 Intelligent Product Search</h1><div style="font-size: 13.5px; color: #64748B; margin-top: 4px;">Powered by Hybrid RAG (Sentence Transformers + BM25 + RRF + CrossEncoder + Gemini 3.5 Flash-lite)</div></div><div style="display: flex; gap: 8px;"><span class="tech-pill">🔑 Semantic Search</span><span class="tech-pill">🔤 BM25</span><span class="tech-pill">✦ Gemini 3.5</span></div></div></div>""",
    unsafe_allow_html=True,
)

# ==========================================================
# Search Controls Bar
# ==========================================================

c_cat, c_input = st.columns([1, 2.5])

with c_cat:
    selected_cat = st.selectbox(
        "📁 Product Category",
        CATEGORIES,
        key="category_select_box",
    )

with c_input:
    query = st.text_input(
        "🔎 Search Query",
        value=initial_query,
        placeholder=f"Search in {selected_cat.replace('_', ' ')}...",
        key="search_query_box",
    )

btn_c1, btn_c2, _ = st.columns([1, 1, 3])

with btn_c1:
    search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

with btn_c2:
    clear_clicked = st.button("🗑️ Clear", type="secondary", use_container_width=True)

if clear_clicked:
    st.session_state.result = None
    st.session_state.execution_time = None
    if "search_query_initial" in st.session_state:
        del st.session_state["search_query_initial"]
    st.rerun()

# Execute search against production RAG pipeline
if search_clicked or (initial_query and not st.session_state.result):
    target_q = query.strip() if query.strip() else (initial_query.strip() if initial_query else "refrigerator water filter")
    
    start = time.perf_counter()
    with st.spinner("Running Hybrid RAG Search Pipeline..."):
        pipeline = load_pipeline(selected_cat)
        res = pipeline.run(query=target_q)
            
    end = time.perf_counter()
    st.session_state.result = res
    st.session_state.execution_time = end - start
    st.toast("Search Completed Successfully", icon="✅")

# Clear initial search query state
if "search_query_initial" in st.session_state:
    del st.session_state["search_query_initial"]

# ==========================================================
# Results Display
# ==========================================================

if st.session_state.result:
    result = st.session_state.result
    execution_time = st.session_state.execution_time
    documents = result.get("documents", [])
    ans_text = result.get("answer", "No answer generated.")
    tokens = result.get("total_tokens", 0)

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #D9E2EC;'>", unsafe_allow_html=True)

    # 4 Clean Top Tabs
    products_tab, answer_tab, evaluation_tab, architecture_tab = st.tabs(
        [
            "📦 Retrieved Products",
            "💬 AI Generated Answer",
            "📊 RAG Evaluation",
            "🏗 Architecture",
        ]
    )

    # ------------------------------------------------------
    # Tab 1: Retrieved Products
    # ------------------------------------------------------
    with products_tab:
        st.markdown(
            f"""<div style="font-size: 19px; font-weight: 800; color: #172033; margin-bottom: 14px; margin-top: 4px; display: flex; align-items: center; gap: 8px;">📦 Retrieved Products ({len(documents)})</div>""",
            unsafe_allow_html=True,
        )

        if not documents:
            st.info("No products found for this query.")
        else:
            for idx, doc in enumerate(documents, start=1):
                metadata = doc.get("metadata", doc)
                title = metadata.get("product_title", doc.get("title", f"Product #{idx}"))
                store = metadata.get("store", doc.get("store", "Amazon Brand"))
                main_cat = metadata.get("main_category", doc.get("main_category", selected_cat))
                sub_cat = metadata.get("sub_category", doc.get("sub_category", "General Products"))
                avg_rating = metadata.get("product_average_rating", doc.get("average_rating", 0))
                reviews_cnt = metadata.get("product_review_count", doc.get("rating_number", 0))
                img_url = metadata.get("product_image_url", doc.get("image_url", ""))
                parent_asin = metadata.get("parent_asin", doc.get("parent_asin", "N/A"))
                document_text = doc.get("document", doc.get("description", ""))

                # Product Card Container
                col_img, col_info = st.columns([1.2, 3], gap="medium")

                with col_img:
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.image("https://placehold.co/300x300?text=No+Image", use_container_width=True)

                with col_info:
                    st.markdown(
                        f"""<h3 style="font-size: 18px; font-weight: 800; color: #172033; margin-top: 0; margin-bottom: 10px;">{idx}. {title}</h3>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""<div style="font-size: 13.5px; color: #475569; margin-bottom: 6px;">🏬 <b>Store:</b> {store}</div>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""<div style="font-size: 13.5px; color: #475569; margin-bottom: 6px;">📁 <b>Main Category:</b> {main_cat}</div>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""<div style="font-size: 13px; color: #64748B; margin-bottom: 14px;">📂 <b>Sub Category:</b> {sub_cat}</div>""",
                        unsafe_allow_html=True,
                    )

                    # Rating & Review badges
                    st.markdown(
                        f"""<div style="display: flex; gap: 12px; align-items: center;"><div style="background: #FFF3E0; border: 1px solid #FF9900; color: #B45309; font-weight: 800; padding: 6px 14px; border-radius: 20px; font-size: 13.5px; display: inline-flex; align-items: center; gap: 6px;">⭐ Rating: <b>{float(avg_rating):.1f}</b></div><div style="background: #EAF3FB; border: 1px solid #B8D5EE; color: #146EB4; font-weight: 800; padding: 6px 14px; border-radius: 20px; font-size: 13.5px; display: inline-flex; align-items: center; gap: 6px;">📄 Reviews: <b>{int(reviews_cnt):,}</b></div></div>""",
                        unsafe_allow_html=True,
                    )

                # Collapsible RAG Context Accordion
                with st.expander(f"🔍 Retrieved Context (RAG) - ASIN: {parent_asin}"):
                    st.code(document_text, language="text")

                st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #D9E2EC;'>", unsafe_allow_html=True)

    # ------------------------------------------------------
    # Tab 2: AI Generated Answer
    # ------------------------------------------------------
    with answer_tab:
        st.subheader("💬 AI Generated Answer (Gemini 3.5 Flash-lite)")
        st.markdown(
            f"""<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 14px; padding: 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); margin-bottom: 20px; font-size: 15px; color: #172033; line-height: 1.6;">{ans_text}</div>""",
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Retrieved Products", len(documents))
        m2.metric("Category", selected_cat.replace("_", " "))
        m3.metric("Tokens Consumed", f"{int(tokens):,}")
        m4.metric("Response Time", f"{execution_time:.2f}s" if execution_time else "0.0s")

    # ------------------------------------------------------
    # Tab 3: RAG Evaluation (Real Faithfulness & Relevance)
    # ------------------------------------------------------
    with evaluation_tab:
        # A. RETRIEVAL RELEVANCE SECTION
        st.markdown(
            """<div style="font-size: 22px; font-weight: 800; color: #172033; margin-bottom: 4px;">🎯 Retrieval Relevance</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            """<div style="font-size: 14px; color: #64748B; margin-bottom: 16px;">Evaluates whether the top retrieved products are relevant to the user's query.</div>""",
            unsafe_allow_html=True,
        )

        if st.button("🔍 Evaluate Retrieval Relevance", type="primary", key="btn_eval_rel"):
            with st.spinner("Evaluating retrieval relevance with LLM..."):
                relevance_result = RetrievalRelevanceEvaluator.evaluate(
                    query=result.get("query", query),
                    documents=documents[:5],
                )
                st.session_state.relevance_result = relevance_result
                st.toast("Retrieval Relevance Evaluated!", icon="🎯")

        rel_res = st.session_state.get("relevance_result", {})
        if rel_res:
            rel_score = rel_res.get("score", 0.0)
            rel_prods = rel_res.get("relevant_products", 0)
            tot_prods = rel_res.get("total_products", len(documents[:5]))
            prod_analysis = rel_res.get("product_analysis", [])

            rel_c1, rel_c2, rel_c3 = st.columns(3)
            with rel_c1:
                st.metric("Retrieval Relevance", f"{rel_score:.1f}%")
            with rel_c2:
                st.metric("Relevant Products", rel_prods)
            with rel_c3:
                st.metric("Retrieved Products", tot_prods)

            st.markdown("### Calculation")
            st.code(
                f"Retrieval Relevance = Relevant Products / Retrieved Products × 100\n= {rel_prods} / {tot_prods} × 100\n= {rel_score:.2f}%",
                language="text",
            )

            if prod_analysis:
                st.markdown("### Product Analysis")
                for prod in prod_analysis:
                    p_idx = prod.get("product_index", 1)
                    p_title = prod.get("product_title", f"Product #{p_idx}")
                    is_rel = prod.get("relevant", False)
                    p_reason = prod.get("reason", "")

                    if is_rel:
                        st.markdown(
                            f"""<div style="background: #DCFCE7; border: 1px solid #A7F3D0; border-radius: 12px; padding: 16px; margin-bottom: 12px;"><div style="color: #15803D; font-weight: 800; font-size: 15px; margin-bottom: 6px;">✓ Relevant</div><div style="color: #172033; font-weight: 700; font-size: 14px; margin-bottom: 4px;">Product {p_idx}: {p_title}</div><div style="color: #475569; font-size: 13px;"><b>Reason:</b> {p_reason}</div></div>""",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""<div style="background: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 12px; padding: 16px; margin-bottom: 12px;"><div style="color: #B91C1C; font-weight: 800; font-size: 15px; margin-bottom: 6px;">✗ Not Relevant</div><div style="color: #172033; font-weight: 700; font-size: 14px; margin-bottom: 4px;">Product {p_idx}: {p_title}</div><div style="color: #475569; font-size: 13px;"><b>Reason:</b> {p_reason}</div></div>""",
                            unsafe_allow_html=True,
                        )

        st.markdown("<hr style='margin: 28px 0; border: none; border-top: 1px solid #D9E2EC;'>", unsafe_allow_html=True)

        # B. FAITHFULNESS SECTION
        st.markdown(
            """<div style="font-size: 22px; font-weight: 800; color: #172033; margin-bottom: 4px;">💬 Faithfulness</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            """<div style="font-size: 14px; color: #64748B; margin-bottom: 16px;">Evaluate whether the generated answer is supported by the retrieved product context.</div>""",
            unsafe_allow_html=True,
        )

        if st.button("🔍 Evaluate Faithfulness", type="primary", key="btn_eval_faith"):
            with st.spinner("Evaluating response faithfulness with LLM..."):
                faithfulness_result = FaithfulnessEvaluator.evaluate(
                    answer=ans_text,
                    documents=documents,
                )
                st.session_state.faithfulness_result = faithfulness_result
                st.toast("Faithfulness Evaluated!", icon="💬")

        faith_res = st.session_state.get("faithfulness_result", {})
        if faith_res:
            faith_score = faith_res.get("score")
            supp_claims = faith_res.get("supported_claims", 0)
            tot_claims = faith_res.get("total_claims", 0)
            claim_analysis = faith_res.get("claim_analysis", [])

            faith_c1, faith_c2, faith_c3 = st.columns(3)
            with faith_c1:
                st.metric("Faithfulness Score", f"{faith_score:.1f}%" if faith_score is not None else "N/A")
            with faith_c2:
                st.metric("Supported Claims", supp_claims)
            with faith_c3:
                st.metric("Total Claims", tot_claims)

            if tot_claims > 0 and faith_score is not None:
                st.markdown("### Calculation")
                st.code(
                    f"Faithfulness = Supported Claims / Total Claims × 100\n= {supp_claims} / {tot_claims} × 100\n= {faith_score:.2f}%",
                    language="text",
                )

            if claim_analysis:
                st.markdown("### Claim Analysis")
                for claim in claim_analysis:
                    c_text = claim.get("claim", "")
                    is_supp = claim.get("supported", False)
                    evidence = claim.get("evidence", "No evidence found")

                    if is_supp:
                        st.markdown(
                            f"""<div style="background: #DCFCE7; border: 1px solid #A7F3D0; border-radius: 12px; padding: 16px; margin-bottom: 10px;"><div style="color: #15803D; font-weight: 800; font-size: 14px; margin-bottom: 4px;">✓ Supported</div><div style="color: #172033; font-weight: 700; font-size: 13.5px;">Claim: {c_text}</div><div style="color: #475569; font-size: 12.5px; margin-top: 2px;"><b>Evidence:</b> {evidence}</div></div>""",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""<div style="background: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 12px; padding: 16px; margin-bottom: 10px;"><div style="color: #B91C1C; font-weight: 800; font-size: 14px; margin-bottom: 4px;">✗ Not Supported</div><div style="color: #172033; font-weight: 700; font-size: 13.5px;">Claim: {c_text}</div><div style="color: #475569; font-size: 12.5px; margin-top: 2px;"><b>Evidence:</b> {evidence}</div></div>""",
                            unsafe_allow_html=True,
                        )

    # ------------------------------------------------------
    # Tab 4: Architecture (Clean Compact Vertical System Flow)
    # ------------------------------------------------------
    with architecture_tab:
        st.markdown(
            """<div style="font-size: 22px; font-weight: 800; color: #172033; margin-bottom: 4px;">🏗 Hybrid RAG Architecture & Execution Flow</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            """<div style="font-size: 14px; color: #64748B; margin-bottom: 24px;">End-to-end multi-stage pipeline connecting dense vector search, sparse BM25 keyword matching, Reciprocal Rank Fusion, CrossEncoder reranking, and Gemini 3.5 Flash-lite.</div>""",
            unsafe_allow_html=True,
        )

        arch_flow_html = """<div style="max-width: 640px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 4px;">

<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="font-size: 16px;">🔍</div>
<div style="font-size: 14px; font-weight: 800; color: #131921;">User Query</div>
<div style="font-size: 11.5px; color: #64748B;">Natural Language Product Search</div>
</div>

<div style="font-size: 18px; color: #FF9900; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="font-size: 16px;">🧠</div>
<div style="font-size: 14px; font-weight: 800; color: #172033;">Sentence Transformers</div>
<div style="font-size: 11.5px; color: #64748B;">Embedding Generation</div>
</div>

<div style="font-size: 18px; color: #2563EB; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 2px dashed #2563EB; border-radius: 14px; padding: 16px; width: 100%; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.05);">
<div style="font-size: 12px; font-weight: 800; color: #2563EB; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 12px; text-align: center;">⚡ HYBRID RETRIEVAL STAGE</div>
<div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center;">
<div style="background: #EAF3FB; border: 1px solid #B8D5EE; border-radius: 10px; padding: 12px; text-align: center;">
<div style="font-size: 18px;">🧠</div>
<div style="font-size: 13.5px; font-weight: 800; color: #146EB4;">Semantic Search</div>
<div style="font-size: 11px; color: #475569; margin-top: 2px;">(ChromaDB Vector)</div>
</div>
<div style="font-size: 18px; font-weight: 900; color: #2563EB;">+</div>
<div style="background: #EAF3FB; border: 1px solid #B8D5EE; border-radius: 10px; padding: 12px; text-align: center;">
<div style="font-size: 18px;">🔤</div>
<div style="font-size: 13.5px; font-weight: 800; color: #146EB4;">BM25 Search</div>
<div style="font-size: 11px; color: #475569; margin-top: 2px;">Keyword Index</div>
</div>
</div>
</div>

<div style="font-size: 18px; color: #7C3AED; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="font-size: 16px;">🔀</div>
<div style="font-size: 14px; font-weight: 800; color: #7C3AED;">Reciprocal Rank Fusion</div>
<div style="font-size: 11.5px; color: #64748B;">RRF Merge</div>
</div>

<div style="font-size: 18px; color: #7C3AED; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="font-size: 16px;">⚡</div>
<div style="font-size: 14px; font-weight: 800; color: #7C3AED;">CrossEncoder Reranker</div>
<div style="font-size: 11.5px; color: #64748B;">Deep Relevance Scoring</div>
</div>

<div style="font-size: 18px; color: #15803D; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="font-size: 16px;">📝</div>
<div style="font-size: 14px; font-weight: 800; color: #172033;">Prompt Builder</div>
<div style="font-size: 11.5px; color: #64748B;">Context Templating</div>
</div>

<div style="font-size: 18px; color: #15803D; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #FFFFFF; border: 2px solid #15803D; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px; box-shadow: 0 4px 10px rgba(21, 128, 61, 0.12);">
<div style="font-size: 16px;">✨</div>
<div style="font-size: 14px; font-weight: 800; color: #15803D;">Google Gemini 3.5 Flash-lite</div>
<div style="font-size: 11.5px; color: #64748B;">LLM Generation</div>
</div>

<div style="font-size: 18px; color: #15803D; font-weight: bold; line-height: 1;">↓</div>

<div style="background: #ECFDF3; border: 1px solid #A7F3D0; border-radius: 12px; padding: 10px 24px; text-align: center; width: 280px;">
<div style="font-size: 16px;">💬</div>
<div style="font-size: 14px; font-weight: 800; color: #15803D;">Generated Answer</div>
<div style="font-size: 11.5px; color: #334155;">Cited Response</div>
</div>

</div>"""

        st.markdown(arch_flow_html, unsafe_allow_html=True)

# Footer
st.markdown(
    """<div class="platform-footer"><b>Amazon Review Intelligence Platform</b> • Built with Streamlit, Hybrid RAG & Gemini 3.5</div>""",
    unsafe_allow_html=True,
)
