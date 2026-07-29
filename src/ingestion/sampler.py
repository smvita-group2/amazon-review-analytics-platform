from pyspark.sql import DataFrame


def create_sample(
    df: DataFrame,
    fraction: float = 0.01,
    seed: int = 42,
) -> DataFrame:
    """
    Create a reproducible random sample from a DataFrame.

    Args:
        df: Input Spark DataFrame.
        fraction: Fraction of rows to sample.
        seed: Random seed for reproducibility.

    Returns:
        Sampled Spark DataFrame.
    """

    return df.sample(
        withReplacement=False,
        fraction=fraction,
        seed=seed,
    )
