# 16 Project TODO

## Tracked Technical Debt & Future Roadmap

1. **Automated ML Pipeline Triggers**:
   - Add automated triggers to rebuild BM25 indices and ChromaDB vector collections whenever new Gold datasets are published by Glue.

2. **Vector DB Scaling**:
   - Support remote vector database deployments (e.g. OpenSearch or Pinecone) alongside local ChromaDB for multi-node production deployment.

3. **Evaluation Automation**:
   - Integrate `faithfulness.py` and `retrieval_relevance.py` evaluation scripts directly into GitHub CI workflow to prevent quality regression.

4. **Multi-Category Parallel Execution**:
   - Expand Glue workflows to dynamically fan-out ETL jobs across all Amazon product categories concurrently.

5. **Expanded Test Coverage**:
   - Add mock UI tests for Streamlit pages using `streamlit.testing`.
