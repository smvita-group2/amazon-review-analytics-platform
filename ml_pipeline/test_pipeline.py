from pipeline import Pipeline


def format_score(score):

    if score is None:
        return "N/A"

    try:
        score = float(score)

        # Semantic scores are already between 0 and 1
        if 0.0 <= score <= 1.0:
            return f"{score * 100:.1f}%"

        # BM25 / CrossEncoder raw scores
        return f"{score:.3f}"

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

            for i, document in enumerate(result["documents"], start=1):

                metadata = document.get("metadata", {})

                print(f"\n{'=' * 100}")
                print(f"RESULT #{i}")
                print(f"{'=' * 100}")

                print(f"Product          : {metadata.get('product_title', 'N/A')}")
                print(f"Store            : {metadata.get('store', 'N/A')}")
                print(f"Category         : {metadata.get('main_category', 'N/A')}")
                print(f"Sub Category     : {metadata.get('sub_category', 'N/A')}")

                print(f"Average Rating   : {metadata.get('product_average_rating', 'N/A')}")
                print(f"Rating Count     : {metadata.get('product_rating_count', 'N/A')}")
                print(f"Review Count     : {metadata.get('product_review_count', 'N/A')}")

                print(f"Parent ASIN      : {metadata.get('parent_asin', 'N/A')}")

                print(f"Image URL        : {metadata.get('product_image_url', 'N/A')}")

                score = (
                    document.get("rerank_score")
                    or document.get("similarity_score")
                )

                print(f"Score            : {format_score(score)}")

                preview = document.get("document", "")

                if preview:

                    preview = preview.replace("\n", " ")

                    if len(preview) > 350:
                        preview = preview[:350] + "..."

                else:

                    preview = "N/A"

                print("\nDocument Preview")
                print("-" * 100)
                print(preview)

                print("\nMetadata Keys")
                print("-" * 100)
                print(sorted(metadata.keys()))

        except Exception as e:

            print(f"\nError: {e}")


if __name__ == "__main__":
    main()