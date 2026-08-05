#!/usr/bin/env python3
"""Production entry point for the Chunk Generation pipeline stage.

Stage: ``06_Text_Chunking``. Executed via ``spark-submit`` on Amazon EMR.

Reads validated Final Documents, splits each document into semantically
coherent, retrieval-optimized chunks using an adaptive
paragraph -> sentence -> whitespace splitting strategy, assigns
deterministic chunk identity and sibling links, validates the resulting
schema, and writes the chunk dataset to Parquet on S3 alongside a run
manifest.

This module composes ``config.py``, ``logger.py``, ``schema.py``, and
``utils.py`` exactly as published; none of those modules are modified.
Every S3 location this stage reads from or writes to is sourced from
``config.settings.s3`` (``config.S3Config``); no S3 path is hardcoded
in this module.

Usage::

    spark-submit \\
        --py-files config.py,logger.py,schema.py,utils.py \\
        01_generate_chunks.py \\
        [--input-path S3_URI] [--output-path S3_URI] \\
        [--validation-path S3_URI] [--manifest-path S3_URI]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, fields, replace
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, IntegerType, StringType, StructField, StructType

from config import (
    ChunkConfig,
    MasterConfig,
    OutputConfig,
    S3Config,
    SparkConfig,
    settings,
)
from logger import ExecutionTimer, get_logger, suppress_verbose_third_party_logging
from schema import (
    CHUNK_OUTPUT_SCHEMA,
    FINAL_DOCUMENT_SCHEMA,
    PARTITION_COLUMNS,
    ChunkOutputColumns,
    ExecutionMetadataColumns,
    InputColumns,
    PipelineMetadataColumns,
    SchemaValidationError,
    SchemaValidator,
)
from utils import (
    Stopwatch,
    count_characters,
    estimate_token_count,
    generate_chunk_id,
    generate_uuid4,
    has_minimum_alphanumeric_ratio,
    is_blank,
    normalize_paragraph_structure,
    normalize_text,
    normalize_whitespace,
    validate_positive_integer,
    validate_s3_uri,
)

_LOGGER = get_logger(__name__, settings.logging)

# Columns required from the Final Documents dataset to generate chunks.
# Only these columns are read/selected, per the "read only required
# columns" Spark best practice, which lets the Parquet reader skip
# column groups it never touches.
_REQUIRED_INPUT_COLUMNS: Tuple[str, ...] = (
    InputColumns.PARENT_ASIN,
    InputColumns.CATEGORY,
    InputColumns.PRODUCT_TITLE,
    InputColumns.DOCUMENT_TEXT,
)

# Suffix convention used to recognize which fields of a dataclass carry
# S3 locations, so path validation/resolution can operate generically
# over any dataclass (currently ``config.S3Config``) without hardcoding
# a fixed list of field names.
_S3_PATH_FIELD_SUFFIX: str = "_path"


class ChunkGenerationPipelineError(Exception):
    """Raised for fatal, non-recoverable failures of the pipeline run."""


# ---------------------------------------------------------------------------
# Adaptive chunking parameters
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AdaptiveChunkingParameters:
    """Token-based sizing parameters for the adaptive chunking strategy.

    Character-level thresholds used by the splitting/packing algorithm are
    derived from these token counts via ``chars_per_token``, which is
    reused from ``config.ChunkConfig`` rather than redeclared, so a single
    token/character conversion ratio is shared across the pipeline.

    Attributes:
        target_min_tokens: Lower bound of the desired per-chunk token
            range.
        target_max_tokens: Upper bound of the desired per-chunk token
            range; chunk packing flushes once a chunk reaches this size.
        min_tokens: Absolute minimum per-chunk token count; chunks smaller
            than this are merged into a neighbor where possible.
        max_tokens: Absolute maximum per-chunk token count; never
            exceeded by packing.
        overlap_tokens: Approximate number of trailing tokens from a
            chunk carried forward as leading context in the next chunk.
        chars_per_token: Assumed average characters per token, reused
            from ``config.ChunkConfig.chars_per_token``.
        paragraph_separator: Paragraph boundary delimiter, reused from
            ``config.ChunkConfig.paragraph_separator``.
        min_alphanumeric_ratio: Minimum alphanumeric-character ratio a
            finished chunk must meet to be retained, reused from
            ``config.ChunkConfig.min_alphanumeric_ratio``.
    """

    target_min_tokens: int = 350
    target_max_tokens: int = 500
    min_tokens: int = 200
    max_tokens: int = 600
    overlap_tokens: int = 50
    chars_per_token: float = settings.chunk.chars_per_token
    paragraph_separator: str = settings.chunk.paragraph_separator
    min_alphanumeric_ratio: float = settings.chunk.min_alphanumeric_ratio

    def __post_init__(self) -> None:
        """Validate internal consistency of the configured token thresholds.

        Raises:
            ValueError: If the thresholds are not in a sane, internally
                consistent order, or if ``chars_per_token`` is not
                strictly positive.
        """
        if self.chars_per_token <= 0:
            raise ValueError("chars_per_token must be strictly positive.")
        if not (0 < self.min_tokens <= self.target_min_tokens <= self.target_max_tokens <= self.max_tokens):
            raise ValueError(
                "Token thresholds must satisfy "
                "0 < min_tokens <= target_min_tokens <= target_max_tokens <= max_tokens; "
                f"got min={self.min_tokens}, target_min={self.target_min_tokens}, "
                f"target_max={self.target_max_tokens}, max={self.max_tokens}."
            )
        if self.overlap_tokens < 0 or self.overlap_tokens >= self.min_tokens:
            raise ValueError(
                "overlap_tokens must be non-negative and smaller than min_tokens; "
                f"got overlap_tokens={self.overlap_tokens}, min_tokens={self.min_tokens}."
            )

    @property
    def min_chars(self) -> int:
        """Minimum per-chunk character count derived from ``min_tokens``."""
        return max(1, round(self.min_tokens * self.chars_per_token))

    @property
    def max_chars(self) -> int:
        """Maximum per-chunk character count derived from ``max_tokens``."""
        return max(self.min_chars, round(self.max_tokens * self.chars_per_token))

    @property
    def target_max_chars(self) -> int:
        """Soft flush threshold derived from ``target_max_tokens``."""
        return max(self.min_chars, round(self.target_max_tokens * self.chars_per_token))

    @property
    def overlap_chars(self) -> int:
        """Overlap character count derived from ``overlap_tokens``."""
        return max(0, round(self.overlap_tokens * self.chars_per_token))


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------


class ConfigurationValidator:
    """Validates configuration and runtime inputs before Spark initialization.

    Failing fast here, before a ``SparkSession`` is created, avoids
    spinning up executors for a run that is guaranteed to fail.
    """

    @staticmethod
    def validate_chunk_config(chunk_config: ChunkConfig) -> None:
        """Validate internal consistency of ``config.ChunkConfig``.

        Args:
            chunk_config: Chunk configuration to validate.

        Raises:
            ChunkGenerationPipelineError: If the configuration is
                internally inconsistent.
        """
        if not (0 < chunk_config.min_chunk_chars <= chunk_config.target_chunk_chars <= chunk_config.max_chunk_chars):
            raise ChunkGenerationPipelineError(
                "config.ChunkConfig has inconsistent character thresholds: "
                f"min={chunk_config.min_chunk_chars}, target={chunk_config.target_chunk_chars}, "
                f"max={chunk_config.max_chunk_chars}."
            )
        if chunk_config.chunk_overlap_chars < 0 or chunk_config.chunk_overlap_chars >= chunk_config.min_chunk_chars:
            raise ChunkGenerationPipelineError(
                "config.ChunkConfig.chunk_overlap_chars must be non-negative and smaller "
                f"than min_chunk_chars; got {chunk_config.chunk_overlap_chars}."
            )
        validate_positive_integer(chunk_config.target_chunk_chars, "target_chunk_chars")

    @staticmethod
    def validate_s3_paths(s3_config: S3Config) -> None:
        """Validate that every S3-location field on ``s3_config`` is a valid URI.

        Operates generically over every dataclass field whose name ends
        in ``_path`` (currently every location field on
        ``config.S3Config``), so a new path field added to
        ``config.S3Config`` in the future is automatically covered
        without a corresponding change to this method.

        Args:
            s3_config: Resolved S3 configuration for this run (normally
                ``config.settings.s3``, optionally overridden per-field
                by CLI arguments).

        Raises:
            ChunkGenerationPipelineError: If any ``*_path`` field is not
                a valid ``s3://bucket/key`` URI.
        """
        invalid_paths: List[str] = []
        for path_field in fields(s3_config):
            if not path_field.name.endswith(_S3_PATH_FIELD_SUFFIX):
                continue
            uri = getattr(s3_config, path_field.name)
            if not validate_s3_uri(uri):
                invalid_paths.append(f"{path_field.name}={uri!r}")
        if invalid_paths:
            raise ChunkGenerationPipelineError(
                f"Invalid S3 URI(s) in S3 configuration: {', '.join(invalid_paths)}."
            )

    @staticmethod
    def validate_all(
        chunk_config: ChunkConfig,
        chunking_parameters: AdaptiveChunkingParameters,
        s3_config: S3Config,
    ) -> None:
        """Run every configuration validation check.

        ``chunking_parameters`` self-validates in ``__post_init__``, so
        constructing it successfully already proves its own consistency;
        it is accepted here only so the full validation surface is
        visible from a single call site.

        Args:
            chunk_config: Chunk configuration to validate.
            chunking_parameters: Adaptive chunking parameters (already
                validated at construction time).
            s3_config: Resolved S3 configuration for this run.

        Raises:
            ChunkGenerationPipelineError: If any check fails.
        """
        with ExecutionTimer(_LOGGER, "validate_configuration"):
            ConfigurationValidator.validate_chunk_config(chunk_config)
            ConfigurationValidator.validate_s3_paths(s3_config)
            _LOGGER.info(
                "Configuration validated | target_tokens=%d-%d | min_tokens=%d | "
                "max_tokens=%d | overlap_tokens=%d",
                chunking_parameters.target_min_tokens,
                chunking_parameters.target_max_tokens,
                chunking_parameters.min_tokens,
                chunking_parameters.max_tokens,
                chunking_parameters.overlap_tokens,
            )


# ---------------------------------------------------------------------------
# Spark session factory
# ---------------------------------------------------------------------------


class SparkSessionFactory:
    """Builds the ``SparkSession`` used by this stage from ``config.py`` values."""

    @staticmethod
    def create_spark_session(
        spark_config: SparkConfig, output_config: OutputConfig
    ) -> SparkSession:
        """Build and configure a ``SparkSession`` for the Chunk Generation stage.

        Every tunable is sourced from ``config.SparkConfig``/
        ``config.OutputConfig``; nothing here is hardcoded independently
        of ``config.py``. Adaptive Query Execution is enabled so Spark
        coalesces post-shuffle partitions and mitigates data skew at
        runtime, reducing the amount of manual shuffle-partition tuning
        this stage would otherwise require.

        Args:
            spark_config: Spark session and execution tuning parameters.
            output_config: Output writing settings, used to align the
                Parquet compression codec.

        Returns:
            A configured, active ``SparkSession``.
        """
        builder = (
            SparkSession.builder.appName(spark_config.app_name)
            .config("spark.sql.shuffle.partitions", spark_config.shuffle_partitions)
            .config("spark.executor.memory", spark_config.executor_memory)
            .config("spark.driver.memory", spark_config.driver_memory)
            .config("spark.driver.maxResultSize", spark_config.max_result_size)
            .config(
                "spark.dynamicAllocation.enabled",
                str(spark_config.dynamic_allocation_enabled).lower(),
            )
            .config(
                "spark.speculation",
                str(spark_config.speculative_execution_enabled).lower(),
            )
            .config(
                "spark.sql.execution.arrow.pyspark.enabled",
                str(spark_config.arrow_pyspark_enabled).lower(),
            )
            .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.sql.adaptive.skewJoin.enabled", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.sql.parquet.compression.codec", output_config.compression_codec)
            # EMRFS S3-optimized committer: avoids the rename-based commit
            # protocol's O(n) S3 rename cost at this dataset's output
            # volume and is the EMR-recommended committer for Parquet
            # writes to S3.
            .config("spark.sql.sources.commitProtocolClass",
                     "org.apache.spark.internal.io.cloud.PathOutputCommitProtocol")
            .config("spark.sql.parquet.output.committer.class",
                     "org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter")
            .config("spark.hadoop.fs.s3a.committer.name", spark_config.s3_committer_name)
            .config("spark.hadoop.fs.s3a.committer.magic.enabled", "true")
        )
        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        return spark


# ---------------------------------------------------------------------------
# Document reader
# ---------------------------------------------------------------------------


class DocumentReader:
    """Reads and validates the Final Documents dataset."""

    def __init__(self, spark: SparkSession) -> None:
        """Initialize the reader.

        Args:
            spark: Active ``SparkSession``.
        """
        self._spark = spark

    def read_final_documents(self, input_path: str) -> DataFrame:
        """Read, validate, and project the Final Documents dataset.

        Parquet is self-describing, so the underlying file's schema is
        read from its footer (a metadata-only operation, not a data scan)
        and validated against ``schema.FINAL_DOCUMENT_SCHEMA`` before any
        column is selected. Only the columns this stage needs are then
        explicitly selected and cast, so no reliance is placed on
        implicit type coercion and no unused column group is ever
        materialized off S3.

        Args:
            input_path: S3 prefix to read Final Documents Parquet files
                from (sourced from ``config.settings.s3`` by the caller).

        Returns:
            A ``DataFrame`` containing exactly
            ``schema.InputColumns.PARENT_ASIN``,
            ``schema.InputColumns.CATEGORY``,
            ``schema.InputColumns.PRODUCT_TITLE``, and
            ``schema.InputColumns.DOCUMENT_TEXT``.

        Raises:
            SchemaValidationError: If the underlying dataset is missing
                required columns or has incompatible column types.
            ChunkGenerationPipelineError: If the Parquet dataset at
                ``input_path`` cannot be read at all (e.g. missing
                prefix, access denied).
        """
        with ExecutionTimer(_LOGGER, "read_final_documents"):
            try:
                raw_df = self._spark.read.parquet(input_path)
            except Exception as exc:
                raise ChunkGenerationPipelineError(
                    f"Failed to read Final Documents from '{input_path}': {exc}"
                ) from exc

            validation_result = SchemaValidator.validate_schema_compatibility(
                raw_df.schema, FINAL_DOCUMENT_SCHEMA, allow_unexpected_columns=True
            )
            if not validation_result.is_valid:
                raise SchemaValidationError(
                    "Final Documents input schema is incompatible: "
                    f"missing={validation_result.missing_columns}, "
                    f"datatype_mismatches={validation_result.datatype_mismatches}, "
                    f"nullability_mismatches={validation_result.nullability_mismatches}."
                )

            expected_types = {
                struct_field.name: struct_field.dataType
                for struct_field in FINAL_DOCUMENT_SCHEMA.fields
                if struct_field.name in _REQUIRED_INPUT_COLUMNS
            }
            projected_df = raw_df.select(
                *[
                    F.col(column_name).cast(expected_types[column_name]).alias(column_name)
                    for column_name in _REQUIRED_INPUT_COLUMNS
                ]
            )
            _LOGGER.info("Final Documents read from '%s'.", input_path)
        return projected_df

    def filter_valid_documents(self, df: DataFrame) -> DataFrame:
        """Drop rows with a missing required identifier or blank document text.

        Args:
            df: Projected Final Documents ``DataFrame``.

        Returns:
            A ``DataFrame`` containing only rows with non-blank
            ``parent_asin``, ``category``, and ``document_text`` values.
        """
        with ExecutionTimer(_LOGGER, "filter_valid_documents"):
            filtered_df = df.filter(
                F.col(InputColumns.PARENT_ASIN).isNotNull()
                & (F.length(F.trim(F.col(InputColumns.PARENT_ASIN))) > 0)
                & F.col(InputColumns.CATEGORY).isNotNull()
                & (F.length(F.trim(F.col(InputColumns.CATEGORY))) > 0)
                & F.col(InputColumns.DOCUMENT_TEXT).isNotNull()
                & (F.length(F.trim(F.col(InputColumns.DOCUMENT_TEXT))) > 0)
            )
        return filtered_df


# ---------------------------------------------------------------------------
# Adaptive chunking algorithm (pure Python, unit-testable in isolation)
# ---------------------------------------------------------------------------

_SENTENCE_BOUNDARY_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


class AdaptiveChunker:
    """Splits a single document's text into semantically coherent chunks.

    Strategy: prefer paragraph boundaries; recursively fall back to
    sentence boundaries, then whitespace boundaries, for any segment that
    exceeds ``params.max_chars``; never split inside a word; greedily
    pack segments toward ``params.target_max_chars``; merge chunks that
    fall below ``params.min_chars`` into a neighbor; finally carry
    trailing context forward as overlap between consecutive chunks.

    Contains no Spark code; a single instance is safe to reuse across
    many documents within one executor task (see
    ``_build_chunk_generation_udf``), since it holds no per-call
    mutable state.
    """

    def __init__(self, params: AdaptiveChunkingParameters) -> None:
        """Initialize the chunker.

        Args:
            params: Adaptive chunking sizing parameters.
        """
        self._params = params

    def chunk_document(self, document_text: Optional[str]) -> List[Dict[str, Any]]:
        """Chunk a single document's text into ordered chunk records.

        Args:
            document_text: Raw document text to chunk.

        Returns:
            An ordered list of dictionaries, each with keys
            ``chunk_number`` (zero-based, contiguous), ``chunk_text``,
            ``token_count``, and ``character_count``. Returns an empty
            list for blank or unusable input.
        """
        normalized = normalize_paragraph_structure(normalize_text(document_text))
        if is_blank(normalized):
            return []

        raw_paragraphs = [
            paragraph.strip()
            for paragraph in normalized.split(self._params.paragraph_separator)
            if not is_blank(paragraph)
        ]
        if not raw_paragraphs:
            raw_paragraphs = [normalized]

        atomic_segments: List[str] = []
        for paragraph in raw_paragraphs:
            atomic_segments.extend(self._decompose_segment(paragraph))
        if not atomic_segments:
            return []

        packed_chunks = self._pack_segments(atomic_segments)
        merged_chunks = self._merge_tiny_chunks(packed_chunks)
        final_chunks = self._apply_overlap(merged_chunks)

        records: List[Dict[str, Any]] = []
        for chunk_text in final_chunks:
            cleaned = normalize_whitespace(chunk_text)
            if is_blank(cleaned):
                continue
            if not has_minimum_alphanumeric_ratio(cleaned, self._params.min_alphanumeric_ratio):
                continue
            records.append(
                {
                    "chunk_text": cleaned,
                    "token_count": estimate_token_count(cleaned, self._params.chars_per_token),
                    "character_count": count_characters(cleaned),
                }
            )

        return [
            {"chunk_number": chunk_number, **record}
            for chunk_number, record in enumerate(records)
        ]

    def _decompose_segment(self, segment: str) -> List[str]:
        """Recursively split ``segment`` until every piece fits within ``max_chars``.

        Args:
            segment: Text segment to decompose (typically a paragraph or
                a sentence).

        Returns:
            A list of segments, each no longer than
            ``params.max_chars`` (except for a single unsplittable word
            longer than ``max_chars``, which is kept intact since words
            are never split).
        """
        segment = segment.strip()
        if not segment:
            return []
        if len(segment) <= self._params.max_chars:
            return [segment]

        sentences = self._split_into_sentences(segment)
        if len(sentences) > 1:
            decomposed: List[str] = []
            for sentence in sentences:
                decomposed.extend(self._decompose_segment(sentence))
            return decomposed

        return self._split_by_whitespace(segment)

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split ``text`` into sentences using punctuation-boundary heuristics.

        Args:
            text: Text to split.

        Returns:
            A list of non-blank sentence strings.
        """
        return [sentence.strip() for sentence in _SENTENCE_BOUNDARY_PATTERN.split(text) if sentence.strip()]

    def _split_by_whitespace(self, text: str) -> List[str]:
        """Greedily pack whitespace-delimited words into ``max_chars``-bounded pieces.

        Words are never split. A single word longer than ``max_chars``
        (e.g. a long URL or identifier) is kept intact as its own,
        oversized piece rather than being broken apart.

        Args:
            text: Text to split.

        Returns:
            A list of word-respecting pieces.
        """
        words = text.split()
        if not words:
            return []

        pieces: List[str] = []
        buffer = ""
        for word in words:
            candidate = f"{buffer} {word}".strip() if buffer else word
            if len(candidate) <= self._params.max_chars:
                buffer = candidate
                continue
            if buffer:
                pieces.append(buffer)
                buffer = ""
            if len(word) <= self._params.max_chars:
                buffer = word
            else:
                pieces.append(word)
        if buffer:
            pieces.append(buffer)
        return pieces

    def _pack_segments(self, segments: Sequence[str]) -> List[str]:
        """Greedily pack ordered segments into chunks bounded by ``max_chars``.

        A chunk is flushed once appending the next segment would exceed
        ``params.max_chars``, or once the chunk already reaches
        ``params.target_max_chars`` (the soft target), whichever comes
        first.

        Args:
            segments: Ordered, already-decomposed segments, each no
                longer than ``params.max_chars``.

        Returns:
            A list of packed chunk strings.
        """
        chunks: List[str] = []
        buffer = ""
        for segment in segments:
            candidate = f"{buffer} {segment}".strip() if buffer else segment
            if len(candidate) <= self._params.max_chars:
                buffer = candidate
                if len(buffer) >= self._params.target_max_chars:
                    chunks.append(buffer)
                    buffer = ""
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(segment) <= self._params.max_chars:
                buffer = segment
                if len(buffer) >= self._params.target_max_chars:
                    chunks.append(buffer)
                    buffer = ""
            else:
                chunks.append(segment)

        if buffer:
            chunks.append(buffer)
        return chunks

    def _merge_tiny_chunks(self, chunks: Sequence[str]) -> List[str]:
        """Merge chunks smaller than ``min_chars`` into an adjacent chunk.

        Prefers merging a tiny chunk forward into its successor; falls
        back to merging backward into the previously finalized chunk when
        there is no successor (or the merge would exceed ``max_chars``).
        A chunk that cannot be merged in either direction without
        exceeding ``max_chars`` is retained as-is, since this pipeline
        stage never discards content.

        Args:
            chunks: Ordered chunk strings to merge.

        Returns:
            An ordered list of merged chunk strings.
        """
        if not chunks:
            return []

        working_chunks = list(chunks)
        merged: List[str] = []
        index = 0
        while index < len(working_chunks):
            current = working_chunks[index]
            is_tiny = len(current) < self._params.min_chars

            if is_tiny and index + 1 < len(working_chunks):
                candidate = f"{current} {working_chunks[index + 1]}".strip()
                if len(candidate) <= self._params.max_chars:
                    working_chunks[index + 1] = candidate
                    index += 1
                    continue

            if is_tiny and merged:
                candidate = f"{merged[-1]} {current}".strip()
                if len(candidate) <= self._params.max_chars:
                    merged[-1] = candidate
                    index += 1
                    continue

            merged.append(current)
            index += 1

        return merged

    def _apply_overlap(self, chunks: Sequence[str]) -> List[str]:
        """Prepend trailing context from each chunk to the next chunk.

        Args:
            chunks: Ordered, merged chunk strings.

        Returns:
            An ordered list of chunk strings, each (other than the first)
            prefixed with up to ``params.overlap_chars`` characters of
            trailing context from its predecessor, trimmed to a
            whitespace boundary so no word is split.
        """
        if len(chunks) <= 1 or self._params.overlap_chars <= 0:
            return list(chunks)

        overlapped: List[str] = [chunks[0]]
        for index in range(1, len(chunks)):
            overlap_text = self._extract_overlap_tail(chunks[index - 1])
            current_chunk = chunks[index]
            combined = f"{overlap_text} {current_chunk}".strip() if overlap_text else current_chunk
            overlapped.append(combined)
        return overlapped

    def _extract_overlap_tail(self, text: str) -> str:
        """Extract up to ``overlap_chars`` trailing characters, trimmed to a word boundary.

        Args:
            text: Text to extract trailing context from.

        Returns:
            The trailing overlap text, guaranteed not to start mid-word.
        """
        overlap_chars = self._params.overlap_chars
        if overlap_chars <= 0 or not text:
            return ""
        tail = text[-overlap_chars:]
        first_space_index = tail.find(" ")
        if first_space_index > 0:
            tail = tail[first_space_index + 1 :]
        return tail.strip()


