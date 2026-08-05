#!/usr/bin/env python3
"""Configuration for the Hybrid RAG Intelligent Product Search pipeline.

This module defines every configuration value consumed by the current
pipeline stage, ``06_Text_Chunking`` (Chunk Generation), and by the
shared ``logger.py``, ``schema.py``, and ``utils.py`` modules.

All configuration is expressed as immutable (frozen) dataclasses grouped
by concern (project metadata, S3 layout, Spark runtime, chunking
parameters, execution runtime, output writing, validation thresholds,
and logging). A single module-level ``settings`` instance, built from an
aggregating ``MasterConfig``, is the intended entry point for callers.
Every future module in this pipeline must obtain configuration through
``settings`` rather than declaring its own local defaults, so this file
remains the single source of truth for every configurable value.

This module contains no business logic, no Spark code, and no helper
utilities; it only declares configuration. Lightweight, dependency-free
shape validation (e.g. "does this look like an s3:// URI") is performed
in ``__post_init__`` hooks using only the standard library, so this
module never imports ``utils``, ``logger``, or ``schema`` and therefore
cannot participate in an import cycle with them.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

# ---------------------------------------------------------------------------
# Logging support types
# ---------------------------------------------------------------------------


class LogLevel(Enum):
    """Enumeration of supported logging levels.

    Mirrors the standard library's ``logging`` module levels so that
    ``LoggingConfig.log_level.value`` is a valid argument to
    ``logging.Logger.setLevel``.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


# ---------------------------------------------------------------------------
# Shared validation helpers (stdlib-only; not exported as a public API)
# ---------------------------------------------------------------------------

# A conservative, intentionally strict pattern: requires a trailing slash
# so every configured path is unambiguously a "directory" prefix that
# downstream Spark readers/writers and manifest writers can safely join
# object/file names onto without a caller having to remember to add one.
_S3_DIRECTORY_URI_PATTERN = re.compile(
    r"^s3://(?P<bucket>[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9])/(?P<key>.+/)$"
)


def _require_s3_directory_uri(value: str, field_name: str) -> str:
    """Validate that ``value`` is a well-formed, trailing-slash S3 URI.

    Args:
        value: Candidate S3 URI.
        field_name: Name of the field being validated, used only to
            produce an actionable error message.

    Returns:
        ``value`` unchanged, when valid.

    Raises:
        ValueError: If ``value`` is not a syntactically valid
            ``s3://bucket/key/`` URI.
    """
    if not isinstance(value, str) or not _S3_DIRECTORY_URI_PATTERN.match(value):
        raise ValueError(
            f"{field_name}={value!r} must be a complete 's3://bucket/key/' URI "
            "with a trailing slash."
        )
    return value


