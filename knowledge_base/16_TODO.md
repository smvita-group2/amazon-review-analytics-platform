# 16 Project TODO

## Purpose
Tracks technical debt, planned roadmap features, and future system enhancements for the Amazon Review Analytics Platform.

## Related Files
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [12 Testing](12_TESTING.md)
- [15 Decisions](15_DECISIONS.md)

## Key Concepts
- **Roadmap Planning**: Future platform extensions across automated pipeline triggers, remote vector databases, CI/CD evaluation, and multi-category scaling.

## Content

### Tracked Technical Debt & Feature Roadmap

#### 1. Automated ML Pipeline Triggers
- Add event-driven triggers (S3 event notification / EventBridge) to rebuild BM25 indices and ChromaDB vector collections whenever new Gold datasets are published by Glue jobs.

#### 2. Vector DB Scaling
- Support remote vector database deployments (e.g. OpenSearch Serverless or Pinecone) alongside local ChromaDB for multi-node cloud deployments.

#### 3. Continuous ML Evaluation
- Integrate `faithfulness.py` and `retrieval_relevance.py` evaluation scripts directly into GitHub CI workflows (`.github/workflows/ci.yml`) to prevent retrieval quality regression.

#### 4. Concurrent Multi-Category ETL Fan-Out
- Expand Glue workflows to dynamically launch parallel PySpark jobs across all Amazon product categories concurrently.

#### 5. Streamlit Component Testing
- Expand PyTest suite to include mock UI integration tests using Streamlit's official testing framework (`streamlit.testing`).

## Next Reading
- [17 Design System](17_DESIGN_SYSTEM.md)