# ---------------------------------------------------------------------------
# Chunk generator (Spark orchestration around AdaptiveChunker)
# ---------------------------------------------------------------------------

_CHUNK_RECORD_FIELD_SCHEMA = StructType(
    [
        StructField("chunk_number", IntegerType(), nullable=False),
        StructField("chunk_text", StringType(), nullable=False),
        StructField("token_count", IntegerType(), nullable=False),
        StructField("character_count", IntegerType(), nullable=False),
    ]
)

_CHUNK_IDENTITY_SCHEMA = StructType(
    [
        StructField("chunk_id", StringType(), nullable=False),
        StructField("previous_chunk_id", StringType(), nullable=True),
        StructField("next_chunk_id", StringType(), nullable=True),
    ]
)


def _build_chunk_generation_udf(params: AdaptiveChunkingParameters):
    """Build the per-document chunking UDF.

    A PySpark UDF is used to expand a single document row into a variable 
    number of semantically-derived chunk rows. The single ``AdaptiveChunker`` 
    instance is constructed once and reused. The UDF returns an array of 
    structs so the whole array can be exploded with a single, built-in 
    ``explode`` call rather than driving the row-multiplication through 
    RDD-level operations.

    Args:
        params: Adaptive chunking sizing parameters.

    Returns:
        A Spark SQL UDF mapping document text to
        ``array<struct<chunk_number,chunk_text,token_count,character_count>>``.
    """
    chunker = AdaptiveChunker(params)

    @F.udf(ArrayType(_CHUNK_RECORD_FIELD_SCHEMA))
    def _chunk_documents(document_text: str) -> List[Dict[str, Any]]:
        return chunker.chunk_document(document_text)

    return _chunk_documents


