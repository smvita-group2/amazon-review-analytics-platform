from pathlib import Path

import numpy as np
import pandas as pd

import pyarrow.dataset as ds

import torch

from tqdm import tqdm

from sentence_transformers import SentenceTransformer
# Embedding Processor
class EmbeddingProcessor:
    """
    Generates semantic embeddings
    for unique Amazon products.
    """

    def __init__(
            self,
            input_file,
            output_dir,
            batch_size=50000,
            embedding_batch_size=512
    ):
        self.input_file = Path(input_file)

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.batch_size = batch_size

        self.embedding_batch_size = embedding_batch_size

        self.dataset = None

        self.scanner = None

        self.products = None

        self.documents = None

        self.model = None

        self.embeddings = None

        self.device = None
        self.start_index = 0
    # Load Dataset
    def load_dataset(self):
        """
        Loads cleaned_data.parquet
        """

        print("=" * 60)
        print("LOADING DATASET")
        print("=" * 60)

        self.dataset = ds.dataset(
            self.input_file,
            format="parquet"
        )

        self.scanner = self.dataset.scanner(
            batch_size=self.batch_size
        )

        print("Dataset Loaded Successfully")

    # Prepare Products
    def prepare_products(self):
        """
        Extracts one unique record
        for every parent_asin.
        """

        print("=" * 60)
        print("PREPARING PRODUCTS")
        print("=" * 60)

        product_batches = []

        total_reviews = 0

        batch_number = 0

        for batch in self.scanner.to_batches():
            batch_number += 1

            print(f"Processing Batch : {batch_number}")

            batch_df = batch.to_pandas()
            total_reviews += len(batch_df)
            batch_df = batch_df[
                [
                    "parent_asin",
                    "product_title",
                    "store",
                    "main_category",
                    "sub_category",
                    "description_text",
                    "features_text"
                ]

            ]

            batch_df = batch_df.drop_duplicates(
                subset="parent_asin"
            )

            product_batches.append(batch_df)

            del batch_df
            del batch
        self.products = pd.concat(
            product_batches,
            ignore_index=True
        )

        self.products = self.products.drop_duplicates(
            subset="parent_asin"
        )
        # Free memory
        del product_batches

        print(f"Total Reviews Processed : {total_reviews:,}")

        print(f"Unique Products : {len(self.products):,}")

    # Create Documents



    def create_documents(self):
        """
        Creates one document
        for every unique product.
        """

        print("=" * 60)
        print("CREATING PRODUCT DOCUMENTS")
        print("=" * 60)

        self.products = self.products.fillna("")

        self.documents = []

        for row in tqdm(
                self.products.itertuples(index=False),
                total=len(self.products),
                desc="Creating Documents"
        ):
            document = (
                f"Title: {row.product_title}\n\n"
                f"Brand: {row.store}\n\n"
                f"Category: {row.main_category}\n\n"
                f"Sub Category: {row.sub_category}\n\n"
                f"Description:\n{row.description_text}\n\n"
                f"Features:\n{row.features_text}"
            )

            self.documents.append(document)

        print(
            f"Documents Created : {len(self.documents):,}"
        )
    # Load Embedding Model
    def load_model(self):
        """
        Loads SentenceTransformer model.
        """

        print("=" * 60)
        print("LOADING EMBEDDING MODEL")
        print("=" * 60)

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        MODEL_NAME = (
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.model = SentenceTransformer(
            MODEL_NAME,
            device=self.device
        )

        self.model.max_seq_length = 256

        print(f"Running on : {self.device}")

        print("Embedding Model Loaded Successfully")

    # Initialize Checkpoint Files
    def initialize_checkpoint_files(self):
        """
        Creates checkpoint file paths.
        """

        self.embedding_checkpoint = (
                self.output_dir /
                "embedding_checkpoint.npy"
        )

        self.last_embedding_file = (
                self.output_dir /
                "last_embedding.txt"
        )

        self.metadata_file = (
                self.output_dir /
                "product_metadata.parquet"
        )

        self.final_embedding_file = (
                self.output_dir /
                "product_embeddings.npy"
        )

        self.completed_flag = (
                self.output_dir /
                "embedding_completed.flag"
        )

    # Load Embedding Checkpoint
    def load_checkpoint(self):
        """
        Loads embedding checkpoint if available.
        """

        print("=" * 60)
        print("LOADING EMBEDDING CHECKPOINT")
        print("=" * 60)

        if (
                self.embedding_checkpoint.exists()
                and
                self.last_embedding_file.exists()
        ):

            self.embeddings = list(
                np.load(
                    self.embedding_checkpoint,
                    allow_pickle=True
                )
            )

            with open(
                    self.last_embedding_file,
                    "r"
            ) as file:

                self.start_index = int(
                    file.read()
                )

            print(
                f"Checkpoint Found"
            )

            print(
                f"Resume From : {self.start_index:,}"
            )

            print(
                f"Embeddings Loaded : {len(self.embeddings):,}"
            )

        else:

            self.embeddings = []

            self.start_index = 0

            print(
                "No Checkpoint Found"
            )

        # Save Embedding Checkpoint

    def save_checkpoint(
            self,
            current_index
    ):
        """
        Saves embedding checkpoint.
        """

        print("=" * 60)
        print("SAVING EMBEDDING CHECKPOINT")
        print("=" * 60)

        np.save(
            self.embedding_checkpoint,
            np.array(
                self.embeddings,
                dtype=np.float32
            )
        )

        with open(
                self.last_embedding_file,
                "w"
        ) as file:
            file.write(
                str(current_index)
            )

        print(
            f"Checkpoint Saved : {current_index:,}"
        )

    # Generate Embeddings
    def generate_embeddings(self):
        """
        Generates embeddings in batches
        with automatic checkpointing.
        """

        print("=" * 60)
        print("GENERATING EMBEDDINGS")
        print("=" * 60)

        total_documents = len(self.documents)

        checkpoint_interval = 10

        batch_counter = 0

        for start in tqdm(
                range(
                    self.start_index,
                    total_documents,
                    self.embedding_batch_size
                )
        ):

            end = min(
                start + self.embedding_batch_size,
                total_documents
            )

            batch_documents = self.documents[
                start:end
            ]

            batch_embeddings = self.model.encode(
                batch_documents,
                batch_size=self.embedding_batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )

            self.embeddings.extend(
                batch_embeddings.astype(np.float32)
            )

            batch_counter += 1

            # Save checkpoint every 10 batches
            if batch_counter % checkpoint_interval == 0:
                self.save_checkpoint(
                    current_index=end
                )

                print(
                    f"Checkpoint Saved "
                    f"at Document {end:,}"
                )

            del batch_documents
            del batch_embeddings

            if self.device == "cuda":
                torch.cuda.empty_cache()
        self.save_checkpoint(
            current_index=total_documents
        )

        print(
            f"Embeddings Generated : {len(self.embeddings):,}"
        )

    # Save Final Embeddings
    def save_embeddings(self):
        """
        Saves final embeddings
        and metadata.
        """

        print("=" * 60)
        print("SAVING FINAL EMBEDDINGS")
        print("=" * 60)

        embeddings_array = np.array(
            self.embeddings,
            dtype=np.float32
        )

        np.save(
            self.final_embedding_file,
            embeddings_array
        )

        self.products.to_parquet(
            self.metadata_file,
            index=False
        )

        with open(
                self.completed_flag,
                "w"
        ) as file:
            file.write("Completed")

        print(
            f"Embeddings Saved : {len(embeddings_array):,}"
        )

        print(
            f"Metadata Saved : {len(self.products):,}"
        )
        # Remove temporary checkpoint files
        if self.embedding_checkpoint.exists():
            self.embedding_checkpoint.unlink()

        if self.last_embedding_file.exists():
            self.last_embedding_file.unlink()
        print(
            "Embedding Pipeline Completed Successfully"
        )

    # Complete Pipeline
    def process(self):
        """
        Runs complete embedding pipeline.
        """

        self.load_dataset()

        self.prepare_products()

        self.create_documents()

        self.load_model()

        self.initialize_checkpoint_files()

        self.load_checkpoint()

        self.generate_embeddings()

        self.save_embeddings()