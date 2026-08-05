#!/usr/bin/env python3
"""Enterprise utility functions for the Hybrid RAG Intelligent Product Search pipeline.

This module contains only generic, reusable helper functions: string
normalization and cleaning, approximate token/character counting,
deterministic ID and hash generation, timestamp helpers, input/output
validation, S3 path validation, data-quality checks, and execution timing.

This module performs no Spark operations and contains no
pipeline-stage-specific business logic (e.g. no semantic chunking
algorithm lives here); every function operates on plain Python values and
is safe to unit test outside of any Spark context.
"""

from __future__ import annotations

import hashlib
import re
import time
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# String cleaning and normalization
# ---------------------------------------------------------------------------

# Compiled once at module load time and reused across every call, since
# these patterns are applied per-row at production data volumes and
# recompiling a regex per invocation would be a meaningful, avoidable cost.
_WHITESPACE_RUN_PATTERN = re.compile(r"\s+")
_INTRA_LINE_WHITESPACE_PATTERN = re.compile(r"[ \t]+")
_MULTIPLE_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")
_CONTROL_CHARACTER_PATTERN = re.compile(
    "".join(
        chr(codepoint)
        for codepoint in range(0x00, 0x20)
        if chr(codepoint) not in ("\t", "\n")
    ).join(["[", "]"])
)


def clean_text(raw_text: Optional[str]) -> str:
    """Safely clean raw text for downstream processing.

    Handles ``None`` and non-string input defensively (returning an empty
    string rather than raising), strips non-printable ASCII control
    characters (other than tab and newline, which carry structural
    meaning for paragraph/line detection), and trims leading/trailing
    whitespace.

    Args:
        raw_text: Arbitrary input that is expected to be text but may be
            ``None`` or of an unexpected type due to upstream data-quality
            issues.

    Returns:
        A cleaned string; ``""`` if ``raw_text`` is ``None``, empty, or not
        a string.
    """
    if not isinstance(raw_text, str) or not raw_text:
        return ""
    return _CONTROL_CHARACTER_PATTERN.sub("", raw_text).strip()


def normalize_whitespace(text: str) -> str:
    """Collapse every run of whitespace (including newlines) into a single space.

    Intended for finalizing a chunk's display text, where internal line
    breaks from the source document should not leak into a single
    semantic unit of retrievable text.

    Args:
        text: Text to normalize.

    Returns:
        ``text`` with all whitespace runs collapsed to a single space and
        leading/trailing whitespace removed.
    """
    return _WHITESPACE_RUN_PATTERN.sub(" ", text).strip()


def normalize_paragraph_structure(text: str) -> str:
    """Normalize line endings and intra-line spacing while preserving paragraph breaks.

    Converts ``\\r\\n``/``\\r`` to ``\\n``, collapses runs of horizontal
    whitespace (spaces/tabs) within a line to a single space, and
    collapses three or more consecutive newlines down to exactly two
    (a single blank line), so paragraph-boundary detection later in the
    pipeline operates on a consistent ``\\n\\n`` separator without being
    confused by irregular source formatting.

    Args:
        text: Text to normalize.

    Returns:
        Text with normalized line endings and paragraph spacing.
    """
    unix_line_endings = text.replace("\r\n", "\n").replace("\r", "\n")
    collapsed_intra_line = _INTRA_LINE_WHITESPACE_PATTERN.sub(" ", unix_line_endings)
    collapsed_blank_lines = _MULTIPLE_BLANK_LINES_PATTERN.sub("\n\n", collapsed_intra_line)
    return collapsed_blank_lines.strip()


def normalize_text(raw_text: Optional[str]) -> str:
    """Apply full text normalization: safe cleaning plus Unicode canonicalization.

    Composes ``clean_text`` with Unicode NFKC normalization, which
    canonicalizes visually-equivalent character sequences (e.g. combining
    characters, full-width variants) into a consistent representation.
    This is the entry-point normalizer that should be applied once to raw
    source text before any further processing.

    Args:
        raw_text: Arbitrary input that is expected to be text but may be
            ``None`` or malformed.

    Returns:
        A fully normalized string; ``""`` for ``None``/empty/non-string
        input.
    """
    cleaned = clean_text(raw_text)
    if not cleaned:
        return ""
    return unicodedata.normalize("NFKC", cleaned)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to at most ``max_length`` characters, appending ``suffix`` if cut.

    Primarily useful for safely including a preview of long text in log
    messages without flooding logs with entire document bodies.

    Args:
        text: Text to truncate.
        max_length: Maximum number of characters to retain, including the
            suffix.
        suffix: String appended to indicate truncation occurred.

    Returns:
        ``text`` unchanged if it already fits within ``max_length``,
        otherwise a truncated string of exactly ``max_length`` characters.

    Raises:
        ValueError: If ``max_length`` is smaller than ``len(suffix)``,
            since no meaningful truncation is possible in that case.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be at least as long as suffix ({len(suffix)})."
        )
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


