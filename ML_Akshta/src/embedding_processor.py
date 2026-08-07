from pathlib import Path
import json

import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer


# Embedding Processor
class EmbeddingProcessor:
    """
    Generates semantic embeddings
    with checkpoint support.
    """

    def __init__(
            self,
            input_file,
            output_dir,
            model_name="all-MiniLM-L6-v2",
            batch_size=256
    ):

        self.input_file = Path(input_file)

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.model_name = model_name

        self.batch_size = batch_size

        self.documents = None

        self.model = None

        self.embedding_output = (
            self.output_dir /
            "product_embeddings.npy"
        )

        self.flag_file = (
            self.output_dir /
            "embedding_completed.flag"
        )

        # Checkpoint Directory

        self.checkpoint_dir = (
            self.output_dir /
            "embeddings_checkpoint"
        )

        self.checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Progress File

        self.progress_file = (
            self.checkpoint_dir /
            "progress.json"
        )
    # Load Documents
    def load_documents(self):
        """
        Loads product documents
        for embedding generation.
        """

        print("=" * 60)
        print("LOADING PRODUCT DOCUMENTS")
        print("=" * 60)

        if not self.input_file.exists():

            raise FileNotFoundError(
                f"\nInput file not found:\n"
                f"{self.input_file}"
            )

        self.documents = pd.read_parquet(
            self.input_file
        )

        if "combined_text" not in self.documents.columns:

            raise ValueError(
                "'combined_text' column "
                "not found."
            )

        self.documents[
            "combined_text"
        ] = (
            self.documents[
                "combined_text"
            ]
            .fillna("")
            .astype(str)
        )

        print(
            "Documents Loaded Successfully"
        )

        print(
            f"Total Products : "
            f"{len(self.documents):,}"
        )

        print(
            f"Columns : "
            f"{self.documents.columns.tolist()}"
        )


    # Load Model
    def load_model(self):
        """
        Loads SentenceTransformer
        model.
        """

        print("=" * 60)
        print("LOADING EMBEDDING MODEL")
        print("=" * 60)

        self.model = SentenceTransformer(
            self.model_name
        )

        print(
            "Embedding Model Loaded Successfully"
        )

        print(
            f"Model Name : "
            f"{self.model_name}"
        )

        print(
            f"Embedding Dimension : "
            f"{self.model.get_sentence_embedding_dimension()}"
        )
    # Load Progress
    def load_progress(self):
        """
        Loads the last completed
        batch number from the
        progress file.
        """

        print("=" * 60)
        print("CHECKING CHECKPOINT")
        print("=" * 60)

        if self.progress_file.exists():

            try:

                with open(
                        self.progress_file,
                        "r"
                ) as file:

                    progress = json.load(file)

            except json.JSONDecodeError:

                print(
                    "Progress file corrupted."
                )

                print(
                    "Starting from Batch : 1"
                )

                return 0
            last_completed_batch = (
                progress.get(
                    "last_completed_batch",
                    0
                )
            )

            print(
                f"Resuming from Batch : "
                f"{last_completed_batch + 1}"
            )

            return last_completed_batch

        print(
            "No Checkpoint Found"
        )

        print(
            "Starting From Batch : 1"
        )

        return 0


    # Save Progress
    def save_progress(
            self,
            batch_number
    ):
        """
        Saves the last completed
        batch number.
        """

        progress = {

            "last_completed_batch":
                batch_number

        }

        with open(
                self.progress_file,
                "w"
        ) as file:

            json.dump(
                progress,
                file,
                indent=4
            )
    # Save Batch
    def save_batch(
            self,
            batch_number,
            batch_embeddings
    ):
        """
        Saves one embedding batch
        as a checkpoint file.
        """

        batch_file = (
            self.checkpoint_dir /
            f"batch_{batch_number:04d}.npy"
        )

        np.save(
            batch_file,
            batch_embeddings
        )

        print(
            f"Checkpoint Saved : "
            f"{batch_file.name}"
        )
    # Generate Embeddings
    def generate_embeddings(self):
        """
        Generates embeddings
        with checkpoint support.
        """

        print("=" * 60)
        print("GENERATING EMBEDDINGS")
        print("=" * 60)

        total_documents = len(
            self.documents
        )

        total_batches = (
            total_documents +
            self.batch_size - 1
        ) // self.batch_size

        last_completed_batch = (
            self.load_progress()
        )

        for batch_number in range(
                last_completed_batch + 1,
                total_batches + 1
        ):

            start = (
                (batch_number - 1)
                * self.batch_size
            )

            end = min(
                start + self.batch_size,
                total_documents
            )

            print()

            print(
                f"Generating Batch : "
                f"{batch_number}/{total_batches}"
            )

            batch_documents = (

                self.documents[
                    "combined_text"
                ]

                .iloc[start:end]

                .tolist()

            )

            batch_embeddings = (
                self.model.encode(

                    batch_documents,

                    batch_size=self.batch_size,

                    show_progress_bar=False,

                    convert_to_numpy=True,

                    normalize_embeddings=True

                )
                .astype(np.float32)
            )

            self.save_batch(

                batch_number,

                batch_embeddings

            )

            self.save_progress(
                batch_number
            )

            print(

                f"Processed : "
                f"{end:,}/{total_documents:,}"

            )

            del batch_documents
            del batch_embeddings

        print()

        print(
            "All Embedding Batches Generated Successfully"
        )
    # Merge Batches
    def merge_batches(self):
        """
        Merges all checkpoint
        embedding batches into
        a single NumPy array.
        """

        print("=" * 60)
        print("MERGING EMBEDDING BATCHES")
        print("=" * 60)

        batch_files = sorted(
            self.checkpoint_dir.glob(
                "batch_*.npy"
            )
        )

        if not batch_files:

            raise FileNotFoundError(
                "No embedding checkpoint files found."
            )

        embedding_batches = []

        for batch_file in batch_files:

            print(
                f"Loading : {batch_file.name}"
            )

            embedding_batches.append(
                np.load(batch_file)
            )

        embeddings = np.vstack(
            embedding_batches
        )

        del embedding_batches

        expected_documents = len(
            self.documents
        )

        if embeddings.shape[0] != expected_documents:

            raise ValueError(
                "Embedding count mismatch.\n"
                f"Expected : {expected_documents}\n"
                f"Found    : {embeddings.shape[0]}"
            )

        np.save(
            self.embedding_output,
            embeddings
        )

        print()

        print(
            "Merged Embeddings Saved Successfully"
        )

        print(
            f"Output File : {self.embedding_output}"
        )

        print(
            f"Embedding Shape : {embeddings.shape}"
        )

        del embeddings
    # Create Completion Flag
    def create_flag(self):
        """
        Creates a completion flag
        after successful embedding
        generation.
        """

        print("=" * 60)
        print("CREATING COMPLETION FLAG")
        print("=" * 60)

        self.flag_file.write_text(
            "Embedding generation completed successfully."
        )

        print(
            "Completion Flag Created Successfully"
        )

        print(
            f"Flag File : {self.flag_file}"
        )
    # Cleanup Checkpoints
    def cleanup_checkpoints(self):
        """
        Removes checkpoint files
        after successful merge.
        """

        print("=" * 60)
        print("CLEANING CHECKPOINTS")
        print("=" * 60)

        batch_files = sorted(
            self.checkpoint_dir.glob(
                "batch_*.npy"
            )
        )

        for batch_file in batch_files:
            batch_file.unlink()

        if self.progress_file.exists():
            self.progress_file.unlink()

        print(
            "Checkpoint Files Removed Successfully"
        )
    # Complete Pipeline
    def process(self):
        """
        Runs the complete
        embedding generation
        pipeline.
        """

        self.load_documents()

        self.load_model()

        self.generate_embeddings()

        self.merge_batches()

        self.create_flag()

        self.cleanup_checkpoints()

        # Free Memory
        del self.documents
        del self.model

        print()

        print("=" * 60)
        print("EMBEDDING GENERATION COMPLETED")
        print("=" * 60)

        print(
            f"Embeddings : {self.embedding_output}"
        )

        print(
            f"Flag File : {self.flag_file}"
        )

# Main
if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_FILE = (
        BASE_DIR /
        "outputs" /
        "product_documents.parquet"
    )

    OUTPUT_DIR = (
        BASE_DIR /
        "outputs"
    )

    processor = EmbeddingProcessor(

        input_file=INPUT_FILE,

        output_dir=OUTPUT_DIR,

        model_name="all-MiniLM-L6-v2",

        batch_size=256

    )

    processor.process()