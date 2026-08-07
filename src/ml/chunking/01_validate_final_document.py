#!/usr/bin/env python3
"""Validation stage for the Hybrid RAG Intelligent Product Search pipeline.

This module determines whether ``final_documents`` is production-ready for
the downstream text-chunking stage. It enforces schema correctness, fails
fast on a missing/empty input dataset, and reports duplicate ``parent_asin``
records, null-field violations, empty/whitespace-only documents, character
count statistics, category distribution, and short/long document outliers.
All offending row sets and a machine-readable validation summary are
persisted to S3.

Runtime: Amazon EMR / PySpark 3.5.x / Python 3.11
Entry point: spark-submit 01_validate_final_documents.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import boto3
from pyspark import StorageLevel
from pyspark.sql import DataFrame, Row, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DataType, StringType, StructField, StructType

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PipelineError(Exception):
    """Base exception for all fatal pipeline failures."""


class SchemaValidationError(PipelineError):
    """Raised when the input DataFrame schema does not match the contract."""


class InvalidInputPathError(PipelineError):
    """Raised when the configured input path is missing, unreadable, or empty."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable configuration for the final-documents validation stage.

    Centralizing configuration avoids hardcoded literals scattered through
    the pipeline logic and makes the stage testable against alternate paths
    without touching business logic.
    """

    pipeline_name: str = "hybrid-rag-validate-final-documents"
    app_name: str = "hybrid-rag-validate-final-documents"

    # Input/output contracts are fixed per the upstream pipeline agreement.
    input_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/preprocessing/final_documents/"
    )
    output_base_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/preprocessing/validation/final_documents/"
    )

    duplicate_output_path: str = field(init=False)
    null_records_output_path: str = field(init=False)
    empty_documents_output_path: str = field(init=False)
    category_distribution_output_path: str = field(init=False)
    document_statistics_output_path: str = field(init=False)
    length_histogram_output_path: str = field(init=False)
    very_short_documents_output_path: str = field(init=False)
    extremely_long_documents_output_path: str = field(init=False)
    summary_output_path: str = field(init=False)

    required_string_columns: Tuple[str, ...] = (
        "parent_asin",
        "category",
        "product_title",
        "document",
    )

    # Outlier thresholds, expressed as configuration rather than magic
    # numbers embedded in filter predicates.
    short_document_char_threshold: int = 100
    long_document_char_threshold: int = 5000

    # Document-length histogram buckets, consumed by the downstream
    # chunking stage to pick a chunk size/overlap. Each entry is
    # (label, lower_bound_inclusive, upper_bound_inclusive); the final
    # bucket's upper bound is None to represent an open-ended "5000+" tail.
    # Order matters: it defines both bucket precedence and the sort order
    # persisted in the output, since bucket labels are strings and would
    # not sort correctly on their own (e.g. "1001-2000" < "301-500").
    histogram_buckets: Tuple[Tuple[str, int, Optional[int]], ...] = (
        ("0-100", 0, 100),
        ("101-300", 101, 300),
        ("301-500", 301, 500),
        ("501-1000", 501, 1000),
        ("1001-2000", 1001, 2000),
        ("2001-5000", 2001, 5000),
        ("5000+", 5001, None),
    )

    # Quantiles requested for the character-count distribution, plus the
    # approxQuantile relative error tolerance (0.0 = exact, costlier).
    quantile_targets: Tuple[float, ...] = (0.5, 0.95, 0.99)
    quantile_relative_error: float = 0.01

    input_file_format: str = "parquet"
    write_mode: str = "overwrite"
    shuffle_partitions: int = 200

    def __post_init__(self) -> None:
        # dataclass is frozen, so derived paths are assigned via object.__setattr__.
        base = self.output_base_path.rstrip("/")
        object.__setattr__(self, "duplicate_output_path", f"{base}/duplicate_parent_asin/")
        object.__setattr__(self, "null_records_output_path", f"{base}/null_records/")
        object.__setattr__(self, "empty_documents_output_path", f"{base}/empty_documents/")
        object.__setattr__(
            self, "category_distribution_output_path", f"{base}/category_distribution/"
        )
        object.__setattr__(
            self, "document_statistics_output_path", f"{base}/document_statistics/"
        )
        object.__setattr__(
            self, "length_histogram_output_path", f"{base}/document_length_histogram/"
        )
        object.__setattr__(
            self, "very_short_documents_output_path", f"{base}/very_short_documents/"
        )
        object.__setattr__(
            self, "extremely_long_documents_output_path", f"{base}/extremely_long_documents/"
        )
        object.__setattr__(self, "summary_output_path", f"{base}/validation_summary.json")

    @property
    def expected_schema(self) -> StructType:
        """Contractual schema for the ``final_documents`` dataset."""
        return StructType(
            [
                StructField("parent_asin", StringType(), True),
                StructField("category", StringType(), True),
                StructField("product_title", StringType(), True),
                StructField("document", StringType(), True),
            ]
        )


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def build_logger(app_name: str) -> logging.Logger:
    """Configure and return a structured stdout logger.

    EMR captures stdout into step/driver logs, so a single stream handler
    with a consistent, parseable format is sufficient for downstream log
    aggregation (e.g. CloudWatch Logs subscription filters).
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


