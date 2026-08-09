from ml_pipeline.pipeline import Pipeline


def format_score(score):
    """
    Format reranker relevance score.
    """

    if score is None:
        return "N/A"

    try:
        return f"{float(score):.1f}%"

    except Exception:
        return str(score)


def main():

    print("=" * 100)
    print("Amazon Hybrid RAG Test")
    print("=" * 100)

    pipeline = Pipeline(
        category="Appliances",
    )

    while True:

        query = input("\nEnter Query (type 'exit' to quit): ").strip()

        if query.lower() == "exit":
            break

        try:

            result = pipeline.run(query)

            print("\n" + "=" * 100)
            print("ANSWER")
            print("=" * 100)
            print(result["answer"])

            print("\n" + "=" * 100)
            print("TOP RETRIEVED DOCUMENTS")
            print("=" * 100)

            for i, document in enumerate(
                result["documents"],
                start=1,
            ):

                metadata = document.get(
                    "metadata",
                    {},
                )

                print(f"\n{'=' * 100}")
                print(f"RESULT #{i}")
                print(f"{'=' * 100}")

                print(f"Product          : " f"{metadata.get('product_title', 'N/A')}")

                print(f"Store            : " f"{metadata.get('store', 'N/A')}")

                print(f"Category         : " f"{metadata.get('main_category', 'N/A')}")

                print(f"Sub Category     : " f"{metadata.get('sub_category', 'N/A')}")

                print(
                    f"Average Rating   : "
                    f"{metadata.get('product_average_rating', 'N/A')}"
                )

                print(
                    f"Rating Count     : "
                    f"{metadata.get('product_rating_count', 'N/A')}"
                )

                print(
                    f"Review Count     : "
                    f"{metadata.get('product_review_count', 'N/A')}"
                )

                print(f"Parent ASIN      : " f"{metadata.get('parent_asin', 'N/A')}")

                print(
                    f"Image URL        : " f"{metadata.get('product_image_url', 'N/A')}"
                )

                print(
                    f"Relevance        : "
                    f"{format_score(document.get('rerank_score'))}"
                )

                preview = document.get(
                    "document",
                    "",
                )

                if preview:

                    preview = preview.replace(
                        "\n",
                        " ",
                    )

                    if len(preview) > 400:

                        preview = preview[:400] + "..."

                else:

                    preview = "N/A"

                print("\nDocument Preview")
                print("-" * 100)
                print(preview)

                print("\nMetadata Keys")
                print("-" * 100)

                print(
                    sorted(
                        metadata.keys(),
                    )
                )

        except Exception as e:

            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
