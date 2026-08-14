# Generated Dependencies Index

## Purpose
Index of core third-party Python packages, version specs, and inter-module dependency relationships.

## Related Files
- [03 Tech Stack](../03_TECH_STACK.md)
- [Module Index](module_index.md)

## Key Concepts
- **Dependency Inventory**: Core Python libraries, version specs, and functional usage across the platform.

## Content

### External Third-Party Packages
```text
Dependency           Version Specifier   Purpose
-------------------  ------------------  ----------------------------------------------
numpy                >=1.24.0, <2.0.0    Numeric array computations
pandas               >=1.5.0, <2.2.0     DataFrame operations & analytics
pyarrow              >=10.0.0, <15.0.0   Parquet file format serialization
boto3                Latest              AWS SDK for S3, Glue, and CloudWatch
python-dotenv        Latest              Environment variable management
rank-bm25            >=0.2.2             BM25 lexical search implementation
google-genai         >=1.37.0            Google Gemini SDK
sentence-transformers >=5.1.0            Dense vector embedding models
chromadb             ==1.0.20            Vector database storage
scikit-learn         ==1.7.1             Metric utilities & evaluation
streamlit            ==1.49.1            Interactive web application framework
pytest               Latest              Automated unit and integration testing
```

### Module Dependency Mapping
```text
gluejobs/ ──► src/ ──► config/
ml_pipeline/ ──► config/
streamlit_app/ ──► ml_pipeline/
tests/ ──► src/, ml_pipeline/, config/
```

## Next Reading
- [03 Tech Stack](../03_TECH_STACK.md)
