# 09 Streamlit Overview

## Purpose
Provides an architectural overview of the Streamlit frontend web application, module layout, theme integration (`theme.py`), page navigation, and layout styling.

## Related Files
- [09 Streamlit Pages](09_STREAMLIT_PAGES.md)
- [17 Design System](17_DESIGN_SYSTEM.md)
- [18 UI Components](18_UI_COMPONENTS.md)
- [19 Frontend Guidelines](19_FRONTEND_GUIDELINES.md)

## Key Concepts
- **Multi-Page Application Structure**: Standardized Streamlit `pages/` layout (`Home.py`, `1_Product_Search.py`, `2_Dashboard.py`).
- **Amazon Light Theme**: Custom CSS tokens injected globally via `inject_amazon_theme()`.
- **Custom Top Navbar**: High-contrast top header navbar and animated logo component.

## Content

### Application Directory Structure
```text
streamlit_app/
├── Home.py                  # Landing page & platform architecture overview
├── theme.py                 # Amazon Light CSS tokens, top navbar, logo & sidebar
└── pages/
    ├── 1_Product_Search.py  # Hybrid RAG search & conversational review analysis
    └── 2_Dashboard.py       # Analytics dashboard, rating distribution & category metrics
```

### Theme & Styling Integration (`theme.py`)
- `inject_amazon_theme()`: Injects custom CSS rules, Plus Jakarta Sans typography, high-contrast tab controls, card styling, and custom metric badges.
- `render_top_navbar()`: Displays custom Amazon Review Intelligence top navigation bar with page routing controls.
- `render_sidebar_logo()`: Displays animated SVG brand mark in sidebar header.

## Next Reading
- [09 Streamlit Pages](09_STREAMLIT_PAGES.md)
