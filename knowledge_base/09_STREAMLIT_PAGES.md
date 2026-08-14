# 09 Streamlit Pages

## Purpose
Detailed documentation of the application pages (`Home.py`, `1_Product_Search.py`, `2_Dashboard.py`), describing user workflows, interactive controls, and backend integrations.

## Related Files
- [08 ML Pipeline](08_ML_PIPELINE.md)
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
- [18 UI Components](18_UI_COMPONENTS.md)
- [19 Frontend Guidelines](19_FRONTEND_GUIDELINES.md)

## Key Concepts
- **Product Search Page**: Natural language RAG interface executing hybrid retrieval (dense vector + sparse BM25) and Gemini streaming synthesis.
- **Analytics Dashboard Page**: Interactive BI visual analytics covering rating distributions, review volumes, and product leaderboards.

## Content

### Page Specifications

#### 1. Landing Overview (`Home.py`)
- **Purpose**: Introduces the platform, key business capabilities, and data lake architecture.
- **Features**: High-level platform metric badges, interactive architecture diagram rendering, quick navigation callouts.

#### 2. RAG Product Search (`pages/1_Product_Search.py`)
- **Purpose**: Primary interactive natural language search interface over product metadata and customer reviews.
- **Features**:
  - Natural language search bar with category selection dropdown.
  - Advanced search hyperparameter controls (`top_k`, `alpha` dense/sparse weight, cross-encoder rerank flag).
  - Gemini LLM streaming response container with expandable retrieved context source cards.
  - Individual product result cards with star ratings, positive takeaways, and negative takeaways.

#### 3. Analytics Dashboard (`pages/2_Dashboard.py`)
- **Purpose**: Interactive BI metrics dashboard for dataset analysis.
- **Features**: Review volume trends over time, rating distribution histograms, top-rated products table, category filtering.

## Next Reading
- [10 Terraform](10_TERRAFORM.md)