# ---------------------------------------------------------------------------
# Token and character counting
# ---------------------------------------------------------------------------


def count_characters(text: Optional[str]) -> int:
    """Return the character length of ``text``, treating ``None`` as zero length.

    Args:
        text: Text to measure.

    Returns:
        ``len(text)``, or ``0`` if ``text`` is ``None``.
    """
    return len(text) if text else 0


def estimate_token_count(text: Optional[str], chars_per_token: float = 4.0) -> int:
    """Estimate a token count for ``text`` without invoking a real tokenizer.

    Uses a fixed characters-per-token heuristic, which is sufficient for
    chunk-sizing decisions (this pipeline stage does not need exact token
    counts, only a consistent, cheap proxy for them) while avoiding the
    cost and dependency of loading a real tokenizer for every row at
    production data volumes.

    Args:
        text: Text to estimate a token count for.
        chars_per_token: Assumed average number of characters per token.

    Returns:
        ``max(1, round(len(text) / chars_per_token))`` for non-empty text,
        or ``0`` for ``None``/empty text.

    Raises:
        ValueError: If ``chars_per_token`` is not strictly positive.
    """
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be strictly positive.")
    if not text:
        return 0
    return max(1, round(len(text) / chars_per_token))


# ---------------------------------------------------------------------------
# Hash, ID, and UUID generation
# ---------------------------------------------------------------------------


def generate_sha256_hash(value: str) -> str:
    """Return the hex-encoded SHA-256 digest of ``value``.

    Args:
        value: String to hash.

    Returns:
        A 64-character lowercase hexadecimal digest.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_chunk_id(parent_asin: str, chunk_number: int) -> str:
    """Deterministically generate a stable, unique chunk identifier.

    The identifier is a pure function of ``parent_asin`` and
    ``chunk_number``: re-running the pipeline over unchanged source data
    reproduces identical chunk IDs, making writes idempotent and making
    ``previous_chunk_id``/``next_chunk_id`` computable locally (by
    applying this same function to ``chunk_number - 1``/``chunk_number +
    1``) without any shuffle or lookup against sibling rows.

    Args:
        parent_asin: Source document's product identifier.
        chunk_number: Zero-based position of this chunk within its source
            document.

    Returns:
        A 24-character hexadecimal identifier, truncated from a SHA-256
        digest. 24 hex characters (96 bits) makes accidental collision
        probability negligible at this pipeline's scale (millions of
        chunks), while keeping the identifier compact for storage and
        indexing.
    """
    digest = generate_sha256_hash(f"{parent_asin}::chunk::{chunk_number}")
    return digest[:24]


def generate_uuid4() -> str:
    """Generate a random (version 4) UUID string.

    Use for identifiers that must be unique per invocation (e.g. a
    pipeline run ID) rather than deterministically reproducible; for
    reproducible, content-derived identifiers, use
    ``generate_sha256_hash`` or ``generate_chunk_id`` instead.

    Returns:
        A UUID4 string, e.g. ``"3fa85f64-5717-4562-b3fc-2c963f66afa6"``.
    """
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------


def current_utc_timestamp() -> datetime:
    """Return the current time as a timezone-aware UTC ``datetime``.

    Returns:
        The current UTC time.
    """
    return datetime.now(timezone.utc)


def current_utc_iso_timestamp() -> str:
    """Return the current UTC time as an ISO-8601 string.

    Returns:
        The current UTC time formatted via ``datetime.isoformat()``.
    """
    return current_utc_timestamp().isoformat()


# ---------------------------------------------------------------------------
# Input / output validation
# ---------------------------------------------------------------------------


def validate_non_empty_string(value: Optional[str], field_name: str) -> str:
    """Validate that ``value`` is a non-blank string, returning it stripped.

    Args:
        value: Value to validate.
        field_name: Name of the field being validated, used to produce an
            actionable error message.

    Returns:
        ``value`` with leading/trailing whitespace removed.

    Raises:
        ValueError: If ``value`` is ``None``, not a string, or blank after
            stripping.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field_name}' must be a non-empty string; got: {value!r}")
    return value.strip()


