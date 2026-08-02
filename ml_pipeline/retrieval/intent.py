"""
Intent

Represents the parsed user intent used by the
Hybrid RAG retrieval pipeline.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Intent:
    """
    Structured representation of a user query.
    """

    original_query: str

    product_type: str | None = None

    brand: str | None = None

    capacity: str | None = None

    budget: bool = False

    premium: bool = False

    priority_features: list[str] = field(
        default_factory=list,
    )

    use_case: str | None = None