class StageTimer:
    """Context manager that logs START/END/ELAPSED for a pipeline stage.

    Consolidating this pattern avoids duplicated timing/logging boilerplate
    at the top of every validation function.
    """

    def __init__(self, logger: logging.Logger, stage_name: str) -> None:
        self._logger = logger
        self._stage_name = stage_name
        self._start_time: float = 0.0

    def __enter__(self) -> "StageTimer":
        self._start_time = time.time()
        self._logger.info("STAGE START | %s", self._stage_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed = time.time() - self._start_time
        if exc_type is None:
            self._logger.info(
                "STAGE END | %s | elapsed_seconds=%.2f", self._stage_name, elapsed
            )
        else:
            self._logger.error(
                "STAGE FAILED | %s | elapsed_seconds=%.2f | error=%s",
                self._stage_name,
                elapsed,
                exc_val,
            )
        return False


# ---------------------------------------------------------------------------
# Spark session
# ---------------------------------------------------------------------------


def build_spark_session(config: PipelineConfig) -> SparkSession:
    """Construct a SparkSession tuned for an EMR validation workload.

    Settings favor stable shuffle behavior and efficient serialization over
    aggressive tuning, since this stage is I/O- and scan-bound rather than
    compute-bound.
    """
    return (
        SparkSession.builder.appName(config.app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.adaptive.skewJoin.enabled", "true")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.shuffle.partitions", str(config.shuffle_partitions))
        .config("spark.python.worker.reuse", "true")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .getOrCreate()
    )


# ---------------------------------------------------------------------------
# Input resolution and fail-fast checks
# ---------------------------------------------------------------------------


def validate_input_path_exists(spark: SparkSession, config: PipelineConfig, logger: logging.Logger) -> None:
    """Verify the S3 input path exists before any read is attempted.

    This check runs entirely on the driver via the Hadoop FileSystem API,
    so a missing prefix fails in milliseconds with an unambiguous message
    instead of surfacing later as an opaque error from the distributed
    read path (which can otherwise take much longer to fail and can
    conflate "path missing" with "path unreadable" or "schema mismatch").
    """
    hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(config.input_path)  # noqa: SLF001
    file_system = hadoop_path.getFileSystem(spark._jsc.hadoopConfiguration())  # noqa: SLF001

    if not file_system.exists(hadoop_path):
        raise InvalidInputPathError(
            f"Input path does not exist: '{config.input_path}'. "
            "Verify the upstream final_documents stage completed successfully."
        )
    logger.info("Input path existence check passed | path=%s", config.input_path)


def _resolve_input_dataframe(spark: SparkSession, config: PipelineConfig) -> DataFrame:
    """Read the input dataset, failing fast on an unreadable/missing path.

    Reading eagerly here (rather than deferring failure to a later action)
    ensures path-level errors surface with a clear, actionable exception
    instead of a cryptic downstream Spark stack trace.
    """
    try:
        return spark.read.format(config.input_file_format).load(config.input_path)
    except Exception as exc:  # noqa: BLE001 - re-raised as a typed pipeline error
        raise InvalidInputPathError(
            f"Unable to read input data at '{config.input_path}': {exc}"
        ) from exc


def validate_non_empty_input(df: DataFrame, config: PipelineConfig, logger: logging.Logger) -> None:
    """Fail fast if the input dataset contains zero rows.

    ``df.head(1)`` triggers only a single-partition scan rather than a full
    dataset count, making the emptiness check cheap even on large inputs.
    """
    if not df.head(1):
        raise InvalidInputPathError(
            f"Input dataset at '{config.input_path}' exists but contains no rows."
        )
    logger.info("Input dataset presence check passed | path=%s", config.input_path)


def validate_schema(df: DataFrame, config: PipelineConfig, logger: logging.Logger) -> None:
    """Validate the DataFrame schema against the expected contract.

    Checks for missing columns, unexpected extra columns, and datatype
    mismatches on the expected columns. Raises on any violation since a
    schema mismatch invalidates every downstream check in this module.
    """
    actual_fields: Dict[str, DataType] = {f.name: f.dataType for f in df.schema.fields}
    expected_fields: Dict[str, DataType] = {
        f.name: f.dataType for f in config.expected_schema.fields
    }

    missing_columns = sorted(set(expected_fields) - set(actual_fields))
    unexpected_columns = sorted(set(actual_fields) - set(expected_fields))
    type_mismatches: List[str] = [
        f"{name}: expected={expected_fields[name].simpleString()}, "
        f"actual={actual_fields[name].simpleString()}"
        for name in expected_fields
        if name in actual_fields and actual_fields[name] != expected_fields[name]
    ]

    if unexpected_columns:
        logger.warning("Unexpected columns present in input schema: %s", unexpected_columns)

    if missing_columns or type_mismatches:
        raise SchemaValidationError(
            f"Schema validation failed. missing_columns={missing_columns}, "
            f"type_mismatches={type_mismatches}"
        )

    logger.info("Schema validation passed. columns=%s", list(actual_fields.keys()))


# ---------------------------------------------------------------------------
# Core validation pass (single aggregation for row count, nulls, char stats,
# empty-document count, and short/long document counts)
# ---------------------------------------------------------------------------


def compute_core_metrics(
    df: DataFrame, config: PipelineConfig, logger: logging.Logger
) -> Tuple[Row, int]:
    """Compute row count, null counts, empty-doc count, char-count
    min/max/avg/stddev, and document-length histogram bucket counts in a
    single Spark action.

    Consolidating these conditional aggregations into one ``agg`` call
    avoids ten-plus separate full-dataset scans, which is the single
    highest-impact optimization available on a wide, cache-resident
    DataFrame like this one. Histogram bucketing in particular could be
    implemented as a ``groupBy`` on a derived bucket column, but that
    forces a shuffle; expressing each bucket as a conditional count in
    this existing aggregation keeps the whole pass shuffle-free.

    Returns:
        A tuple of (aggregation result row, total row count).
    """
    empty_condition = F.col("document").isNotNull() & (F.trim(F.col("document")) == "")
    short_condition = F.col("char_count") < config.short_document_char_threshold
    long_condition = F.col("char_count") > config.long_document_char_threshold

    agg_exprs = [F.count(F.lit(1)).alias("total_rows")]
    for column_name in config.required_string_columns:
        agg_exprs.append(
            F.count(F.when(F.col(column_name).isNull(), 1)).alias(f"{column_name}__null_count")
        )
    agg_exprs.extend(
        [
            F.count(F.when(empty_condition, 1)).alias("empty_document_count"),
            F.count(F.when(short_condition, 1)).alias("very_short_document_count"),
            F.count(F.when(long_condition, 1)).alias("extremely_long_document_count"),
            F.min("char_count").alias("char_count_min"),
            F.max("char_count").alias("char_count_max"),
            F.avg("char_count").alias("char_count_avg"),
            F.stddev("char_count").alias("char_count_stddev"),
        ]
    )
    for bucket_label, lower_bound, upper_bound in config.histogram_buckets:
        bucket_condition = F.col("char_count") >= lower_bound
        if upper_bound is not None:
            bucket_condition = bucket_condition & (F.col("char_count") <= upper_bound)
        agg_exprs.append(
            F.count(F.when(bucket_condition, 1)).alias(f"histogram__{bucket_label}")
        )

    result_row = df.agg(*agg_exprs).first()
    total_rows = int(result_row["total_rows"])
    logger.info("Core metrics computed in a single aggregation pass | total_rows=%d", total_rows)
    return result_row, total_rows


def compute_char_count_quantiles(
    df: DataFrame, config: PipelineConfig, logger: logging.Logger
) -> Dict[str, float]:
    """Compute median/p95/p99 character-count quantiles via approxQuantile.

    ``approxQuantile`` uses a sketch-based algorithm and is a single job
    regardless of the number of quantiles requested, making it far cheaper
    than sorting the full column for exact percentiles.
    """
    quantile_values = df.approxQuantile(
        "char_count", list(config.quantile_targets), config.quantile_relative_error
    )
    quantile_map = {
        "p50_median": quantile_values[0],
        "p95": quantile_values[1],
        "p99": quantile_values[2],
    }
    logger.info("Character count quantiles computed | %s", quantile_map)
    return quantile_map


# ---------------------------------------------------------------------------
# Row-level validation outputs
# ---------------------------------------------------------------------------


def persist_duplicate_parent_asin(
    df: DataFrame, config: PipelineConfig, logger: logging.Logger
) -> int:
    """Detect and persist rows sharing a duplicated ``parent_asin``.

    Uses a groupBy/join rather than a window function so the operation
    scales with partition count instead of requiring a full-dataset window
    shuffle.
    """
    duplicate_keys = (
        df.groupBy("parent_asin")
        .agg(F.count(F.lit(1)).alias("occurrence_count"))
        .filter(F.col("occurrence_count") > 1)
    )

    duplicate_rows = df.join(duplicate_keys, on="parent_asin", how="inner")
    duplicate_count = duplicate_keys.agg(
        F.coalesce(F.sum("occurrence_count"), F.lit(0)).alias("total")
    ).first()["total"]
    duplicate_count = int(duplicate_count)

    if duplicate_count > 0:
        (
            duplicate_rows.drop("char_count")
            .write.mode(config.write_mode)
            .format(config.input_file_format)
            .save(config.duplicate_output_path)
        )
        logger.warning(
            "Duplicate parent_asin rows persisted | count=%d | path=%s",
            duplicate_count,
            config.duplicate_output_path,
        )
    else:
        logger.info("No duplicate parent_asin records found.")

    return duplicate_count


def persist_null_records(
    df: DataFrame, config: PipelineConfig, null_counts: Dict[str, int], logger: logging.Logger
) -> None:
    """Persist rows violating the not-null contract on required columns."""
    if not any(count > 0 for count in null_counts.values()):
        logger.info("No null violations found in required columns.")
        return

    null_condition = F.lit(False)
    for column_name in config.required_string_columns:
        null_condition = null_condition | F.col(column_name).isNull()

    (
        df.filter(null_condition)
        .drop("char_count")
        .write.mode(config.write_mode)
        .format(config.input_file_format)
        .save(config.null_records_output_path)
    )
    logger.warning("Null-violating rows persisted | path=%s", config.null_records_output_path)


def persist_empty_documents(
    df: DataFrame, config: PipelineConfig, empty_count: int, logger: logging.Logger
) -> None:
    """Persist rows with an empty-string or whitespace-only document field."""
    if empty_count == 0:
        logger.info("No empty or whitespace-only document fields found.")
        return

    empty_condition = F.col("document").isNotNull() & (F.trim(F.col("document")) == "")
    (
        df.filter(empty_condition)
        .drop("char_count")
        .write.mode(config.write_mode)
        .format(config.input_file_format)
        .save(config.empty_documents_output_path)
    )
    logger.warning("Empty document rows persisted | path=%s", config.empty_documents_output_path)


def persist_short_and_long_documents(
    df: DataFrame,
    config: PipelineConfig,
    short_count: int,
    long_count: int,
    logger: logging.Logger,
) -> None:
    """Persist very short and extremely long documents to separate paths."""
    if short_count > 0:
        (
            df.filter(F.col("char_count") < config.short_document_char_threshold)
            .write.mode(config.write_mode)
            .format(config.input_file_format)
            .save(config.very_short_documents_output_path)
        )
        logger.warning(
            "Very short documents persisted | threshold=%d | count=%d | path=%s",
            config.short_document_char_threshold,
            short_count,
            config.very_short_documents_output_path,
        )
    else:
        logger.info("No very short documents found below threshold=%d.", config.short_document_char_threshold)

    if long_count > 0:
        (
            df.filter(F.col("char_count") > config.long_document_char_threshold)
            .write.mode(config.write_mode)
            .format(config.input_file_format)
            .save(config.extremely_long_documents_output_path)
        )
        logger.warning(
            "Extremely long documents persisted | threshold=%d | count=%d | path=%s",
            config.long_document_char_threshold,
            long_count,
            config.extremely_long_documents_output_path,
        )
    else:
        logger.info("No extremely long documents found above threshold=%d.", config.long_document_char_threshold)


def persist_category_distribution(df: DataFrame, config: PipelineConfig, logger: logging.Logger) -> None:
    """Compute and persist document count per category."""
    (
        df.groupBy("category")
        .agg(F.count(F.lit(1)).alias("document_count"))
        .orderBy(F.col("document_count").desc())
        .write.mode(config.write_mode)
        .format(config.input_file_format)
        .save(config.category_distribution_output_path)
    )
    logger.info("Category distribution persisted | path=%s", config.category_distribution_output_path)


def persist_length_histogram(
    core_row: Row, config: PipelineConfig, spark: SparkSession, logger: logging.Logger
) -> Dict[str, int]:
    """Persist the document-length histogram computed by ``compute_core_metrics``.

    The downstream chunking stage (02_generate_chunks.py) uses this
    distribution to pick a chunk size and overlap, so bucket order is
    preserved explicitly via a ``bucket_order`` column rather than relying
    on an alphabetical sort of the bucket label, which would misorder
    entries like "1001-2000" ahead of "301-500".

    Returns:
        An ordered mapping of bucket label to document count, for
        inclusion in the run-level log output.
    """
    histogram_counts: Dict[str, int] = {
        bucket_label: int(core_row[f"histogram__{bucket_label}"])
        for bucket_label, _, _ in config.histogram_buckets
    }

    histogram_rows = [
        Row(bucket=bucket_label, document_count=count, bucket_order=order)
        for order, (bucket_label, count) in enumerate(histogram_counts.items())
    ]
    histogram_df = spark.createDataFrame(histogram_rows).orderBy("bucket_order").drop("bucket_order")

    (
        histogram_df.coalesce(1)
        .write.mode(config.write_mode)
        .format(config.input_file_format)
        .save(config.length_histogram_output_path)
    )

    for bucket_label, count in histogram_counts.items():
        logger.info("Document length histogram | bucket=%s | count=%d", bucket_label, count)
    logger.info("Document length histogram persisted | path=%s", config.length_histogram_output_path)

    return histogram_counts


def persist_document_statistics(
    stats: Dict[str, float], config: PipelineConfig, spark: SparkSession, logger: logging.Logger
) -> None:
    """Persist character-count distribution statistics as a single-row dataset."""
    stats_df = spark.createDataFrame([Row(**stats)])
    (
        stats_df.coalesce(1)
        .write.mode(config.write_mode)
        .format(config.input_file_format)
        .save(config.document_statistics_output_path)
    )
    logger.info("Document statistics persisted | path=%s", config.document_statistics_output_path)


# ---------------------------------------------------------------------------
# Summary persistence
# ---------------------------------------------------------------------------


def _parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """Split an ``s3://bucket/key`` URI into its bucket and key components."""
    without_scheme = s3_uri.replace("s3://", "", 1)
    bucket, _, key = without_scheme.partition("/")
    return bucket, key


def determine_validation_status(
    total_rows: int,
    duplicate_count: int,
    null_counts: Dict[str, int],
    empty_document_count: int,
) -> str:
    """Derive an overall PASS / WARNING / FAIL status for the dataset.

    FAIL is reserved for conditions that block downstream chunking entirely
    (no data). WARNING flags data-quality issues that are survivable but
    should be triaged before proceeding. Anything else is PASS.
    """
    if total_rows == 0:
        return "FAIL"

    has_quality_issues = (
        duplicate_count > 0
        or empty_document_count > 0
        or any(count > 0 for count in null_counts.values())
    )
    return "WARNING" if has_quality_issues else "PASS"


def write_validation_summary(summary: dict, config: PipelineConfig, logger: logging.Logger) -> None:
    """Persist the validation summary as a single JSON object on S3.

    A direct boto3 put_object is used instead of a Spark DataFrame write
    because the summary is a single small document, not a distributed
    dataset, and this avoids the part-file/_SUCCESS artifacts a Spark
    write would otherwise produce.
    """
    bucket, key = _parse_s3_uri(config.summary_output_path)
    s3_client = boto3.client("s3")

    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(summary, indent=2, default=str).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as exc:  # noqa: BLE001 - surfaced with S3 context
        raise PipelineError(
            f"Failed to write validation summary to s3://{bucket}/{key}: {exc}"
        ) from exc

    logger.info("Validation summary written | path=%s", config.summary_output_path)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_validation(spark: SparkSession, config: PipelineConfig, logger: logging.Logger) -> dict:
    """Execute the full validation stage and return the summary payload."""
    with StageTimer(logger, "input_path_existence_check"):
        validate_input_path_exists(spark, config, logger)

    df = _resolve_input_dataframe(spark, config)

    with StageTimer(logger, "input_presence_check"):
        validate_non_empty_input(df, config, logger)

    with StageTimer(logger, "schema_validation"):
        validate_schema(df, config, logger)

    # MEMORY_AND_DISK is used instead of the default MEMORY_ONLY cache()
    # because final_documents can exceed executor memory at production
    # scale; spilling to disk avoids recomputation without risking OOM
    # evictions that would silently force a full re-read from S3.
    df = (
        df.select(*config.required_string_columns)
        .withColumn("char_count", F.length(F.col("document")))
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    try:
        with StageTimer(logger, "core_metrics"):
            core_row, total_rows = compute_core_metrics(df, config, logger)

        null_counts = {
            column_name: int(core_row[f"{column_name}__null_count"])
            for column_name in config.required_string_columns
        }
        null_percentages = {
            column_name: round((count / total_rows * 100.0) if total_rows > 0 else 0.0, 4)
            for column_name, count in null_counts.items()
        }
        empty_document_count = int(core_row["empty_document_count"])
        very_short_count = int(core_row["very_short_document_count"])
        extremely_long_count = int(core_row["extremely_long_document_count"])

        for column_name, count in null_counts.items():
            logger.info(
                "Null check | column=%s | null_count=%d | null_percentage=%.4f%%",
                column_name,
                count,
                null_percentages[column_name],
            )
        logger.info(
            "Empty document check | count=%d | percentage=%.4f%%",
            empty_document_count,
            round((empty_document_count / total_rows * 100.0) if total_rows > 0 else 0.0, 4),
        )

        with StageTimer(logger, "char_count_quantiles"):
            quantiles = compute_char_count_quantiles(df, config, logger)

        document_statistics = {
            "char_count_min": int(core_row["char_count_min"] or 0),
            "char_count_max": int(core_row["char_count_max"] or 0),
            "char_count_avg": round(float(core_row["char_count_avg"] or 0.0), 4),
            "char_count_stddev": round(float(core_row["char_count_stddev"] or 0.0), 4),
            "char_count_median": quantiles["p50_median"],
            "char_count_p95": quantiles["p95"],
            "char_count_p99": quantiles["p99"],
        }

        with StageTimer(logger, "length_histogram_persistence"):
            length_histogram = persist_length_histogram(core_row, config, spark, logger)

        with StageTimer(logger, "duplicate_validation"):
            duplicate_count = persist_duplicate_parent_asin(df, config, logger)

        with StageTimer(logger, "null_record_persistence"):
            persist_null_records(df, config, null_counts, logger)

        with StageTimer(logger, "empty_document_persistence"):
            persist_empty_documents(df, config, empty_document_count, logger)

        with StageTimer(logger, "short_and_long_document_persistence"):
            persist_short_and_long_documents(
                df, config, very_short_count, extremely_long_count, logger
            )

        with StageTimer(logger, "category_distribution"):
            persist_category_distribution(df, config, logger)

        with StageTimer(logger, "document_statistics_persistence"):
            persist_document_statistics(document_statistics, config, spark, logger)
    finally:
        df.unpersist()

    validation_status = determine_validation_status(
        total_rows, duplicate_count, null_counts, empty_document_count
    )

    return {
        "pipeline_name": config.pipeline_name,
        "input_path": config.input_path,
        "output_path": config.output_base_path,
        "total_rows": total_rows,
        "duplicate_parent_asin_count": duplicate_count,
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "empty_document_count": empty_document_count,
        "very_short_document_count": very_short_count,
        "extremely_long_document_count": extremely_long_count,
        "document_statistics": document_statistics,
        "document_length_histogram": length_histogram,
        "validation_status": validation_status,
    }


def main() -> None:
    """Entry point invoked via spark-submit."""
    config = PipelineConfig()
    logger = build_logger(config.app_name)
    spark = build_spark_session(config)

    pipeline_start_time = time.time()
    execution_timestamp = datetime.now(timezone.utc).isoformat()
    application_id = spark.sparkContext.applicationId

    logger.info(
        "PIPELINE START | %s | application_id=%s | timestamp=%s",
        config.pipeline_name,
        application_id,
        execution_timestamp,
    )

    try:
        summary = run_validation(spark, config, logger)
        summary["spark_application_id"] = application_id
        summary["spark_version"] = spark.version
        summary["execution_timestamp_utc"] = execution_timestamp
        summary["execution_time_seconds"] = round(time.time() - pipeline_start_time, 2)

        write_validation_summary(summary, config, logger)

        logger.info("Validation status: %s", summary["validation_status"])
    except PipelineError:
        logger.error("Pipeline terminated due to a fatal validation error.", exc_info=True)
        raise
    except Exception:
        logger.error("Pipeline terminated due to an unexpected error.", exc_info=True)
        raise
    finally:
        elapsed = time.time() - pipeline_start_time
        logger.info(
            "PIPELINE END | %s | application_id=%s | elapsed_seconds=%.2f",
            config.pipeline_name,
            application_id,
            elapsed,
        )
        spark.stop()


if __name__ == "__main__":
    main()
