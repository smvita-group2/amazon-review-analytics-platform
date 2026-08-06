"""
Rebuild BM25 Index Only
"""

import pandas as pd

from ml_pipeline.retrieval.bm25_builder import BM25Builder

CATEGORY = "Appliances"

PRODUCT_DOCUMENT_PATH = (
    r"C:\Users\affaa\OneDrive\Desktop\Amazon_RAG_Data"
    r"\product_documents\Appliances\product_documents.parquet"
)


def main():

    print("=" * 60)
    print("Loading Product Documents...")
    print("=" * 60)

    df = pd.read_parquet(
        PRODUCT_DOCUMENT_PATH,
    )

    print(f"Loaded {len(df):,} products")

    print("=" * 60)
    print("Rebuilding BM25 Index...")
    print("=" * 60)

    builder = BM25Builder(
        category=CATEGORY,
    )

    builder.build(df)

    print("=" * 60)
    print("BM25 Index Successfully Rebuilt!")
    print("=" * 60)


if __name__ == "__main__":
    main()