def _build_chunk_identity_udf():
    """Build the deterministic chunk-identity UDF.

    Reuses ``utils.generate_chunk_id`` so chunk identifiers, and their
    forward/backward sibling links, are pure functions of
    ``(parent_asin, chunk_number)``; no shuffle or join against sibling
    rows is required. A PySpark UDF is used to generate deterministic chunk 
    identifiers and forward/backward sibling links.

    Returns:
        A Spark SQL UDF mapping ``(parent_asin, chunk_number,
        total_chunks)`` to ``struct<chunk_id,previous_chunk_id,next_chunk_id>``.
    """

    def _identity_for_row(parent_asin: str, chunk_number: int, total_chunks: int) -> Dict[str, Optional[str]]:
        chunk_id = generate_chunk_id(parent_asin, chunk_number)
        previous_chunk_id = generate_chunk_id(parent_asin, chunk_number - 1) if chunk_number > 0 else None
        next_chunk_id = (
            generate_chunk_id(parent_asin, chunk_number + 1) if chunk_number + 1 < total_chunks else None
        )
        return {
            "chunk_id": chunk_id,
            "previous_chunk_id": previous_chunk_id,
            "next_chunk_id": next_chunk_id,
        }

    @F.udf(_CHUNK_IDENTITY_SCHEMA)
    def _chunk_identity(parent_asin: str, chunk_number: int, total_chunks: int) -> Optional[Dict[str, Optional[str]]]:
        if parent_asin is None or chunk_number is None or total_chunks is None:
            return None
        return _identity_for_row(parent_asin, chunk_number, total_chunks)

    return _chunk_identity