def _require_non_empty(value: str, field_name: str) -> str:
    """Validate that ``value`` is a non-blank string.

    Args:
        value: Candidate string.
        field_name: Name of the field being validated, used only to
            produce an actionable error message.

    Returns:
        ``value`` unchanged, when valid.

    Raises:
        ValueError: If ``value`` is not a string or is blank.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


# ---------------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProjectConfig:
    """High-level project identity and dataset metadata.

    Attributes:
        project_name: Human-readable name of the overall project.
        pipeline_stage: Identifier of the currently executing pipeline
            stage.
        product_categories: Product categories covered by the dataset.
        product_count: Total number of products in the dataset.
    """

    project_name: str = "Hybrid RAG Intelligent Product Search"
    pipeline_stage: str = "06_Text_Chunking"
    product_categories: Tuple[str, ...] = (
        "Video Games",
        "Musical Instruments",
        "Appliances",
    )
    product_count: int = 445_139


# ---------------------------------------------------------------------------
# S3 configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class S3Config:
    """Authoritative S3 layout for the Chunk Generation stage.

    Every path is a complete ``s3://bucket/key/`` URI so downstream
    Spark readers/writers and manifest utilities can consume a path
    directly, without reconstructing it from a separately configured
    bucket and prefix.

    Attributes:
        bucket_name: S3 bucket backing the pipeline's data lake.
        final_documents_input_path: Location of validated Final
            Documents (the input to this stage).
        chunk_output_path: Location generated chunks are written to.
        chunk_validation_path: Location chunk-validation results are
            written to.
        manifest_output_path: Location run manifests and metadata
            records are written to.
        temporary_path: Scratch location for intermediate/temporary
            artifacts (e.g. Spark checkpointing, staged writes).
        region_name: AWS region hosting ``bucket_name``.
    """

    bucket_name: str = "ml-data-aws-transformer-bert"
    final_documents_input_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/preprocessing/final_documents/"
    )
    chunk_output_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/chunking/chunked_documents/"
    )
    chunk_validation_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/chunking/validation/"
    )
    manifest_output_path: str = (
        "s3://ml-data-aws-transformer-bert/ml/chunking/manifests/"
    )
    temporary_path: str = "s3://ml-data-aws-transformer-bert/ml/temp/"
    region_name: str = "us-east-1"

    def __post_init__(self) -> None:
        """Defensively validate every configured path at construction time.

        Failing fast here (rather than letting a malformed path surface
        as an opaque Spark I/O error mid-job) is cheap and turns a bad
        configuration into an immediate, actionable startup error.

        Raises:
            ValueError: If ``bucket_name`` is blank, if any path is not a
                well-formed ``s3://bucket/key/`` URI, or if a path's
                bucket does not match ``bucket_name``.
        """
        _require_non_empty(self.bucket_name, "bucket_name")
        for path_field_name in (
            "final_documents_input_path",
            "chunk_output_path",
            "chunk_validation_path",
            "manifest_output_path",
            "temporary_path",
        ):
            path_value = getattr(self, path_field_name)
            _require_s3_directory_uri(path_value, path_field_name)
            path_bucket = path_value[len("s3://"):].split("/", 1)[0]
            if path_bucket != self.bucket_name:
                raise ValueError(
                    f"{path_field_name}={path_value!r} does not belong to "
                    f"bucket_name={self.bucket_name!r}."
                )


# ---------------------------------------------------------------------------
# Spark configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SparkConfig:
    """Spark session and execution tuning parameters for EMR.

    Attributes:
        app_name: Spark application name, as shown in the YARN/EMR UI.
        shuffle_partitions: Value for ``spark.sql.shuffle.partitions``.
        executor_memory: Value for ``spark.executor.memory``.
        driver_memory: Value for ``spark.driver.memory``.
        dynamic_allocation_enabled: Whether dynamic executor allocation is
            enabled.
        arrow_pyspark_enabled: Whether Arrow-based columnar transfer is
            enabled for pandas UDFs.
        s3_committer_name: Value for
            ``spark.sql.sources.commitProtocolClass``/EMRFS S3-optimized
            committer selection. Using the EMRFS S3-optimized committer
            avoids the rename-based commit protocol's O(n) S3 rename cost
            at this dataset's output volume.
        speculative_execution_enabled: Value for ``spark.speculation``.
            Guards against a single slow/stalled EMR task-node executor
            (a "straggler") holding up the entire chunking stage.
        max_result_size: Value for ``spark.driver.maxResultSize``, sized
            to comfortably hold this stage's driver-side aggregation
            (e.g. manifest/metrics collection) without risking an
            out-of-memory driver.
    """

    app_name: str = "hybrid-rag-chunk-generation"
    shuffle_partitions: int = 800
    executor_memory: str = "8g"
    driver_memory: str = "8g"
    dynamic_allocation_enabled: bool = True
    arrow_pyspark_enabled: bool = True
    s3_committer_name: str = "partitioned"
    speculative_execution_enabled: bool = True
    max_result_size: str = "4g"


# ---------------------------------------------------------------------------
# Chunk generation configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChunkConfig:
    """Parameters governing how Final Documents are split into chunks.

    Attributes:
        target_chunk_chars: Target character length for a generated
            chunk.
        min_chunk_chars: Minimum acceptable chunk length, in characters.
        max_chunk_chars: Maximum acceptable chunk length, in characters.
        chunk_overlap_chars: Number of characters of overlap carried
            between consecutive chunks of the same source document.
        chars_per_token: Assumed average characters per token, used for
            cheap token-count estimation.
        paragraph_separator: Delimiter treated as a paragraph boundary
            when splitting source text.
        min_alphanumeric_ratio: Minimum required ratio of alphanumeric
            characters for a chunk to be considered meaningful content.
    """

    target_chunk_chars: int = 1_000
    min_chunk_chars: int = 200
    max_chunk_chars: int = 1_500
    chunk_overlap_chars: int = 150
    chars_per_token: float = 4.0
    paragraph_separator: str = "\n\n"
    min_alphanumeric_ratio: float = 0.3


# ---------------------------------------------------------------------------
# Runtime configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuntimeConfig:
    """Execution-environment settings for a single pipeline run.

    Attributes:
        environment: Deployment environment this run executes in.
        random_seed: Seed used wherever deterministic-but-arbitrary
            ordering is required.
    """

    environment: str = "production"
    random_seed: int = 42


# ---------------------------------------------------------------------------
# Output configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OutputConfig:
    """Settings controlling how generated chunks are written to storage.

    Attributes:
        output_format: File format used to persist chunk output.
        write_mode: Spark ``DataFrameWriter`` save mode.
        output_partition_count: Number of output partitions/files to
            coalesce to before writing.
        compression_codec: Compression codec applied to output files.
    """

    output_format: str = "parquet"
    write_mode: str = "overwrite"
    output_partition_count: int = 200
    compression_codec: str = "snappy"


# ---------------------------------------------------------------------------
# Validation configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationConfig:
    """Thresholds used when validating generated chunks.

    ``min_chunk_chars``/``max_chunk_chars``/``min_alphanumeric_ratio``
    intentionally mirror the corresponding ``ChunkConfig`` fields: the
    Chunk Generation stage uses them as *targets* while the downstream
    Chunk Validation stage uses this copy as an independent *pass/fail
    gate*. Collapsing them into one field would force both stages to
    always agree, which would silently defeat the validation stage's
    purpose of catching generation-stage regressions. They are kept as
    separate, explicitly-named fields rather than removed.

    Attributes:
        min_chunk_chars: Inclusive minimum acceptable chunk length, in
            characters, used for pass/fail length checks.
        max_chunk_chars: Inclusive maximum acceptable chunk length, in
            characters, used for pass/fail length checks.
        min_alphanumeric_ratio: Minimum required alphanumeric-character
            ratio for a chunk to pass content-quality validation.
        max_allowed_failure_rate: Maximum fraction of chunks permitted to
            fail validation before the stage itself is considered failed.
    """

    min_chunk_chars: int = 200
    max_chunk_chars: int = 1_500
    min_alphanumeric_ratio: float = 0.3
    max_allowed_failure_rate: float = 0.02


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LoggingConfig:
    """Logging behavior consumed by ``logger.LoggerFactory``.

    Attributes:
        logger_name: Default logger name used for logging-side
            diagnostics (e.g. file-handler creation failures).
        log_level: Level applied to configured loggers.
        enable_console_logging: Whether a stdout stream handler is
            attached.
        enable_file_logging: Whether a rotating file handler is attached.
        structured_json_logging: Whether log records are emitted as
            single-line JSON instead of plain text.
        log_format: ``logging.Formatter`` format string used when
            ``structured_json_logging`` is ``False``.
        date_format: ``logging.Formatter`` date format string used when
            ``structured_json_logging`` is ``False``.
        log_file_directory: Local directory rotating log files are
            written to.
        log_file_name: File name of the active rotating log file.
        max_log_file_size_bytes: Size, in bytes, at which the log file is
            rotated.
        backup_count: Number of rotated backup log files retained.
    """

    logger_name: str = "hybrid_rag_pipeline"
    log_level: LogLevel = LogLevel.INFO
    enable_console_logging: bool = True
    enable_file_logging: bool = False
    structured_json_logging: bool = True
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    log_file_directory: str = "/tmp/hybrid_rag_pipeline/logs"
    log_file_name: str = "06_text_chunking.log"
    max_log_file_size_bytes: int = 50 * 1024 * 1024
    backup_count: int = 5


# ---------------------------------------------------------------------------
# Master configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MasterConfig:
    """Aggregate root composing every configuration section.

    Attributes:
        project: Project identity and dataset metadata.
        s3: S3 bucket and path layout.
        spark: Spark session and execution tuning parameters.
        chunk: Chunk generation parameters.
        runtime: Execution-environment settings.
        output: Chunk-output writing settings.
        validation: Chunk validation thresholds.
        logging: Logging behavior.
    """

    project: ProjectConfig = field(default_factory=ProjectConfig)
    s3: S3Config = field(default_factory=S3Config)
    spark: SparkConfig = field(default_factory=SparkConfig)
    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


settings = MasterConfig()
