from pathlib import Path
import pandas as pd


def main():

    BASE_DIR = Path(__file__).resolve().parent.parent

    FILE_PATH = BASE_DIR / "outputs" / "cleaned_data.parquet"

    if not FILE_PATH.exists():
        print("File not found!")
        print(FILE_PATH)
        return

    df = pd.read_parquet(FILE_PATH)

    print("=" * 60)
    print("DATASET INFORMATION")
    print("=" * 60)

    print(f"Shape: {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nCombined Text Sample:\n")
    print(df["combined_text"].iloc[0])


if __name__ == "__main__":
    main()