class ChunkGenerator:
    """Orchestrates adaptive chunk generation over a Final Documents ``DataFrame``."""

    def __init__(self, params: AdaptiveChunkingParameters) -> None:
        """Initialize the generator.

        Args:
            params: Adaptive chunking sizing parameters.
        """
        self._params = params

    def generate(self, documents_df: DataFrame) -> DataFrame:
        """Expand each document row into its constituent chunk rows.

        Args:
            documents_df: ``DataFrame`` with the columns produced by
                ``DocumentReader.read_final_documents``.

        Returns:
            A ``DataFrame`` with one row per generated chunk, containing
            ``parent_asin``, ``category``, ``product_title``,
            ``total_chunks``, ``chunk_number``, ``chunk_text``,
            ``token_count``, and ``character_count``.
        """
        with ExecutionTimer(_LOGGER, "generate_chunks"):
            chunk_udf = _build_chunk_generation_udf(self._params)

            with_chunk_records = documents_df.withColumn(
                "_chunk_records", chunk_udf(F.col(InputColumns.DOCUMENT_TEXT))
            ).withColumn(ChunkOutputColumns.TOTAL_CHUNKS, F.size(F.col("_chunk_records")))

            non_empty_documents = with_chunk_records.filter(
                F.col(ChunkOutputColumns.TOTAL_CHUNKS) > F.lit(0)
            )

            exploded = non_empty_documents.select(
                InputColumns.PARENT_ASIN,
                InputColumns.CATEGORY,
                InputColumns.PRODUCT_TITLE,
                ChunkOutputColumns.TOTAL_CHUNKS,
                F.explode(F.col("_chunk_records")).alias("_chunk_record"),
            )

            chunk_rows = exploded.select(
                InputColumns.PARENT_ASIN,
                InputColumns.CATEGORY,
                InputColumns.PRODUCT_TITLE,
                ChunkOutputColumns.TOTAL_CHUNKS,
                F.col("_chunk_record.chunk_number").alias(ChunkOutputColumns.CHUNK_NUMBER),
                F.col("_chunk_record.chunk_text").alias(ChunkOutputColumns.CHUNK_TEXT),
                F.col("_chunk_record.token_count").alias(ChunkOutputColumns.TOKEN_COUNT),
                F.col("_chunk_record.character_count").alias(ChunkOutputColumns.CHARACTER_COUNT),
            )
        return chunk_rows

    def finalize_chunk_identity(self, chunk_rows_df: DataFrame) -> DataFrame:
        """Attach ``chunk_id``, sibling links, and ``created_timestamp`` to chunk rows.

        Args:
            chunk_rows_df: ``DataFrame`` produced by ``generate``.

        Returns:
            A ``DataFrame`` whose columns, names, and order exactly match
            ``schema.CHUNK_OUTPUT_SCHEMA``.
        """
        with ExecutionTimer(_LOGGER, "finalize_chunk_identity"):
            identity_udf = _build_chunk_identity_udf()

            with_identity = chunk_rows_df.withColumn(
                "_identity",
                identity_udf(
                    F.col(InputColumns.PARENT_ASIN),
                    F.col(ChunkOutputColumns.CHUNK_NUMBER),
                    F.col(ChunkOutputColumns.TOTAL_CHUNKS),
                ),
            )

            finalized = with_identity.select(
                F.col("_identity.chunk_id").alias(ChunkOutputColumns.CHUNK_ID),
                F.col(InputColumns.PARENT_ASIN).alias(ChunkOutputColumns.PARENT_ASIN),
                F.col(InputColumns.CATEGORY).alias(ChunkOutputColumns.CATEGORY),
                F.col(InputColumns.PRODUCT_TITLE).alias(ChunkOutputColumns.PRODUCT_TITLE),
                F.col(ChunkOutputColumns.CHUNK_NUMBER).cast(IntegerType()).alias(ChunkOutputColumns.CHUNK_NUMBER),
                F.col(ChunkOutputColumns.TOTAL_CHUNKS).cast(IntegerType()).alias(ChunkOutputColumns.TOTAL_CHUNKS),
                F.col(ChunkOutputColumns.CHUNK_TEXT).alias(ChunkOutputColumns.CHUNK_TEXT),
                F.col(ChunkOutputColumns.TOKEN_COUNT).cast(IntegerType()).alias(ChunkOutputColumns.TOKEN_COUNT),
                F.col(ChunkOutputColumns.CHARACTER_COUNT)
                .cast(IntegerType())
                .alias(ChunkOutputColumns.CHARACTER_COUNT),
                F.current_timestamp().alias(ChunkOutputColumns.CREATED_TIMESTAMP),
                F.col("_identity.previous_chunk_id").alias(ChunkOutputColumns.PREVIOUS_CHUNK_ID),
                F.col("_identity.next_chunk_id").alias(ChunkOutputColumns.NEXT_CHUNK_ID),
            )
        return finalized