def validate_positive_integer(value: int, field_name: str) -> int:
    """Validate that ``value`` is a strictly positive integer.

    Args:
        value: Value to validate.
        field_name: Name of the field being validated, used to produce an
            actionable error message.

    Returns:
        ``value`` unchanged.

    Raises:
        ValueError: If ``value`` is not an ``int`` or is not strictly
            positive.
    """
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"'{field_name}' must be a positive integer; got: {value!r}")
    return value


def validate_chunk_text_length(text: str, min_chars: int, max_chars: int) -> bool:
    """Check whether ``text`` falls within an acceptable character-length range.

    Non-raising by design: this is intended for output quality-assurance
    checks and metrics (e.g. counting how many generated chunks fall
    outside the target range) rather than for aborting processing.

    Args:
        text: Chunk text to check.
        min_chars: Inclusive minimum acceptable length.
        max_chars: Inclusive maximum acceptable length.

    Returns:
        ``True`` if ``min_chars <= len(text) <= max_chars``, else ``False``.
    """
    return min_chars <= len(text) <= max_chars


# ---------------------------------------------------------------------------
# S3 path validation
# ---------------------------------------------------------------------------

_S3_URI_PATTERN = re.compile(r"^s3://(?P<bucket>[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9])/(?P<key>.+)$")


def validate_s3_uri(uri: str) -> bool:
    """Check whether ``uri`` is a syntactically valid ``s3://bucket/key`` URI.

    Validates structure only (scheme, bucket-name character set and
    length, and a non-empty key); it does not check that the bucket or
    key actually exists in S3.

    Args:
        uri: URI to validate.

    Returns:
        ``True`` if ``uri`` matches the expected ``s3://bucket/key``
        structure, else ``False``.
    """
    return bool(isinstance(uri, str) and _S3_URI_PATTERN.match(uri))


def parse_s3_uri(uri: str) -> Tuple[str, str]:
    """Split an ``s3://bucket/key`` URI into its bucket and key components.

    Args:
        uri: URI to parse.

    Returns:
        A ``(bucket, key)`` tuple.

    Raises:
        ValueError: If ``uri`` is not a syntactically valid S3 URI.
    """
    match = _S3_URI_PATTERN.match(uri) if isinstance(uri, str) else None
    if not match:
        raise ValueError(f"'{uri}' is not a valid s3://bucket/key URI.")
    return match.group("bucket"), match.group("key")


# ---------------------------------------------------------------------------
# Data quality helpers
# ---------------------------------------------------------------------------

_ALPHANUMERIC_PATTERN = re.compile(r"[A-Za-z0-9]")


def is_blank(text: Optional[str]) -> bool:
    """Check whether ``text`` is ``None``, empty, or whitespace-only.

    Args:
        text: Text to check.

    Returns:
        ``True`` if ``text`` has no non-whitespace content.
    """
    return text is None or not text.strip()


def has_minimum_alphanumeric_ratio(text: str, minimum_ratio: float = 0.3) -> bool:
    """Check whether ``text`` contains a sufficient proportion of alphanumeric characters.

    Guards against near-empty-signal text (e.g. strings that are almost
    entirely punctuation, whitespace, or repeated symbols) passing through
    as if they were meaningful natural-language content.

    Args:
        text: Text to check.
        minimum_ratio: Minimum required ratio of alphanumeric characters
            to total characters.

    Returns:
        ``True`` if ``text`` is non-empty and its alphanumeric character
        ratio meets ``minimum_ratio``; ``False`` for empty text or text
        below the ratio.

    Raises:
        ValueError: If ``minimum_ratio`` is not between 0 and 1 inclusive.
    """
    if not 0.0 <= minimum_ratio <= 1.0:
        raise ValueError("minimum_ratio must be between 0.0 and 1.0 inclusive.")
    if not text:
        return False
    alphanumeric_count = len(_ALPHANUMERIC_PATTERN.findall(text))
    return (alphanumeric_count / len(text)) >= minimum_ratio


