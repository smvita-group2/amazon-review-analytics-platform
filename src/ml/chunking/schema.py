#!/usr/bin/env python3
"""Schema definitions for the Hybrid RAG Intelligent Product Search pipeline.

This module defines every Spark schema, column-name constant, column
group, and schema-validation utility consumed by the current pipeline
stage, ``06_Text_Chunking`` (Chunk Generation), and by the downstream
``Chunk Validation`` stage.

This module is schema-definition-only. It contains no ``SparkSession``
creation, no Spark jobs, no DataFrame transformations, no chunk
generation logic, no logging implementation, no S3 operations, and no
file reading or writing. It imports and composes ``config.py``,
``logger.py``, and ``utils.py`` without modifying any of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from pyspark.sql.types import (
    DataType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from config import ChunkConfig, ProjectConfig, ValidationConfig, settings
from logger import get_logger
from utils import validate_non_empty_string

_LOGGER = get_logger(__name__, settings.logging)


# ---------------------------------------------------------------------------
# Column constants
# ---------------------------------------------------------------------------


class InputColumns:
    """Column names for the Final Documents dataset (this stage's input).

    Attributes:
        PARENT_ASIN: Product identifier the document belongs to.
        CATEGORY: Product category the document belongs to.
        PRODUCT_TITLE: Human-readable product title.
        DOCUMENT_TEXT: Final, validated document body to be chunked.
    """

    PARENT_ASIN: str = "parent_asin"
    CATEGORY: str = "category"
    PRODUCT_TITLE: str = "product_title"
    DOCUMENT_TEXT: str = "document"


class ChunkOutputColumns:
    """Column names for the Chunk Generation stage's output dataset.

    Attributes:
        CHUNK_ID: Deterministic chunk identifier (see
            ``utils.generate_chunk_id``).
        PARENT_ASIN: Product identifier the chunk was derived from.
        CATEGORY: Product category the chunk was derived from.
        PRODUCT_TITLE: Human-readable product title of the source
            document.
        CHUNK_NUMBER: Zero-based position of this chunk within its source
            document.
        TOTAL_CHUNKS: Total number of chunks generated from the source
            document.
        CHUNK_TEXT: The generated chunk's text content.
        TOKEN_COUNT: Estimated token count of ``CHUNK_TEXT`` (see
            ``utils.estimate_token_count``).
        CHARACTER_COUNT: Character length of ``CHUNK_TEXT``.
        CREATED_TIMESTAMP: UTC timestamp the chunk record was produced.
        PREVIOUS_CHUNK_ID: Identifier of the preceding sibling chunk, or
            ``None`` for the first chunk of a document.
        NEXT_CHUNK_ID: Identifier of the following sibling chunk, or
            ``None`` for the last chunk of a document.
    """

    CHUNK_ID: str = "chunk_id"
    PARENT_ASIN: str = "parent_asin"
    CATEGORY: str = "category"
    PRODUCT_TITLE: str = "product_title"
    CHUNK_NUMBER: str = "chunk_number"
    TOTAL_CHUNKS: str = "total_chunks"
    CHUNK_TEXT: str = "chunk_text"
    TOKEN_COUNT: str = "token_count"
    CHARACTER_COUNT: str = "character_count"
    CREATED_TIMESTAMP: str = "created_timestamp"
    PREVIOUS_CHUNK_ID: str = "previous_chunk_id"
    NEXT_CHUNK_ID: str = "next_chunk_id"


class PipelineMetadataColumns:
    """Column names describing pipeline/project identity in a metadata record.

    Attributes:
        PROJECT_NAME: Human-readable name of the overall project.
        PIPELINE_STAGE: Identifier of the currently executing pipeline
            stage.
        PRODUCT_CATEGORIES: Product categories covered by the dataset.
        SOURCE_RECORD_COUNT: Number of Final Document records consumed as
            input to the stage.
    """

    PROJECT_NAME: str = "project_name"
    PIPELINE_STAGE: str = "pipeline_stage"
    PRODUCT_CATEGORIES: str = "product_categories"
    SOURCE_RECORD_COUNT: str = "source_record_count"


class ExecutionMetadataColumns:
    """Column names describing a single pipeline run in a metadata record.

    Attributes:
        RUN_ID: Unique identifier of the executing run (see
            ``utils.generate_uuid4``).
        ENVIRONMENT: Deployment environment the run executed in.
        EXECUTION_START_UTC: UTC timestamp the run began.
        EXECUTION_END_UTC: UTC timestamp the run completed.
        ELAPSED_SECONDS: Total wall-clock duration of the run, in seconds.
        INPUT_RECORD_COUNT: Number of records read by the run.
        OUTPUT_RECORD_COUNT: Number of records written by the run.
    """

    RUN_ID: str = "run_id"
    ENVIRONMENT: str = "environment"
    EXECUTION_START_UTC: str = "execution_start_utc"
    EXECUTION_END_UTC: str = "execution_end_utc"
    ELAPSED_SECONDS: str = "elapsed_seconds"
    INPUT_RECORD_COUNT: str = "input_record_count"
    OUTPUT_RECORD_COUNT: str = "output_record_count"


class ValidationMetadataColumns:
    """Column names describing chunk-validation results in a metadata record.

    Attributes:
        TOTAL_RECORDS: Total number of chunk records evaluated.
        PASSED_RECORDS: Number of chunk records that passed validation.
        FAILED_RECORDS: Number of chunk records that failed validation.
        FAILURE_RATE: ``FAILED_RECORDS / TOTAL_RECORDS``.
        MAX_ALLOWED_FAILURE_RATE: Configured threshold ``FAILURE_RATE``
            must not exceed for the stage to be considered passed.
        VALIDATION_PASSED: Whether the stage as a whole passed validation.
        VALIDATED_AT_UTC: UTC timestamp validation was performed.
    """

    TOTAL_RECORDS: str = "total_records"
    PASSED_RECORDS: str = "passed_records"
    FAILED_RECORDS: str = "failed_records"
    FAILURE_RATE: str = "failure_rate"
    MAX_ALLOWED_FAILURE_RATE: str = "max_allowed_failure_rate"
    VALIDATION_PASSED: str = "validation_passed"
    VALIDATED_AT_UTC: str = "validated_at_utc"


class ColumnConstants:
    """Centralized, single-source-of-truth registry of every column name.

    Every column name used anywhere in the Chunk Generation stage must be
    referenced through this class (or its nested member classes) rather
    than hardcoded as a string literal, so a column rename is a one-line
    change made in exactly one place.

    Attributes:
        Input: Column names for the Final Documents input dataset.
        ChunkOutput: Column names for the chunk output dataset.
        PipelineMetadata: Column names for pipeline/project metadata.
        ExecutionMetadata: Column names for run-execution metadata.
        ValidationMetadata: Column names for chunk-validation metadata.
    """

    Input = InputColumns
    ChunkOutput = ChunkOutputColumns
    PipelineMetadata = PipelineMetadataColumns
    ExecutionMetadata = ExecutionMetadataColumns
    ValidationMetadata = ValidationMetadataColumns


# ---------------------------------------------------------------------------
# Input schema (Final Documents)
# ---------------------------------------------------------------------------


def build_final_document_schema() -> StructType:
    """Build the explicit schema of the Final Documents dataset.

    This is the validated output of the upstream ``05_Final_Documents``
    stage and the sole input to Chunk Generation. Schema inference is
    deliberately never relied upon; every field and its nullability is
    declared explicitly so a malformed or drifted upstream file fails
    fast with a clear schema-mismatch error rather than silently
    producing ``null``-typed columns.

    Returns:
        The ``StructType`` describing the Final Documents dataset.
    """
    return StructType(
        [
            StructField(InputColumns.PARENT_ASIN, StringType(), nullable=True),
            StructField(InputColumns.CATEGORY, StringType(), nullable=True),
            StructField(InputColumns.PRODUCT_TITLE, StringType(), nullable=True),
            StructField(InputColumns.DOCUMENT_TEXT, StringType(), nullable=True),
        ]
    )


FINAL_DOCUMENT_SCHEMA: StructType = build_final_document_schema()


# ---------------------------------------------------------------------------
# Chunk output schema
# ---------------------------------------------------------------------------


def build_chunk_output_schema() -> StructType:
    """Build the explicit schema of the Chunk Generation stage's output dataset.

    Written to Parquet under ``config.S3Config.chunks_output_prefix``
    (partitioned by ``PARTITION_COLUMNS``); consumed downstream by Chunk
    Validation and Embedding Generation.

    Returns:
        The ``StructType`` describing the chunk output dataset.
    """
    return StructType(
        [
            StructField(ChunkOutputColumns.CHUNK_ID, StringType(), nullable=False),
            StructField(ChunkOutputColumns.PARENT_ASIN, StringType(), nullable=False),
            StructField(ChunkOutputColumns.CATEGORY, StringType(), nullable=False),
            StructField(ChunkOutputColumns.PRODUCT_TITLE, StringType(), nullable=False),
            StructField(ChunkOutputColumns.CHUNK_NUMBER, IntegerType(), nullable=False),
            StructField(ChunkOutputColumns.TOTAL_CHUNKS, IntegerType(), nullable=False),
            StructField(ChunkOutputColumns.CHUNK_TEXT, StringType(), nullable=False),
            StructField(ChunkOutputColumns.TOKEN_COUNT, IntegerType(), nullable=False),
            StructField(ChunkOutputColumns.CHARACTER_COUNT, IntegerType(), nullable=False),
            StructField(ChunkOutputColumns.CREATED_TIMESTAMP, TimestampType(), nullable=False),
            StructField(ChunkOutputColumns.PREVIOUS_CHUNK_ID, StringType(), nullable=True),
            StructField(ChunkOutputColumns.NEXT_CHUNK_ID, StringType(), nullable=True),
        ]
    )


CHUNK_OUTPUT_SCHEMA: StructType = build_chunk_output_schema()


# ---------------------------------------------------------------------------
# Metadata schemas
# ---------------------------------------------------------------------------


def build_pipeline_metadata_schema() -> StructType:
    """Build the explicit schema of a pipeline/project metadata record.

    Returns:
        The ``StructType`` describing pipeline/project identity fields
        recorded once per run.
    """
    return StructType(
        [
            StructField(PipelineMetadataColumns.PROJECT_NAME, StringType(), nullable=False),
            StructField(PipelineMetadataColumns.PIPELINE_STAGE, StringType(), nullable=False),
            StructField(
                PipelineMetadataColumns.PRODUCT_CATEGORIES,
                StringType(),
                nullable=False,
            ),
            StructField(
                PipelineMetadataColumns.SOURCE_RECORD_COUNT,
                IntegerType(),
                nullable=False,
            ),
        ]
    )


def build_execution_metadata_schema() -> StructType:
    """Build the explicit schema of a run-execution metadata record.

    Returns:
        The ``StructType`` describing per-run execution fields, intended
        for the run manifest written under
        ``config.S3Config.manifest_prefix``.
    """
    return StructType(
        [
            StructField(ExecutionMetadataColumns.RUN_ID, StringType(), nullable=False),
            StructField(ExecutionMetadataColumns.ENVIRONMENT, StringType(), nullable=False),
            StructField(
                ExecutionMetadataColumns.EXECUTION_START_UTC,
                TimestampType(),
                nullable=False,
            ),
            StructField(
                ExecutionMetadataColumns.EXECUTION_END_UTC,
                TimestampType(),
                nullable=True,
            ),
            StructField(
                ExecutionMetadataColumns.ELAPSED_SECONDS,
                IntegerType(),
                nullable=True,
            ),
            StructField(
                ExecutionMetadataColumns.INPUT_RECORD_COUNT,
                IntegerType(),
                nullable=True,
            ),
            StructField(
                ExecutionMetadataColumns.OUTPUT_RECORD_COUNT,
                IntegerType(),
                nullable=True,
            ),
        ]
    )


def build_validation_metadata_schema() -> StructType:
    """Build the explicit schema of a chunk-validation metadata record.

    Returns:
        The ``StructType`` describing chunk-validation summary fields,
        intended for the Chunk Validation stage's manifest output.
    """
    return StructType(
        [
            StructField(ValidationMetadataColumns.TOTAL_RECORDS, IntegerType(), nullable=False),
            StructField(ValidationMetadataColumns.PASSED_RECORDS, IntegerType(), nullable=False),
            StructField(ValidationMetadataColumns.FAILED_RECORDS, IntegerType(), nullable=False),
            StructField(ValidationMetadataColumns.FAILURE_RATE, StringType(), nullable=False),
            StructField(
                ValidationMetadataColumns.MAX_ALLOWED_FAILURE_RATE,
                StringType(),
                nullable=False,
            ),
            StructField(
                ValidationMetadataColumns.VALIDATION_PASSED,
                StringType(),
                nullable=False,
            ),
            StructField(
                ValidationMetadataColumns.VALIDATED_AT_UTC,
                TimestampType(),
                nullable=False,
            ),
        ]
    )


PIPELINE_METADATA_SCHEMA: StructType = build_pipeline_metadata_schema()
EXECUTION_METADATA_SCHEMA: StructType = build_execution_metadata_schema()
VALIDATION_METADATA_SCHEMA: StructType = build_validation_metadata_schema()


# ---------------------------------------------------------------------------
# Reusable column groups
# ---------------------------------------------------------------------------


def _column_names(schema: StructType) -> Tuple[str, ...]:
    """Return the ordered column names declared by ``schema``.

    Args:
        schema: Schema to read column names from.

    Returns:
        A tuple of column names in declaration order.
    """
    return tuple(struct_field.name for struct_field in schema.fields)


def _required_column_names(schema: StructType) -> Tuple[str, ...]:
    """Return the non-nullable column names declared by ``schema``.

    Args:
        schema: Schema to read nullability from.

    Returns:
        A tuple of column names whose ``nullable`` flag is ``False``, in
        declaration order.
    """
    return tuple(
        struct_field.name for struct_field in schema.fields if not struct_field.nullable
    )


def _nullable_column_names(schema: StructType) -> Tuple[str, ...]:
    """Return the nullable column names declared by ``schema``.

    Args:
        schema: Schema to read nullability from.

    Returns:
        A tuple of column names whose ``nullable`` flag is ``True``, in
        declaration order.
    """
    return tuple(struct_field.name for struct_field in schema.fields if struct_field.nullable)


INPUT_COLUMNS: Tuple[str, ...] = _column_names(FINAL_DOCUMENT_SCHEMA)
OUTPUT_COLUMNS: Tuple[str, ...] = _column_names(CHUNK_OUTPUT_SCHEMA)
METADATA_COLUMNS: Tuple[str, ...] = (
    _column_names(PIPELINE_METADATA_SCHEMA)
    + _column_names(EXECUTION_METADATA_SCHEMA)
    + _column_names(VALIDATION_METADATA_SCHEMA)
)
REQUIRED_COLUMNS: Tuple[str, ...] = _required_column_names(CHUNK_OUTPUT_SCHEMA)
NULLABLE_COLUMNS: Tuple[str, ...] = _nullable_column_names(CHUNK_OUTPUT_SCHEMA)
PARTITION_COLUMNS: Tuple[str, ...] = (ChunkOutputColumns.CATEGORY,)


# ---------------------------------------------------------------------------
# Schema validation result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SchemaValidationResult:
    """Outcome of validating an actual schema against an expected schema.

    Attributes:
        is_valid: Whether the actual schema satisfies every check that was
            performed.
        missing_columns: Expected columns absent from the actual schema.
        unexpected_columns: Actual columns absent from the expected
            schema.
        datatype_mismatches: Column names present in both schemas whose
            declared ``DataType`` differs, mapped to a human-readable
            ``"actual -> expected"`` description.
        nullability_mismatches: Column names present in both schemas whose
            declared ``nullable`` flag differs, mapped to a human-readable
            ``"actual -> expected"`` description.
    """

    is_valid: bool
    missing_columns: Tuple[str, ...] = field(default_factory=tuple)
    unexpected_columns: Tuple[str, ...] = field(default_factory=tuple)
    datatype_mismatches: Tuple[str, ...] = field(default_factory=tuple)
    nullability_mismatches: Tuple[str, ...] = field(default_factory=tuple)


class SchemaValidationError(ValueError):
    """Raised when an actual schema fails a required validation check."""


# ---------------------------------------------------------------------------
# Schema validation utilities
# ---------------------------------------------------------------------------


class SchemaValidator:
    """Reusable, stateless schema-validation utilities.

    Every method is a pure function of its arguments (no Spark session,
    no I/O); callers pass in a ``StructType`` obtained from
    ``DataFrame.schema`` and receive back either a boolean/result object
    or a raised ``SchemaValidationError``.
    """

    @staticmethod
    def find_missing_columns(
        actual_columns: Sequence[str], expected_columns: Sequence[str]
    ) -> Tuple[str, ...]:
        """Return the expected columns absent from ``actual_columns``.

        Args:
            actual_columns: Column names present in the schema being
                checked.
            expected_columns: Column names the schema is required to
                contain.

        Returns:
            A tuple of missing column names, in ``expected_columns``
            order.
        """
        actual_set = set(actual_columns)
        return tuple(column for column in expected_columns if column not in actual_set)

    @staticmethod
    def find_unexpected_columns(
        actual_columns: Sequence[str], expected_columns: Sequence[str]
    ) -> Tuple[str, ...]:
        """Return the actual columns absent from ``expected_columns``.

        Args:
            actual_columns: Column names present in the schema being
                checked.
            expected_columns: Column names the schema is allowed to
                contain.

        Returns:
            A tuple of unexpected column names, in ``actual_columns``
            order.
        """
        expected_set = set(expected_columns)
        return tuple(column for column in actual_columns if column not in expected_set)

    @staticmethod
    def validate_required_columns(
        schema: StructType, required_columns: Sequence[str]
    ) -> None:
        """Ensure every column in ``required_columns`` is present in ``schema``.

        Args:
            schema: Schema to check.
            required_columns: Column names that must be present.

        Raises:
            SchemaValidationError: If any required column is missing.
        """
        missing_columns = SchemaValidator.find_missing_columns(
            _column_names(schema), required_columns
        )
        if missing_columns:
            message = f"Schema is missing required column(s): {', '.join(missing_columns)}."
            _LOGGER.error(message)
            raise SchemaValidationError(message)

    @staticmethod
    def validate_no_unexpected_columns(
        schema: StructType, expected_columns: Sequence[str]
    ) -> None:
        """Ensure ``schema`` contains no columns outside ``expected_columns``.

        Args:
            schema: Schema to check.
            expected_columns: Column names ``schema`` is allowed to
                contain.

        Raises:
            SchemaValidationError: If ``schema`` contains any column not
                present in ``expected_columns``.
        """
        unexpected_columns = SchemaValidator.find_unexpected_columns(
            _column_names(schema), expected_columns
        )
        if unexpected_columns:
            message = (
                f"Schema contains unexpected column(s): {', '.join(unexpected_columns)}."
            )
            _LOGGER.error(message)
            raise SchemaValidationError(message)

    @staticmethod
    def validate_datatypes(schema: StructType, expected_schema: StructType) -> None:
        """Ensure columns shared by ``schema`` and ``expected_schema`` share the same ``DataType``.

        Columns present in only one of the two schemas are ignored by this
        check; use ``validate_required_columns``/
        ``validate_no_unexpected_columns`` to enforce column presence.

        Args:
            schema: Schema to check.
            expected_schema: Schema declaring the expected ``DataType`` of
                each column.

        Raises:
            SchemaValidationError: If any shared column's ``DataType``
                differs between the two schemas.
        """
        expected_types: Dict[str, DataType] = {
            struct_field.name: struct_field.dataType for struct_field in expected_schema.fields
        }
        mismatches: List[str] = []
        for struct_field in schema.fields:
            expected_type = expected_types.get(struct_field.name)
            if expected_type is not None and struct_field.dataType != expected_type:
                mismatches.append(
                    f"{struct_field.name}: {struct_field.dataType} -> {expected_type}"
                )
        if mismatches:
            message = f"Schema has datatype mismatch(es): {'; '.join(mismatches)}."
            _LOGGER.error(message)
            raise SchemaValidationError(message)

    @staticmethod
    def validate_nullability(schema: StructType, expected_schema: StructType) -> None:
        """Ensure columns shared by ``schema`` and ``expected_schema`` share the same ``nullable`` flag.

        A column that is nullable in ``schema`` but declared non-nullable
        in ``expected_schema`` is treated as a violation, since a
        downstream consumer relying on the expected schema's non-null
        guarantee could otherwise encounter unexpected ``null`` values.

        Args:
            schema: Schema to check.
            expected_schema: Schema declaring the expected ``nullable``
                flag of each column.

        Raises:
            SchemaValidationError: If any shared column's ``nullable``
                flag is more permissive in ``schema`` than in
                ``expected_schema``.
        """
        expected_nullability: Dict[str, bool] = {
            struct_field.name: struct_field.nullable for struct_field in expected_schema.fields
        }
        mismatches: List[str] = []
        for struct_field in schema.fields:
            expected_nullable = expected_nullability.get(struct_field.name)
            if (
                expected_nullable is not None
                and expected_nullable is False
                and struct_field.nullable is True
            ):
                mismatches.append(
                    f"{struct_field.name}: nullable=True -> nullable=False"
                )
        if mismatches:
            message = f"Schema has nullability mismatch(es): {'; '.join(mismatches)}."
            _LOGGER.error(message)
            raise SchemaValidationError(message)

    @staticmethod
    def validate_schema_compatibility(
        schema: StructType,
        expected_schema: StructType,
        allow_unexpected_columns: bool = False,
    ) -> SchemaValidationResult:
        """Run every schema check and return a single aggregated result.

        Unlike the individual ``validate_*`` methods, this method never
        raises for a failed check; it collects every violation into the
        returned ``SchemaValidationResult`` so a caller (e.g. the Chunk
        Validation stage) can log or persist a complete picture of a
        schema mismatch in one pass.

        Args:
            schema: Schema to check.
            expected_schema: Schema to check ``schema`` against.
            allow_unexpected_columns: When ``False`` (default), columns in
                ``schema`` that are absent from ``expected_schema`` are
                recorded as violations. When ``True``, such columns are
                ignored, which is useful when ``schema`` is permitted to
                carry extra, pipeline-stage-specific columns.

        Returns:
            A ``SchemaValidationResult`` summarizing every check.
        """
        actual_columns = _column_names(schema)
        expected_columns = _column_names(expected_schema)

        missing_columns = SchemaValidator.find_missing_columns(actual_columns, expected_columns)
        unexpected_columns = (
            ()
            if allow_unexpected_columns
            else SchemaValidator.find_unexpected_columns(actual_columns, expected_columns)
        )

        expected_types: Dict[str, DataType] = {
            struct_field.name: struct_field.dataType for struct_field in expected_schema.fields
        }

        datatype_mismatches: List[str] = []
        nullability_mismatches: List[str] = []
        
        for struct_field in schema.fields:
            expected_type = expected_types.get(struct_field.name)
            if expected_type is not None and struct_field.dataType != expected_type:
                datatype_mismatches.append(
                    f"{struct_field.name}: {struct_field.dataType} -> {expected_type}"
                )

        is_valid = not (
            missing_columns or unexpected_columns or datatype_mismatches
        )

        if not is_valid:
            _LOGGER.warning(
                "Schema compatibility check failed | missing=%s | unexpected=%s | "
                "datatype_mismatches=%s | nullability_mismatches=%s",
                missing_columns,
                unexpected_columns,
                datatype_mismatches,
                nullability_mismatches,
            )

        return SchemaValidationResult(
            is_valid=is_valid,
            missing_columns=missing_columns,
            unexpected_columns=unexpected_columns,
            datatype_mismatches=tuple(datatype_mismatches),
            nullability_mismatches=tuple(nullability_mismatches),
        )

    @staticmethod
    def validate_input_schema(schema: StructType) -> SchemaValidationResult:
        """Validate ``schema`` against ``FINAL_DOCUMENT_SCHEMA``.

        Args:
            schema: Schema of an incoming Final Documents DataFrame.

        Returns:
            A ``SchemaValidationResult`` describing compatibility with the
            expected Final Documents schema.
        """
        return SchemaValidator.validate_schema_compatibility(schema, FINAL_DOCUMENT_SCHEMA)

    @staticmethod
    def validate_output_schema(schema: StructType) -> SchemaValidationResult:
        """Validate ``schema`` against ``CHUNK_OUTPUT_SCHEMA``.

        Args:
            schema: Schema of an outgoing chunk DataFrame, checked before
                it is written to ``config.S3Config.chunks_output_prefix``.

        Returns:
            A ``SchemaValidationResult`` describing compatibility with the
            expected chunk output schema.
        """
        return SchemaValidator.validate_schema_compatibility(schema, CHUNK_OUTPUT_SCHEMA)


# ---------------------------------------------------------------------------
# Configuration-derived validation context
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChunkSchemaContext:
    """Bundles chunk-shape configuration relevant to schema-level validation.

    Composes values already declared in ``config.ChunkConfig`` and
    ``config.ValidationConfig`` (rather than redeclaring them) so callers
    that need chunk-length or failure-rate thresholds alongside the
    chunk output schema have a single, config-driven object to depend on.

    Attributes:
        project_name: Human-readable name of the overall project.
        min_chunk_chars: Minimum acceptable chunk length, in characters.
        max_chunk_chars: Maximum acceptable chunk length, in characters.
        chars_per_token: Assumed average characters per token.
        max_allowed_failure_rate: Maximum fraction of chunks permitted to
            fail validation before the stage itself is considered failed.
    """

    project_name: str
    min_chunk_chars: int
    max_chunk_chars: int
    chars_per_token: float
    max_allowed_failure_rate: float

    @classmethod
    def from_config(
        cls,
        project: ProjectConfig = settings.project,
        chunk: ChunkConfig = settings.chunk,
        validation: ValidationConfig = settings.validation,
    ) -> "ChunkSchemaContext":
        """Build a ``ChunkSchemaContext`` from the module-level ``settings``.

        Args:
            project: Project configuration to source ``project_name``
                from. Defaults to ``settings.project``.
            chunk: Chunk configuration to source chunk-length and
                token-estimation values from. Defaults to
                ``settings.chunk``.
            validation: Validation configuration to source
                ``max_allowed_failure_rate`` from. Defaults to
                ``settings.validation``.

        Returns:
            A populated ``ChunkSchemaContext``.
        """
        return cls(
            project_name=validate_non_empty_string(project.project_name, "project_name"),
            min_chunk_chars=chunk.min_chunk_chars,
            max_chunk_chars=chunk.max_chunk_chars,
            chars_per_token=chunk.chars_per_token,
            max_allowed_failure_rate=validation.max_allowed_failure_rate,
        )


DEFAULT_CHUNK_SCHEMA_CONTEXT: ChunkSchemaContext = ChunkSchemaContext.from_config()