# ---------------------------------------------------------------------------
# Metadata builder
# ---------------------------------------------------------------------------


class MetadataBuilder:
    """Builds pipeline- and execution-metadata records for the run manifest."""

    def __init__(self, run_id: str, master_config: MasterConfig) -> None:
        """Initialize the builder.

        Args:
            run_id: Unique identifier of the current run.
            master_config: Aggregate pipeline configuration.
        """
        self._run_id = run_id
        self._config = master_config

    def build_pipeline_metadata(self, source_record_count: int) -> Dict[str, Any]:
        """Build the pipeline/project metadata record for this run.

        Args:
            source_record_count: Number of Final Document records read as
                input.

        Returns:
            A dictionary keyed by ``schema.PipelineMetadataColumns``
            field names.
        """
        return {
            PipelineMetadataColumns.PROJECT_NAME: self._config.project.project_name,
            PipelineMetadataColumns.PIPELINE_STAGE: self._config.project.pipeline_stage,
            PipelineMetadataColumns.PRODUCT_CATEGORIES: ", ".join(self._config.project.product_categories),
            PipelineMetadataColumns.SOURCE_RECORD_COUNT: source_record_count,
        }

    def build_execution_metadata(
        self,
        started_at: datetime,
        completed_at: datetime,
        elapsed_seconds: float,
        input_record_count: int,
        output_record_count: int,
    ) -> Dict[str, Any]:
        """Build the execution metadata record for this run.

        Args:
            started_at: UTC timestamp the run began.
            completed_at: UTC timestamp the run completed.
            elapsed_seconds: Total wall-clock duration of the run.
            input_record_count: Number of Final Document records read.
            output_record_count: Number of chunk records written.

        Returns:
            A dictionary keyed by ``schema.ExecutionMetadataColumns``
            field names.
        """
        return {
            ExecutionMetadataColumns.RUN_ID: self._run_id,
            ExecutionMetadataColumns.ENVIRONMENT: self._config.runtime.environment,
            ExecutionMetadataColumns.EXECUTION_START_UTC: started_at,
            ExecutionMetadataColumns.EXECUTION_END_UTC: completed_at,
            ExecutionMetadataColumns.ELAPSED_SECONDS: int(round(elapsed_seconds)),
            ExecutionMetadataColumns.INPUT_RECORD_COUNT: input_record_count,
            ExecutionMetadataColumns.OUTPUT_RECORD_COUNT: output_record_count,
        }


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------


