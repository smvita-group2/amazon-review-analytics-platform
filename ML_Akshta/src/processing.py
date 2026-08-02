from pathlib import Path
import pandas as pd
import re


class Preprocessor:
    """
    Performs preprocessing on the merged dataset
    for Hybrid RAG Retrieval System.
    """

    def __init__(self, input_file):
        self.input_file = Path(input_file)
        self.df = None

    def load_data(self):
        """
        Loads the merged parquet dataset.
        """

        print("=" * 60)
        print("LOADING MERGED DATASET")
        print("=" * 60)

        if not self.input_file.exists():
            raise FileNotFoundError(
                f"\nFile not found:\n{self.input_file}"
            )

        self.df = pd.read_parquet(self.input_file)

        print(f"\nRows    : {len(self.df):,}")
        print(f"Columns : {len(self.df.columns)}")

        return self.df

    def inspect_data(self):
        """
        Displays dataset information.
        """

        print("\n" + "=" * 60)
        print("DATASET INSPECTION")
        print("=" * 60)

        print(f"\nDataset Shape : {self.df.shape}")

        print("\nColumns:")
        for column in self.df.columns:
            print(column)

        print("\n" + "=" * 60)
        print("DATA TYPES")
        print("=" * 60)
        print(self.df.dtypes)

        print("\n" + "=" * 60)
        print("MISSING VALUES")
        print("=" * 60)

        missing = self.df.isnull().sum()
        missing = missing[missing > 0]

        if len(missing) == 0:
            print("No Missing Values Found")
        else:
            print(missing.sort_values(ascending=False))

        print("\n" + "=" * 60)
        print("DUPLICATE ROWS")
        print("=" * 60)

        duplicate_rows = self.df.duplicated().sum()

        print(f"Duplicate Rows : {duplicate_rows:,}")

        print("\n" + "=" * 60)
        print("MEMORY USAGE")
        print("=" * 60)

        memory = self.df.memory_usage(deep=True).sum() / (1024 ** 2)

        print(f"{memory:.2f} MB")

        print("\n" + "=" * 60)
        print("NUMERIC SUMMARY")
        print("=" * 60)

        print(self.df.describe())

        print("\n" + "=" * 60)
        print("FIRST 5 RECORDS")
        print("=" * 60)

        print(self.df.head())

    def remove_duplicates(self):
        """
        Removes duplicate rows.
        """

        print("\n" + "=" * 60)
        print("REMOVING DUPLICATES")
        print("=" * 60)

        before = len(self.df)

        self.df = self.df.drop_duplicates()

        after = len(self.df)

        removed = before - after

        print(f"Rows Before : {before:,}")
        print(f"Rows After  : {after:,}")
        print(f"Removed     : {removed:,}")
    def clean_text(self, text):
        """
        Cleans a single text string.
        """

        if pd.isna(text):
           return ""

        text = str(text)

        # Convert to lowercase
        text = text.lower()

        # Remove HTML tags
        text = re.sub(r"<.*?>", " ", text)

        # Remove URLs
        text = re.sub(r"http\S+|www\S+", " ", text)

        # Keep only letters, numbers and spaces
        text = re.sub(r"[^a-z0-9\s]", " ", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()
    def clean_columns(self):
        """
        Cleans all text columns.
        """

        print("\n" + "=" * 60)
        print("CLEANING TEXT COLUMNS")
        print("=" * 60)

        text_columns = [
            "product_title",
            "store",
            "main_category",
            "sub_category",
            "description_text",
            "features_text",
            "review_title",
            "review_text"
         ]

        for column in text_columns:

            print(f"Cleaning: {column}")

            self.df[column] = self.df[column].apply(self.clean_text)

        print("\nText cleaning completed.")
    def create_combined_text(self):
        """
        Creates a single searchable document from multiple text columns.
        """

        print("\n" + "=" * 60)
        print("CREATING COMBINED TEXT")
        print("=" * 60)

        self.df["combined_text"] = (
            "Product: " + self.df["product_title"] + "\n\n"
            + "Store: " + self.df["store"] + "\n\n"
            + "Main Category: " + self.df["main_category"] + "\n\n"
            + "Sub Category: " + self.df["sub_category"] + "\n\n"
            + "Description: " + self.df["description_text"] + "\n\n"
            + "Features: " + self.df["features_text"] + "\n\n"
            + "Review Title: " + self.df["review_title"] + "\n\n"
            + "Review: " + self.df["review_text"]
        )

        print("Combined text created successfully.")

        print("\nSample Combined Text:\n")
        print(self.df["combined_text"].iloc[0][:1000])
    def save_clean_data(self):
        """
        Saves the cleaned dataset.
        """

        print("\n" + "=" * 60)
        print("SAVING CLEANED DATA")
        print("=" * 60)

        BASE_DIR = Path(__file__).resolve().parent.parent

        OUTPUT_DIR = BASE_DIR / "outputs"

        OUTPUT_DIR.mkdir(exist_ok=True)

        output_file = OUTPUT_DIR / "cleaned_data.parquet"

        self.df.to_parquet(
            output_file,
            index=False
        )

        print(f"\nDataset saved successfully!")

        print(f"Location:\n{output_file}")

        print(f"\nFinal Shape: {self.df.shape}")
    
def main():

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_FILE = BASE_DIR / "outputs" / "merged_data.parquet"

    processor = Preprocessor(INPUT_FILE)

    processor.load_data()

    processor.inspect_data()

    processor.remove_duplicates()

    processor.clean_columns()

    processor.create_combined_text()
    
    processor.save_clean_data()
if __name__ == "__main__":
    main()