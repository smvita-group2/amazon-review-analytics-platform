from pathlib import Path
import pandas as pd
import joblib

from rank_bm25 import BM25Okapi

class BM25Indexer:
    """
    Creates and saves the BM25 index.
    """

    def __init__(self, input_file):

        self.input_file = Path(input_file)

        self.df = None

        self.tokenized_documents = None

        self.bm25 = None

    def load_documents(self):
        """
        Loads product documents.
        """

        print("=" * 60)
        print("LOADING PRODUCT DOCUMENTS")
        print("=" * 60)

        if not self.input_file.exists():
           raise FileNotFoundError(
                f"\nFile not found:\n{self.input_file}"
           )

        self.df = pd.read_parquet(self.input_file)

        print(f"\nRows    : {len(self.df):,}")
        print(f"Columns : {len(self.df.columns)}")

        return self.df
    def inspect_documents(self):
        """
        Displays dataset information.
        """

        print("\n" + "=" * 60)
        print("DOCUMENT INFORMATION")
        print("=" * 60)

        print(f"\nShape : {self.df.shape}")

        print("\nColumns:")

        for column in self.df.columns:
            print(column)

        print("\nSample Document:\n")

        print(self.df["combined_text"].iloc[0][:1000])

    def tokenize_documents(self):
        """
        Tokenizes documents for BM25.
        """

        print("\n" + "=" * 60)
        print("TOKENIZING DOCUMENTS")
        print("=" * 60)

        self.tokenized_documents = [
            document.split()
            for document in self.df["combined_text"]
        ]

        print(f"\nDocuments Tokenized : {len(self.tokenized_documents):,}")

        print("\nFirst 20 Tokens:\n")

        print(self.tokenized_documents[0][:20])
    def build_index(self):
        """
        Builds the BM25 index.
        """

        print("\n" + "=" * 60)
        print("BUILDING BM25 INDEX")
        print("=" * 60)

        self.bm25 = BM25Okapi(self.tokenized_documents)

        print("\n✓ BM25 Index Created Successfully")

    def save_index(self):
        """
        Saves BM25 index.
       """
        print("\n" + "=" * 60)
        print("SAVING BM25 INDEX")
        print("=" * 60)

        output_dir = Path(__file__).resolve().parent.parent / "models"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "bm25_index.pkl"

        joblib.dump(self.bm25, output_file)

        print(f"\n✓ Index Saved Successfully")
        print(f"Location : {output_file}")
def main():

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_FILE = (
        BASE_DIR /
        "outputs" /
        "product_documents.parquet"
    )

    indexer = BM25Indexer(INPUT_FILE)

    indexer.load_documents()

    indexer.inspect_documents()

    indexer.tokenize_documents()

    indexer.build_index()

    indexer.save_index()


if __name__ == "__main__":
    main()