class OutputWriter:
    """Writes the chunk dataset and run manifest to S3."""

    def write_chunks(self, chunks_df: DataFrame, output_path: str, output_config: OutputConfig) -> None:
        """Write the finalized chunk ``DataFrame`` to partitioned Parquet.

        Repartitioning by the same column used for
        ``partitionBy`` before writing ensures each output partition's
        rows land in a single partition directory, avoiding the
        small-files-per-partition-directory problem a naive write would
        otherwise produce; the repartition's shuffle is bounded by
        ``output_config.output_partition_count`` and is a one-time cost
        paid once per run, not per row downstream.

        Args:
            chunks_df: Finalized chunk ``DataFrame`` matching
                ``schema.CHUNK_OUTPUT_SCHEMA``.
            output_path: S3 prefix to write chunk Parquet files to
                (sourced from ``config.settings.s3`` by the caller).
            output_config: Output writing settings (format, write mode,
                partition count, compression codec).

        Raises:
            ChunkGenerationPipelineError: If the write to ``output_path``
                fails.
        """
        with ExecutionTimer(_LOGGER, "write_chunks"):
            try:
                (
                    chunks_df.repartition(
                        output_config.output_partition_count, F.col(PARTITION_COLUMNS[0])
                    )
                    .write.partitionBy(*PARTITION_COLUMNS)
                    .mode(output_config.write_mode)
                    .option("compression", output_config.compression_codec)
                    .format(output_config.output_format)
                    .save(output_path)
                )
            except Exception as exc:
                raise ChunkGenerationPipelineError(
                    f"Failed to write chunk dataset to '{output_path}': {exc}"
                ) from exc
            _LOGGER.info("Chunk dataset written to '%s'.", output_path)

    def write_manifest(
        self,
        spark: SparkSession,
        run_id: str,
        pipeline_metadata: Dict[str, Any],
        execution_metadata: Dict[str, Any],
        manifest_path: str,
    ) -> None:
        """Write the run's pipeline and execution metadata as a JSON manifest.

        Args:
            spark: Active ``SparkSession``.
            run_id: Unique identifier of the current run, used to
                namespace the manifest's output location.
            pipeline_metadata: Record produced by
                ``MetadataBuilder.build_pipeline_metadata``.
            execution_metadata: Record produced by
                ``MetadataBuilder.build_execution_metadata``.
            manifest_path: S3 prefix manifests are written under
                (sourced from ``config.settings.s3`` by the caller).

        Raises:
            ChunkGenerationPipelineError: If the manifest write fails.
                This is intentionally non-fatal to the caller's data
                write (which has already succeeded by the time this is
                called), but is still surfaced as an error since a
                missing manifest breaks downstream run-tracking.
        """
        with ExecutionTimer(_LOGGER, "write_manifest"):
            destination = f"{manifest_path.rstrip('/')}/{run_id}/"
            try:
                manifest_record = {**pipeline_metadata, **execution_metadata}
                manifest_df = spark.createDataFrame([manifest_record])
                manifest_df.coalesce(1).write.mode("overwrite").json(destination)
            except Exception as exc:
                raise ChunkGenerationPipelineError(
                    f"Failed to write run manifest to '{destination}': {exc}"
                ) from exc
            _LOGGER.info("Run manifest written to '%s'.", destination)


