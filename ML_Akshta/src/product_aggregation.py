from pathlib import Path
import pandas as pd


class ProductAggregator:
    """
    Aggregates review-level data into product-level documents.
    """

    def __init__(self, input_file):
        self.input_file = Path(input_file)
        self.df = None
        self.product_df = None

    def load_data(self):
        """
        Loads cleaned_data.parquet.
        """

        print("=" * 60)
        print("LOADING CLEANED DATASET")
        print("=" * 60)

        if not self.input_file.exists():
            raise FileNotFoundError(
                f"\nFile not found:\n{self.input_file}"
            )

        self.df = pd.read_parquet(self.input_file)

        print(f"\nRows    : {len(self.df):,}")
        print(f"Columns : {len(self.df.columns)}")

        return self.df

    def inspect_dataset(self):
        """
        Displays dataset information.
        """

        print("\n" + "=" * 60)
        print("DATASET INFORMATION")
        print("=" * 60)

        print(f"\nShape : {self.df.shape}")

        print("\nUnique Products :", self.df["parent_asin"].nunique())
        print("Total Reviews   :", len(self.df))
    def aggregate_products(self):
        """
        Aggregates reviews into product-level records.
        """

        print("\n" + "=" * 60)
        print("AGGREGATING PRODUCTS")
        print("=" * 60)

        self.product_df = (
            self.df.groupby("parent_asin")
            .agg(
                product_title=("product_title", "first"),
                store=("store", "first"),
                main_category=("main_category", "first"),
                sub_category=("sub_category", "first"),
                product_average_rating=("product_average_rating", "first"),
                product_rating_count=("product_rating_count", "first"),
                description_text=("description_text", "first"),
                features_text=("features_text", "first"),
                product_image_url=("product_image_url", "first"),

                review_title=(
                    "review_title",
                    lambda x: "\n".join(x.astype(str))
                ),

                review_text=(
                    "review_text",
                    lambda x: "\n".join(x.astype(str))
                )
            )
            .reset_index()
        )

        print(f"\nProducts Created : {len(self.product_df):,}")

    def create_combined_text(self):
        """
        Creates retrieval-ready documents.
        """

        print("\n" + "=" * 60)
        print("CREATING PRODUCT DOCUMENTS")
        print("=" * 60)

        self.product_df["combined_text"] = (

            "Product: "
            + self.product_df["product_title"]

            + "\n\nStore: "
            + self.product_df["store"]

            + "\n\nMain Category: "
            + self.product_df["main_category"]

            + "\n\nSub Category: "
            + self.product_df["sub_category"]

            + "\n\nAverage Rating: "
            + self.product_df["product_average_rating"].astype(str)

            + "\n\nTotal Ratings: "
            + self.product_df["product_rating_count"].astype(str)

            + "\n\nDescription:\n"
            + self.product_df["description_text"]

            + "\n\nFeatures:\n"
            + self.product_df["features_text"]

            + "\n\nCustomer Review Titles:\n"
            + self.product_df["review_title"]

            + "\n\nCustomer Reviews:\n"
            + self.product_df["review_text"]
        )

        print("Combined product documents created successfully.")

        print("\nSample Document:\n")
        print(self.product_df["combined_text"].iloc[0][:1200])

    def finalize_dataset(self):
        """
        Keeps only required columns.
        """

        print("\n" + "=" * 60)
        print("FINALIZING DATASET")
        print("=" * 60)

        self.product_df = self.product_df[
            [
                "parent_asin",
                "product_title",
                "store",
                "main_category",
                "sub_category",
                "product_average_rating",
                "product_rating_count",
                "product_image_url",
                "combined_text"
            ]
        ]

        print("\nFinal Columns:")
        print(self.product_df.columns.tolist())

        print(f"\nFinal Shape : {self.product_df.shape}")

    def save_products(self):
        """
        Saves product dataset.
        """

        print("\n" + "=" * 60)
        print("SAVING PRODUCT DATASET")
        print("=" * 60)

        BASE_DIR = Path(__file__).resolve().parent.parent

        OUTPUT_DIR = BASE_DIR / "outputs"
        OUTPUT_DIR.mkdir(exist_ok=True)

        output_file = OUTPUT_DIR / "product_documents.parquet"

        self.product_df.to_parquet(
            output_file,
            index=False
        )

        print("\nSaved Successfully")
        print(output_file)


def main():

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_FILE = (
        BASE_DIR /
        "outputs" /
        "cleaned_data.parquet"
    )

    aggregator = ProductAggregator(INPUT_FILE)

    aggregator.load_data()
    aggregator.inspect_dataset()
     
    aggregator.aggregate_products()
    aggregator.create_combined_text()
    aggregator.finalize_dataset()
    aggregator.save_products()


if __name__ == "__main__":
    main()  