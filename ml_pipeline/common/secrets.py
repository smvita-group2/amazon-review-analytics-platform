import os

from dotenv import load_dotenv

load_dotenv()


def get_secret(
    key: str,
) -> str:
    """
    Get a secret from environment variables.
    """

    value = os.getenv(key)

    if not value:

        raise ValueError(f"Missing environment variable: {key}")

    return value