# ---------------------------------------------------------------------------
# Execution summary
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionSummary:
    """Aggregate metrics summarizing a single pipeline run.

    Attributes:
        run_id: Unique identifier of the run.
        environment: Deployment environment the run executed in.
        input_record_count: Number of Final Document records read.
        output_record_count: Number of chunk records written.
        elapsed_seconds: Total wall-clock duration of the run.
        average_chunks_per_document: ``output_record_count /
            input_record_count``.
    """

    run_id: str
    environment: str
    input_record_count: int
    output_record_count: int
    elapsed_seconds: float
    average_chunks_per_document: float

    def log(self) -> None:
        """Emit this summary as a single structured log line."""
        _LOGGER.info(
            "EXECUTION SUMMARY | run_id=%s | environment=%s | input_records=%d | "
            "output_records=%d | avg_chunks_per_document=%.2f | elapsed_seconds=%.2f",
            self.run_id,
            self.environment,
            self.input_record_count,
            self.output_record_count,
            self.average_chunks_per_document,
            self.elapsed_seconds,
        )


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------


class ChunkGenerationPipeline:
    """End-to-end orchestrator for the Chunk Generation pipeline stage."""

    def __init__(
        self,
        chunking_parameters: AdaptiveChunkingParameters,
        master_config: MasterConfig = settings,
        s3_config: Optional[S3Config] = None,
    ) -> None:
        """Initialize the pipeline.

        Args:
            chunking_parameters: Adaptive chunking sizing parameters.
            master_config: Aggregate pipeline configuration. Defaults to
                ``config.settings``.
            s3_config: S3 locations for this run. Defaults to
                ``master_config.s3`` (equivalently
                ``config.settings.s3``) when omitted, so every path is
                sourced from ``config.py`` unless a caller (e.g. the CLI)
                explicitly supplies a per-field override.
        """
        self._chunking_parameters = chunking_parameters
        self._config = master_config
        self._s3_config = s3_config if s3_config is not None else master_config.s3

    def run(self) -> ExecutionSummary:
        """Execute the full Chunk Generation stage.

        Returns:
            An ``ExecutionSummary`` describing the completed run.

        Raises:
            ChunkGenerationPipelineError: If configuration validation
                fails, no input records are available to process, or a
                read/write against S3 fails.
            SchemaValidationError: If the input or output schema is
                incompatible with the declared expectations.
        """
        run_id = generate_uuid4()
        stopwatch = Stopwatch().start()
        started_at = datetime.utcnow()
        spark: Optional[SparkSession] = None

        _LOGGER.info("APPLICATION START | run_id=%s | stage=%s", run_id, self._config.project.pipeline_stage)

        try:
            ConfigurationValidator.validate_all(
                self._config.chunk, self._chunking_parameters, self._s3_config
            )

            spark = SparkSessionFactory.create_spark_session(self._config.spark, self._config.output)
            suppress_verbose_third_party_logging()
            _LOGGER.info("Spark session initialized | app_name=%s", self._config.spark.app_name)

            reader = DocumentReader(spark)
            documents_df = reader.read_final_documents(self._s3_config.final_documents_input_path)
            documents_df = reader.filter_valid_documents(documents_df)

            with ExecutionTimer(_LOGGER, "count_input_records"):
                input_record_count = documents_df.count()
            _LOGGER.info("Input validated | input_record_count=%d", input_record_count)

            if input_record_count == 0:
                raise ChunkGenerationPipelineError(
                    "No valid Final Document records found at "
                    f"'{self._s3_config.final_documents_input_path}'."
                )

            generator = ChunkGenerator(self._chunking_parameters)
            chunk_rows_df = generator.generate(documents_df)
            finalized_df = generator.finalize_chunk_identity(chunk_rows_df)
            finalized_df = finalized_df.select(*[struct_field.name for struct_field in CHUNK_OUTPUT_SCHEMA.fields])

            output_validation_result = SchemaValidator.validate_output_schema(finalized_df.schema)
            if not output_validation_result.is_valid:
                raise SchemaValidationError(
                    "Chunk output schema is incompatible: "
                    f"missing={output_validation_result.missing_columns}, "
                    f"unexpected={output_validation_result.unexpected_columns}, "
                    f"datatype_mismatches={output_validation_result.datatype_mismatches}."
                )
            _LOGGER.info("Chunk output schema validated successfully.")

            # Persisted once so the row count and the write both reuse a
            # single materialization of the (non-trivial) chunking
            # computation, rather than recomputing it twice.
            finalized_df = finalized_df.persist(StorageLevel.MEMORY_AND_DISK)
            try:
                with ExecutionTimer(_LOGGER, "count_output_records"):
                    output_record_count = finalized_df.count()

                writer = OutputWriter()
                writer.write_chunks(finalized_df, self._s3_config.chunk_output_path, self._config.output)
            finally:
                finalized_df.unpersist()

            completed_at = datetime.utcnow()
            elapsed_seconds = stopwatch.stop()

            metadata_builder = MetadataBuilder(run_id, self._config)
            pipeline_metadata = metadata_builder.build_pipeline_metadata(input_record_count)
            execution_metadata = metadata_builder.build_execution_metadata(
                started_at, completed_at, elapsed_seconds, input_record_count, output_record_count
            )
            writer.write_manifest(
                spark, run_id, pipeline_metadata, execution_metadata, self._s3_config.manifest_output_path
            )

            summary = ExecutionSummary(
                run_id=run_id,
                environment=self._config.runtime.environment,
                input_record_count=input_record_count,
                output_record_count=output_record_count,
                elapsed_seconds=elapsed_seconds,
                average_chunks_per_document=output_record_count / input_record_count,
            )
            summary.log()
            _LOGGER.info("APPLICATION COMPLETE | run_id=%s", run_id)
            return summary

        except Exception:
            _LOGGER.error("APPLICATION FAILED | run_id=%s", run_id, exc_info=True)
            raise
        finally:
            if spark is not None:
                spark.stop()
                _LOGGER.info("Spark session stopped | run_id=%s", run_id)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for a ``spark-submit`` invocation.

    Every argument is optional and defaults to the project's
    authoritative S3 layout declared in ``config.settings.s3``.

    Args:
        argv: Argument vector to parse. Defaults to ``sys.argv[1:]``.

    Returns:
        The parsed ``argparse.Namespace``.
    """
    default_s3 = settings.s3
    parser = argparse.ArgumentParser(description="Hybrid RAG Chunk Generation stage.")
    parser.add_argument("--input-path", default=default_s3.final_documents_input_path)
    parser.add_argument("--output-path", default=default_s3.chunk_output_path)
    parser.add_argument("--validation-path", default=default_s3.chunk_validation_path)
    parser.add_argument("--manifest-path", default=default_s3.manifest_output_path)
    return parser.parse_args(argv)


def _resolve_s3_config(arguments: argparse.Namespace) -> S3Config:
    """Build the S3 configuration for this run from ``config.settings.s3`` and CLI overrides.

    ``config.settings.s3`` is always the base; only fields explicitly
    overridden on the command line are replaced, via
    ``dataclasses.replace``, which re-runs ``S3Config.__post_init__`` and
    therefore re-validates the resulting configuration as a whole.

    Args:
        arguments: Parsed CLI arguments from ``_parse_arguments``.

    Returns:
        The resolved ``S3Config`` for this run.
    """
    return replace(
        settings.s3,
        final_documents_input_path=arguments.input_path,
        chunk_output_path=arguments.output_path,
        chunk_validation_path=arguments.validation_path,
        manifest_output_path=arguments.manifest_path,
    )


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for ``spark-submit 01_generate_chunks.py``.

    Args:
        argv: Argument vector to parse. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code: ``0`` on success, ``1`` on failure.
    """
    arguments = _parse_arguments(argv)

    try:
        s3_config = _resolve_s3_config(arguments)
    except ValueError as exc:
        _LOGGER.error("Invalid S3 configuration for this run: %s", exc)
        return 1

    chunking_parameters = AdaptiveChunkingParameters()
    pipeline = ChunkGenerationPipeline(chunking_parameters=chunking_parameters, s3_config=s3_config)

    try:
        pipeline.run()
    except Exception:  # noqa: BLE001 - top-level guard for a clean process exit code
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())