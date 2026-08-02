from pathlib import Path
import pandas as pd


class DataLoader:
    """
    Loads all parquet files from the specified folder
    and merges them into a single DataFrame.
    """

    def __init__(self, data_folder):
        self.data_folder = Path(data_folder)

    def load_data(self):
        """
        Reads all parquet files from the folder and
        returns a merged DataFrame.
        """

        print(f"\nSearching for parquet files in:\n{self.data_folder}\n")

        # Check if folder exists
        if not self.data_folder.exists():
            raise FileNotFoundError(
                f"Folder does not exist:\n{self.data_folder}"
            )

        # Find all parquet files
        parquet_files = sorted(self.data_folder.glob("*.parquet"))

        if not parquet_files:
            raise FileNotFoundError(
                f"No parquet files found in:\n{self.data_folder}"
            )

        print(f"Found {len(parquet_files)} parquet files.\n")

        dataframes = []

        for file in parquet_files:
            print(f"Reading: {file.name}")

            df = pd.read_parquet(file)

            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns)}\n")

            dataframes.append(df)

        merged_df = pd.concat(
            dataframes,
            ignore_index=True
        )

        print("=" * 60)
        print("Data Successfully Loaded")
        print("=" * 60)
        print(f"Total Rows    : {len(merged_df):,}")
        print(f"Total Columns : {len(merged_df.columns)}")
        print("=" * 60)

        return merged_df


def main():
    # Project Root
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Input Folder
    DATA_PATH = BASE_DIR / "data" / "Musical_Instruments"

    # Output Folder
    OUTPUT_PATH = BASE_DIR / "outputs"
    OUTPUT_PATH.mkdir(exist_ok=True)

    # Load Data
    loader = DataLoader(DATA_PATH)

    df = loader.load_data()

    # Save merged dataset
    output_file = OUTPUT_PATH / "merged_data.parquet"

    df.to_parquet(
        output_file,
        index=False
    )

    print(f"\nMerged dataset saved successfully!")
    print(f"Location: {output_file}")

    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 Rows:")
    print(df.head())


if __name__ == "__main__":
    main()