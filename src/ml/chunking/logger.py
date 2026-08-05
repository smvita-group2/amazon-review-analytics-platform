#!/usr/bin/env python3
"""Production logging utilities for the Hybrid RAG Intelligent Product Search pipeline.

Provides a thread-safe logger factory that attaches console and/or rotating
file handlers according to ``config.LoggingConfig``, a structured JSON
formatter for log-aggregation pipelines, an execution-timer context
manager/decorator pair for START/END/ELAPSED stage logging, an
exception-logging decorator, and helpers for coexisting cleanly with
Spark's own JVM-side (log4j) logging.

This module contains no business logic and never calls ``print()``; all
output goes through the standard library ``logging`` module.
"""

from __future__ import annotations

import functools
import json
import logging
import logging.handlers
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Set, TypeVar

from config import LoggingConfig

FuncType = TypeVar("FuncType", bound=Callable[..., Any])

# Guards creation/handler-attachment of loggers so concurrent callers
# (e.g. multiple threads driving parallel Spark actions) never attach
# duplicate handlers to the same logger.
_REGISTRY_LOCK = threading.Lock()
_CONFIGURED_LOGGER_NAMES: Set[str] = set()

# Third-party loggers that are extremely verbose at INFO/DEBUG and would
# otherwise drown out pipeline-specific log lines when running under Spark.
_NOISY_THIRD_PARTY_LOGGERS: tuple = ("py4j", "py4j.java_gateway", "py4j.clientserver")


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


