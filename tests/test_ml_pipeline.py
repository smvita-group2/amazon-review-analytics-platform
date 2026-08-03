"""
Unit tests for RAG and ML pipeline components.
"""

import pandas as pd

from ml_pipeline.common.constants import (
    DOCUMENT,
    HELPFUL_VOTE,
    PARENT_ASIN,
    PARENT_ASIN_KEY,
    PRODUCT_AVERAGE_RATING,
    PRODUCT_DOCUMENT,
    PRODUCT_IMAGE_URL,
    PRODUCT_RATING_COUNT,
    PRODUCT_TITLE,
    REVIEW_RATING,
    REVIEW_TEXT,
    REVIEW_TIMESTAMP,
    REVIEW_TITLE,
    STORE,
    VERIFIED_PURCHASE,
)
from ml_pipeline.llm.prompt_builder import PromptBuilder
from ml_pipeline.product_documents.document_builder import ProductDocumentBuilder
from ml_pipeline.product_documents.formatter import ProductDocumentFormatter
from ml_pipeline.product_documents.review_selector import ReviewSelector
from ml_pipeline.retrieval.rrf import ReciprocalRankFusion


def test_reciprocal_rank_fusion():
    """
    Test ReciprocalRankFusion algorithm correctness and rank order.
    """
    semantic_results = [
        {PARENT_ASIN_KEY: "ASIN_1", "score": 0.95},
        {PARENT_ASIN_KEY: "ASIN_2", "score": 0.85},
    ]

    bm25_results = [
        {PARENT_ASIN_KEY: "ASIN_2", "score": 12.5},
        {PARENT_ASIN_KEY: "ASIN_3", "score": 10.1},
    ]

    fused = ReciprocalRankFusion.fuse(
        semantic_results=semantic_results,
        bm25_results=bm25_results,
    )

    assert len(fused) == 3
    # ASIN_2 appears in both lists (rank 2 in semantic, rank 1 in BM25), so it should rank first overall
    assert fused[0][PARENT_ASIN_KEY] == "ASIN_2"


def test_prompt_builder():
    """
    Test PromptBuilder context construction and prompt output.
    """
    documents = [
        {DOCUMENT: "Product 1: Wireless Headphones, Price: $50"},
        {DOCUMENT: "Product 2: Noise Cancelling Earbuds, Price: $80"},
    ]
    query = "Which headphones are under $60?"

    prompt = PromptBuilder.build(query=query, documents=documents)

    assert "USER QUESTION" in prompt
    assert query in prompt
    assert "Wireless Headphones" in prompt
    assert "Noise Cancelling Earbuds" in prompt


def test_review_selector():
    """
    Test ReviewSelector top-helpful and recent review extraction.
    """
    data = {
        HELPFUL_VOTE: [10, 2, 50, 0, 1],
        REVIEW_TIMESTAMP: pd.to_datetime([
            "2023-01-01",
            "2023-05-01",
            "2023-02-01",
            "2023-06-01",
            "2023-04-01",
        ]),
    }
    df = pd.DataFrame(data)

    selector = ReviewSelector()
    selected = selector.select_reviews(df)

    assert len(selected) <= 8


def test_product_document_formatter():
    """
    Test ProductDocumentFormatter formatting output.
    """
    product = pd.Series({
        PRODUCT_TITLE: "Wireless Mouse",
        STORE: "Logitech",
        PRODUCT_AVERAGE_RATING: 4.8,
        PRODUCT_RATING_COUNT: 1500,
        "main_category": "Electronics",
        "sub_category": "Accessories",
    })
    reviews = pd.DataFrame({
        REVIEW_TITLE: ["Great"],
        REVIEW_TEXT: ["Smooth sensor"],
        REVIEW_RATING: [5],
        VERIFIED_PURCHASE: [True],
        HELPFUL_VOTE: [10],
    })

    formatter = ProductDocumentFormatter()
    doc = formatter.build_document(
        product=product,
        reviews=reviews,
        description="Ergonomic optical mouse",
        features="USB-C rechargeable",
    )

    assert "Wireless Mouse" in doc
    assert "Logitech" in doc
    assert "Ergonomic optical mouse" in doc


def test_product_document_builder():
    """
    Test ProductDocumentBuilder document dataframe output.
    """
    df = pd.DataFrame({
        PARENT_ASIN: ["ASIN100", "ASIN100"],
        PRODUCT_TITLE: ["Smart Speaker", "Smart Speaker"],
        STORE: ["Amazon", "Amazon"],
        "main_category": ["Electronics", "Electronics"],
        "sub_category": ["Speakers", "Speakers"],
        PRODUCT_AVERAGE_RATING: [4.6, 4.6],
        PRODUCT_RATING_COUNT: [500, 500],
        PRODUCT_IMAGE_URL: ["http://img.url", "http://img.url"],
        "description_text": ["Voice controlled", "Voice controlled"],
        "features_text": ["Alexa built-in", "Alexa built-in"],
        REVIEW_RATING: [5, 4],
        REVIEW_TITLE: ["Awesome", "Good"],
        REVIEW_TEXT: ["Love it", "Decent sound"],
        VERIFIED_PURCHASE: [True, True],
        HELPFUL_VOTE: [10, 2],
        REVIEW_TIMESTAMP: pd.to_datetime(["2023-01-01", "2023-02-01"]),
    })

    builder = ProductDocumentBuilder()
    doc_df = builder.build_documents(df)

    assert len(doc_df) == 1
    assert doc_df.iloc[0][PARENT_ASIN] == "ASIN100"
    assert PRODUCT_DOCUMENT in doc_df.columns
