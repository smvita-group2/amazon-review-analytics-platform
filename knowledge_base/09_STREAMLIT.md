# 09 Streamlit UI

## Application Structure

Located in `streamlit_app/`:

```text
streamlit_app/
├── Home.py                  # Landing page & system architecture overview
├── theme.py                 # Styling system, dark theme CSS tokens, cards & layouts
└── pages/
    ├── 1_Product_Search.py  # Hybrid RAG product search & conversational review analysis
    └── 2_Dashboard.py       # Product analytics, rating distribution & category charts
```

## UI Page Details

### 1. `Home.py`
- **Purpose**: Welcomes users and introduces the platform's features.
- **Components**: High-level platform stats, data pipeline diagrams, technical architecture overview.

### 2. `pages/1_Product_Search.py`
- **Purpose**: Primary interactive interface for natural language query execution.
- **Features**:
  - Natural language search bar with category filtering.
  - Hybrid retrieval parameter configuration (top_k, alpha weight, rerank flags).
  - Gemini LLM streaming answer display with expandable retrieved source context cards.
  - Individual product breakdown cards displaying star ratings, positive/negative review takeaways.

### 3. `pages/2_Dashboard.py`
- **Purpose**: Interactive BI metrics dashboard.
- **Features**: Review volume trends, rating distribution histograms, top-rated products table.

### 4. `theme.py`
- **Purpose**: Centralized custom CSS injector introducing dark mode theme styling, card borders, and custom metric badges.