class StructuredJsonFormatter(logging.Formatter):
    """Formatter emitting one JSON object per log record.

    Intended for environments where logs are shipped to a log-aggregation
    system (e.g. CloudWatch Logs Insights, OpenSearch) that benefits from
    structured, queryable fields rather than free-text lines.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as a single-line JSON string.

        Args:
            record: The log record to format.

        Returns:
            A JSON-encoded string representing the record. Non-serializable
            field values are coerced to their string representation via
            ``default=str`` rather than raising, since a formatter must
            never itself throw and swallow the original log line.
        """
        payload = {
            "timestamp_utc": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "process": record.process,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _build_formatter(config: LoggingConfig) -> logging.Formatter:
    """Build the formatter selected by ``config.structured_json_logging``.

    Args:
        config: Logging configuration.

    Returns:
        A ``StructuredJsonFormatter`` when structured logging is enabled,
        otherwise a plain-text ``logging.Formatter`` using
        ``config.log_format``/``config.date_format``.
    """
    if config.structured_json_logging:
        return StructuredJsonFormatter()
    return logging.Formatter(fmt=config.log_format, datefmt=config.date_format)


# ---------------------------------------------------------------------------
# Handler builders
# ---------------------------------------------------------------------------


def _build_console_handler(formatter: logging.Formatter) -> logging.Handler:
    """Build a stdout stream handler.

    EMR captures a step's stdout into its step/driver logs, so a stream
    handler targeting stdout is sufficient for EMR-native log capture
    without any additional shipping configuration.

    Args:
        formatter: Formatter to attach to the handler.

    Returns:
        A configured ``logging.StreamHandler``.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def _build_file_handler(
    config: LoggingConfig, formatter: logging.Formatter
) -> Optional[logging.Handler]:
    """Build a rotating local file handler, or ``None`` if it cannot be created.

    File handler creation is defensive: on EMR, a driver may run under a
    user or in a directory without write permission to the configured log
    directory. Rather than crash the entire Spark application over a
    logging side-channel, a failure here is caught, reported via the
    console handler (which is always attempted first), and ``None`` is
    returned so the caller simply proceeds without file logging.

    Args:
        config: Logging configuration.
        formatter: Formatter to attach to the handler.

    Returns:
        A configured ``logging.handlers.RotatingFileHandler``, or ``None``
        if the log directory could not be created or opened for writing.
    """
    try:
        os.makedirs(config.log_file_directory, exist_ok=True)
        log_file_path = os.path.join(config.log_file_directory, config.log_file_name)
        handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=config.max_log_file_size_bytes,
            backupCount=config.backup_count,
        )
        handler.setFormatter(formatter)
        return handler
    except OSError as exc:
        logging.getLogger(config.logger_name).warning(
            "File logging disabled; could not create log file at '%s/%s': %s",
            config.log_file_directory,
            config.log_file_name,
            exc,
        )
        return None


# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------


class LoggerFactory:
    """Thread-safe factory that builds and caches configured loggers.

    Repeated calls with the same logger name are idempotent: only the
    first call attaches handlers, and every subsequent call returns the
    same underlying ``logging.Logger`` without re-attaching handlers,
    which would otherwise duplicate every log line.
    """

    @staticmethod
    def get_logger(name: str, config: Optional[LoggingConfig] = None) -> logging.Logger:
        """Return a configured logger, creating and caching it on first use.

        Args:
            name: Logger name, conventionally the calling module's
                ``__name__``.
            config: Logging configuration to apply. Defaults to
                ``LoggingConfig()`` (its dataclass defaults) when omitted.

        Returns:
            A ``logging.Logger`` with console and/or file handlers attached
            according to ``config``, propagation disabled (so records are
            not duplicated by the root logger's own handlers), and its
            level set to ``config.log_level``.
        """
        resolved_config = config or LoggingConfig()
        logger = logging.getLogger(name)

        with _REGISTRY_LOCK:
            if name in _CONFIGURED_LOGGER_NAMES:
                return logger

            logger.setLevel(resolved_config.log_level.value)
            logger.propagate = False

            formatter = _build_formatter(resolved_config)

            if resolved_config.enable_console_logging:
                logger.addHandler(_build_console_handler(formatter))

            if resolved_config.enable_file_logging:
                file_handler = _build_file_handler(resolved_config, formatter)
                if file_handler is not None:
                    logger.addHandler(file_handler)

            _CONFIGURED_LOGGER_NAMES.add(name)

        return logger


def get_logger(name: str, config: Optional[LoggingConfig] = None) -> logging.Logger:
    """Module-level convenience wrapper around ``LoggerFactory.get_logger``.

    Args:
        name: Logger name, conventionally the calling module's ``__name__``.
        config: Logging configuration to apply.

    Returns:
        A configured ``logging.Logger``.
    """
    return LoggerFactory.get_logger(name, config)


# ---------------------------------------------------------------------------
# Spark-compatible logging
# ---------------------------------------------------------------------------


def suppress_verbose_third_party_logging() -> None:
    """Raise the level of known-noisy third-party loggers to ``WARNING``.

    Py4J, the bridge Spark's Python driver uses to talk to the JVM, emits
    high-volume INFO/DEBUG chatter that has no diagnostic value for this
    pipeline's own logs and otherwise crowds out pipeline-specific log
    lines when the root logger level is permissive.
    """
    for noisy_logger_name in _NOISY_THIRD_PARTY_LOGGERS:
        logging.getLogger(noisy_logger_name).setLevel(logging.WARNING)


def get_spark_log4j_logger(spark_session: Any, logger_name: str) -> Any:
    """Return a log4j logger obtained from the active ``SparkSession``'s JVM gateway.

    Useful when a log line should be written through Spark's own log4j
    logging system (and therefore end up in the same YARN container logs
    Spark's own log lines go to) rather than through a separate
    Python-only stream that an operator might not think to check.

    Args:
        spark_session: The active ``pyspark.sql.SparkSession``.
        logger_name: Name to register the log4j logger under.

    Returns:
        A ``py4j.java_gateway.JavaObject`` proxying an
        ``org.apache.log4j.Logger`` instance, exposing ``.info(str)``,
        ``.warn(str)``, ``.error(str)``, and ``.debug(str)`` methods.
    """
    log_manager = spark_session._jvm.org.apache.log4j.LogManager  # noqa: SLF001
    return log_manager.getLogger(logger_name)


# ---------------------------------------------------------------------------
# Execution timing
# ---------------------------------------------------------------------------


class ExecutionTimer:
    """Context manager that logs START/END/ELAPSED for a named stage of work.

    Example:
        with ExecutionTimer(logger, "read_final_documents"):
            df = spark.read.parquet(input_path)
    """

    def __init__(self, logger: logging.Logger, stage_name: str) -> None:
        """Initialize the timer.

        Args:
            logger: Logger to emit START/END/ELAPSED/FAILED messages to.
            stage_name: Human-readable name of the stage being timed.
        """
        self._logger = logger
        self._stage_name = stage_name
        self._start_time: float = 0.0

    def __enter__(self) -> "ExecutionTimer":
        self._start_time = time.time()
        self._logger.info("STAGE START | %s", self._stage_name)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        elapsed_seconds = time.time() - self._start_time
        if exc_type is None:
            self._logger.info(
                "STAGE END | %s | elapsed_seconds=%.2f", self._stage_name, elapsed_seconds
            )
        else:
            self._logger.error(
                "STAGE FAILED | %s | elapsed_seconds=%.2f | error=%s",
                self._stage_name,
                elapsed_seconds,
                exc_value,
            )
        return False  # never suppress the exception


def timed_stage(
    logger: Optional[logging.Logger] = None, stage_name: Optional[str] = None
) -> Callable[[FuncType], FuncType]:
    """Decorator variant of ``ExecutionTimer`` for timing an entire function.

    Args:
        logger: Logger to emit timing messages to. When omitted, a logger
            is resolved via ``get_logger(func.__module__)`` at call time,
            so the decorator can be applied without a logger being
            available at import time.
        stage_name: Name to log for this stage. Defaults to the wrapped
            function's qualified name.

    Returns:
        A decorator that wraps the target function with START/END/ELAPSED
        logging identical to ``ExecutionTimer``.
    """

    def decorator(func: FuncType) -> FuncType:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            active_logger = logger or get_logger(func.__module__)
            resolved_stage_name = stage_name or func.__qualname__
            with ExecutionTimer(active_logger, resolved_stage_name):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# Exception logging
# ---------------------------------------------------------------------------


def log_exceptions(
    logger: Optional[logging.Logger] = None, reraise: bool = True
) -> Callable[[FuncType], FuncType]:
    """Decorator that logs any exception raised by the wrapped function with a full traceback.

    Args:
        logger: Logger to emit the exception to. When omitted, a logger is
            resolved via ``get_logger(func.__module__)`` at call time.
        reraise: When ``True`` (default), the original exception is
            re-raised after logging, preserving normal failure propagation
            for callers such as ``spark-submit`` exit-code handling. When
            ``False``, the exception is swallowed and ``None`` is returned
            instead; this should be used sparingly and only for genuinely
            non-fatal, best-effort operations.

    Returns:
        A decorator that wraps the target function with exception logging.
    """

    def decorator(func: FuncType) -> FuncType:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            active_logger = logger or get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception:
                active_logger.error(
                    "Unhandled exception in '%s'", func.__qualname__, exc_info=True
                )
                if reraise:
                    raise
                return None

        return wrapper  # type: ignore[return-value]

    return decorator