# ---------------------------------------------------------------------------
# Metadata generation and ordering
# ---------------------------------------------------------------------------


def build_metadata_record(
    base_fields: Dict[str, Any],
    include_timestamp: bool = True,
    include_run_id: bool = True,
) -> Dict[str, Any]:
    """Assemble a metadata record from caller-supplied fields plus standard fields.

    Centralizes the pattern of "a dictionary of facts about this run, plus
    a generated timestamp and/or run identifier", so every metadata/manifest
    record produced across the pipeline has a consistent shape.

    Args:
        base_fields: Caller-supplied fields to include verbatim.
        include_timestamp: Whether to add a ``generated_at_utc`` field.
        include_run_id: Whether to add a ``generated_run_id`` field.

    Returns:
        A new dictionary containing ``base_fields`` plus any requested
        standard fields. ``base_fields`` itself is not mutated.
    """
    record = dict(base_fields)
    if include_timestamp:
        record["generated_at_utc"] = current_utc_iso_timestamp()
    if include_run_id:
        record["generated_run_id"] = generate_uuid4()
    return record


def order_records_by_field(records: List[Dict[str, Any]], field_name: str) -> List[Dict[str, Any]]:
    """Return ``records`` sorted ascending by the value at ``field_name``.

    A generic ordering utility; for example, ordering a list of chunk
    records by their source-document character offset before assigning
    sequential chunk numbers.

    Args:
        records: List of dictionaries to sort. Not mutated.
        field_name: Key present in every record whose value determines
            sort order.

    Returns:
        A new, sorted list; ``records`` itself is left unmodified.

    Raises:
        KeyError: If any record is missing ``field_name``.
    """
    return sorted(records, key=lambda record: record[field_name])


# ---------------------------------------------------------------------------
# General reusable utilities
# ---------------------------------------------------------------------------


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide ``numerator`` by ``denominator``, returning ``default`` instead of raising on zero.

    Args:
        numerator: Dividend.
        denominator: Divisor.
        default: Value returned when ``denominator`` is zero.

    Returns:
        ``numerator / denominator``, or ``default`` if ``denominator`` is
        zero.
    """
    if denominator == 0:
        return default
    return numerator / denominator


# ---------------------------------------------------------------------------
# Execution timing
# ---------------------------------------------------------------------------


@dataclass
class Stopwatch:
    """A minimal, logging-independent execution timer.

    Distinct from ``logger.ExecutionTimer``: this class only measures
    elapsed time and carries no logging dependency, making it suitable for
    embedding a duration into a metrics dictionary or return value without
    forcing a log line to be emitted at the measurement site.

    Attributes:
        _start_time: Internal monotonic start time, set by ``start()``.
        _elapsed_seconds: Internal accumulated elapsed time, set by
            ``stop()``.
    """

    _start_time: Optional[float] = field(default=None, init=False, repr=False)
    _elapsed_seconds: Optional[float] = field(default=None, init=False, repr=False)

    def start(self) -> "Stopwatch":
        """Start (or restart) the stopwatch.

        Returns:
            ``self``, to support ``stopwatch = Stopwatch().start()``.
        """
        self._start_time = time.perf_counter()
        self._elapsed_seconds = None
        return self

    def stop(self) -> float:
        """Stop the stopwatch and return the elapsed time in seconds.

        Returns:
            Elapsed seconds since ``start()`` was called.

        Raises:
            RuntimeError: If ``start()`` was never called.
        """
        if self._start_time is None:
            raise RuntimeError("Stopwatch.stop() called before start().")
        self._elapsed_seconds = time.perf_counter() - self._start_time
        return self._elapsed_seconds

    def elapsed_seconds(self) -> float:
        """Return the most recently recorded elapsed time.

        Returns:
            The elapsed seconds recorded by the last ``stop()`` call.

        Raises:
            RuntimeError: If ``stop()`` has not yet been called.
        """
        if self._elapsed_seconds is None:
            raise RuntimeError("Stopwatch.elapsed_seconds() called before stop().")
        return self._elapsed_seconds
