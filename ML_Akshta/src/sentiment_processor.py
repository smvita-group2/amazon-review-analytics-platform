from pathlib import Path
import os

import pandas as pd
import pyarrow.dataset as ds

import torch

from tqdm import tqdm

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)
#Class
class SentimentProcessor:
    """
    Generates product-level sentiment statistics
    using review-level sentiment analysis.
    """

    def __init__(
        self,
        input_file,
        output_dir,
        batch_size=20000,
        mini_batch_size=64
    ):

        self.input_file = Path(input_file)

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.batch_size = batch_size

        self.mini_batch_size = mini_batch_size

        self.dataset = None

        self.scanner = None

        self.tokenizer = None

        self.model = None

        self.device = None

        self.product_statistics = {}

        self.start_batch = 1

        self.start_review = 0
        self.checkpoint_interval = 10

        self.initialize_checkpoint_files()
    #Load Dataset
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
    #Load model
    def load_model(self):
        """
        Loads tokenizer and sentiment model.
        """

        print("=" * 60)
        print("LOADING MODEL")
        print("=" * 60)

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        MODEL_NAME = (
            "cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(MODEL_NAME)
        )

        self.model.to(self.device)

        self.model.eval()

        print(f"Running on : {self.device}")
    #Checkpoint path
    def initialize_checkpoint_files(self):
        """
        Creates checkpoint file paths.
        """

        self.checkpoint_file = (
                self.output_dir /
                "product_sentiment_checkpoint.parquet"
        )

        self.last_batch_file = (
                self.output_dir /
                "last_batch.txt"
        )

        self.last_review_file = (
                self.output_dir /
                "last_review.txt"
        )
    #Load Checkpoint

    def load_checkpoint(self):
        """
        Loads checkpoint if available.
        """

        print("=" * 60)
        print("LOADING CHECKPOINT")
        print("=" * 60)

        if (
                self.checkpoint_file.exists()
                and
                self.last_batch_file.exists()
                and
                self.last_review_file.exists()
        ):

            checkpoint_df = pd.read_parquet(
                self.checkpoint_file
            )

            self.product_statistics = {}

            for _, row in checkpoint_df.iterrows():
                self.product_statistics[
                    row["parent_asin"]
                ] = {

                    "positive": int(row["positive"]),
                    "neutral": int(row["neutral"]),
                    "negative": int(row["negative"])
                }

            with open(
                    self.last_batch_file,
                    "r"
            ) as file:

                self.start_batch = int(
                    file.read()
                )

            with open(
                    self.last_review_file,
                    "r"
            ) as file:

                self.start_review = int(
                    file.read()
                )

            print("Checkpoint Loaded Successfully")

            print(f"Resume Batch  : {self.start_batch}")

            print(f"Resume Review : {self.start_review}")

            print(
                f"Products Loaded : {len(self.product_statistics):,}"
            )

        else:

            print("No Checkpoint Found")

            self.product_statistics = {}

            self.start_batch = 1

            self.start_review = 0

    # Save Checkpoint
    def save_checkpoint(
            self,
            current_batch,
            current_review
    ):
        """
        Saves processing checkpoint.
        """

        print("=" * 60)
        print("SAVING CHECKPOINT")
        print("=" * 60)

        checkpoint_df = (
            pd.DataFrame
            .from_dict(
                self.product_statistics,
                orient="index"
            )
            .reset_index()
        )

        checkpoint_df.rename(
            columns={
                "index": "parent_asin"
            },
            inplace=True
        )

        checkpoint_df.to_parquet(
            self.checkpoint_file,
            index=False
        )

        with open(
                self.last_batch_file,
                "w"
        ) as file:
            file.write(
                str(current_batch)
            )

        with open(
                self.last_review_file,
                "w"
        ) as file:
            file.write(
                str(current_review)
            )

        print("Checkpoint Saved Successfully")

        print(f"Batch  : {current_batch}")

        print(f"Review : {current_review}")

    # Predict Sentiment
    def predict_sentiment(
            self,
            review_list
    ):
        """
        Predict sentiment for a mini-batch of reviews.
        """

        inputs = self.tokenizer(
            review_list,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(**inputs)

            predictions = torch.argmax(
                outputs.logits,
                dim=1
            )

        label_mapping = {

            0: "negative",

            1: "neutral",

            2: "positive"
        }

        labels = [

            label_mapping[prediction.item()]

            for prediction in predictions
        ]

        return labels

    # Update Product Statistics
    def update_product_statistics(
            self,
            batch_df,
            labels
    ):
        """
        Updates product-level sentiment statistics.
        """

        for parent_asin, sentiment in zip(
                batch_df["parent_asin"],
                labels
        ):

            # Create entry for new product
            if parent_asin not in self.product_statistics:
                self.product_statistics[parent_asin] = {

                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }

            # Update sentiment count
            self.product_statistics[parent_asin][sentiment] += 1

    # Process Batches
   
    def process_batches(self):
        """
        Processes all reviews batch by batch.
        """

        print("=" * 60)
        print("STARTING SENTIMENT PROCESSING")
        print("=" * 60)

        batch_number = 0

        for batch in self.scanner.to_batches():

            batch_number += 1

            # Skip batches already processed
            if batch_number < self.start_batch:
                continue

            print("\n" + "=" * 60)
            print(f"Processing Batch : {batch_number}")
            print("=" * 60)

            # Convert Arrow batch to Pandas
            batch_df = batch.to_pandas()

            # Keep required columns
            batch_df = batch_df[
                [
                    "parent_asin",
                    "review_text"
                ]
            ]

            # Handle missing reviews
            batch_df["review_text"] = (
                batch_df["review_text"]
                .fillna("")
                .astype(str)
            )

            # Resume from saved review if restarting same batch
            start_review = 0

            if batch_number == self.start_batch:
                start_review = min(
                    self.start_review + self.mini_batch_size,
                    len(batch_df)
                )

            mini_batch_counter = 0

            # ---------------------------------------------------
            # Process reviews in mini-batches
            # ---------------------------------------------------

            for review_start in range(
                    start_review,
                    len(batch_df),
                    self.mini_batch_size
            ):

                review_end = min(
                    review_start + self.mini_batch_size,
                    len(batch_df)
                )

                mini_batch_df = batch_df.iloc[
                    review_start:review_end
                ]

                review_list = (
                    mini_batch_df["review_text"]
                    .tolist()
                )

                # Predict Sentiment
                labels = self.predict_sentiment(
                    review_list
                )

                # Update Statistics
                self.update_product_statistics(
                    mini_batch_df,
                    labels
                )

                mini_batch_counter += 1
                if (
                    mini_batch_counter
                    % self.checkpoint_interval
                    == 0
                ):
                    self.save_checkpoint(
                        current_batch=batch_number,
                        current_review=review_end
                    )

                    print(
                        f"Checkpoint Saved "
                        f"(Batch {batch_number}, "
                        f"Review {review_end})"
                    )

            # ---------------------------------------------------
            # Save final checkpoint for this batch
            # ---------------------------------------------------

            self.save_checkpoint(
                current_batch=batch_number,
                current_review=review_end
            )

            print(
                f"Batch {batch_number} Completed"
            )

            # Free Memory
            del batch_df

            if "mini_batch_df" in locals():
                del mini_batch_df

            if "review_list" in locals():
                del review_list

            if "labels" in locals():
                del labels

            

            torch.cuda.empty_cache()

        print("\nAll batches processed successfully.")
    # Create Final Dataset
    def create_final_dataset(self):
        """
        Creates final product sentiment dataset.
        """

        print("=" * 60)
        print("CREATING FINAL DATASET")
        print("=" * 60)

        sentiment_df = (
            pd.DataFrame
            .from_dict(
                self.product_statistics,
                orient="index"
            )
            .reset_index()
        )

        sentiment_df.rename(
            columns={
                "index": "parent_asin"
            },
            inplace=True
        )

        # Total Reviews
        sentiment_df["total_reviews"] = (

                sentiment_df["positive"]

                + sentiment_df["neutral"]

                + sentiment_df["negative"]
        )

        # Sentiment Score
        sentiment_df["sentiment_score"] = (

                         sentiment_df["positive"] - sentiment_df["negative"]) / sentiment_df["total_reviews"]

        output_file = (

                self.output_dir /

                "product_sentiment.parquet"
        )

        sentiment_df.to_parquet(
            output_file,
            index=False
        )

        print(f"Final Dataset Saved : {output_file}")

        print(f"Products : {len(sentiment_df):,}")

    # Main Process
    def process(self):
        """
        Executes the complete sentiment processing pipeline.
        """

        print("=" * 60)
        print("PRODUCT SENTIMENT PIPELINE")
        print("=" * 60)

        # Initialize checkpoint paths
        #self.initialize_checkpoint_files()

        # Load dataset
        self.load_dataset()

        # Load model
        self.load_model()

        # Load checkpoint if available
        self.load_checkpoint()

        # Process all batches
        self.process_batches()

        # Create final dataset
        self.create_final_dataset()

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)