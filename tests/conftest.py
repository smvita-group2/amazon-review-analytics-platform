"""
Shared pytest fixtures.

Provides PySpark test session fixtures and test data helpers.
"""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """
    Provides a shared PySpark local session for unit testing.
    """
    session = (
        SparkSession.builder.appName("AmazonReviewAnalyticsUnitTests")
        .master("local[1]")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()
