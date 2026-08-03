"""
Smoke tests verifying core package imports, configuration loading, and pipeline readiness.
"""

from ml_pipeline.common.config import get_setting
from ml_pipeline.common.constants import CATEGORIES, PARENT_ASIN
from ml_pipeline.embeddings.embedding_generator import EmbeddingGenerator
from ml_pipeline.embeddings.embedding_model import EmbeddingModel
from ml_pipeline.product_documents.document_builder import ProductDocumentBuilder
from ml_pipeline.product_documents.formatter import ProductDocumentFormatter
from ml_pipeline.product_documents.review_selector import ReviewSelector
from ml_pipeline.retrieval.rrf import ReciprocalRankFusion
from src.bronze_to_silver.metadata_transformer import MetadataTransformer
from src.bronze_to_silver.reviews_transformer import ReviewsTransformer
from src.silver_to_gold.gold_visualization_transformer import GoldVisualizationTransformer
from src.silver_to_gold.silver_master_transformer import SilverMasterTransformer
from src.validation.metadata_validator import MetadataValidator
from src.validation.reviews_validator import ReviewsValidator


def test_package_imports_smoke():
    """
    Verify all core ETL, ML, RAG, and validation classes import without error.
    """
    assert ReviewsTransformer is not None
    assert MetadataTransformer is not None
    assert SilverMasterTransformer is not None
    assert GoldVisualizationTransformer is not None
    assert ReviewsValidator is not None
    assert MetadataValidator is not None
    assert ProductDocumentBuilder is not None
    assert ReviewSelector is not None
    assert ProductDocumentFormatter is not None
    assert EmbeddingModel is not None
    assert EmbeddingGenerator is not None
    assert ReciprocalRankFusion is not None


def test_config_settings_smoke():
    """
    Verify YAML settings and project constants load cleanly.
    """
    assert PARENT_ASIN == "parent_asin"
    assert len(CATEGORIES) > 0

    model_name = get_setting("embedding", "model_name")
    assert model_name == "sentence-transformers/all-MiniLM-L6-v2"

    cleaned_path = get_setting("paths", "cleaned")
    assert cleaned_path == "data/cleaned_data"
