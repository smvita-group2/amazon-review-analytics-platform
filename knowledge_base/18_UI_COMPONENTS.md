# 18 UI Components

## Purpose
Documents the library of reusable frontend UI components defined in `streamlit_app/theme.py` and page layouts, specifying purpose, parameters, behavior, and styling.

## Related Files
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
- [17 Design System](17_DESIGN_SYSTEM.md)
- [19 Frontend Guidelines](19_FRONTEND_GUIDELINES.md)

## Key Concepts
- **Reusable Component Wrappers**: Modular Python helper functions encapsulating custom HTML/CSS markup.
- **Consistent Page Layouts**: Standardized navigation header, sidebar logo, metric badges, and product cards.

## Content

### Reusable UI Component Specifications

#### 1. Top Navbar (`render_top_navbar`)
- **Purpose**: Global branding top navigation bar displaying platform title and active page links.
- **Parameters**: None.
- **Behavior**: Renders high-contrast dark banner (`#131921`) with hover state navigation links.
- **Styling**: Sticky top position, height 60px, Amazon orange hover highlights (`#FF9900`).

#### 2. Sidebar Brand Mark (`render_sidebar_logo`)
- **Purpose**: Displays animated Amazon Review Intelligence brand mark at top of sidebar.
- **Parameters**: None.
- **Behavior**: Displays SVG logo with smooth hover transition.
- **Styling**: White background container, subtle 1px border (`#D9E2EC`).

#### 3. Metric Badge Card
- **Purpose**: Highlights platform key performance indicators (KPIs) like total reviews, avg rating, catalog size.
- **Parameters**: `label` (str), `value` (str), `delta` (str), `icon` (str).
- **Behavior**: Clean card container displaying bold value and trend delta badge.
- **Styling**: White background (`#FFFFFF`), border `1px solid #D9E2EC`, border-radius `12px`.

#### 4. Product Result Card
- **Purpose**: Renders individual product search hits in RAG results.
- **Parameters**: `asin` (str), `title` (str), `rating` (float), `positive_aspects` (list), `negative_aspects` (list).
- **Behavior**: Expandable card showing product title, rating stars, and key review takeaways.
- **Styling**: Rounded border card, star rating badges, light green/red aspect tag highlights.

#### 5. Streaming Gemini Answer Container
- **Purpose**: Displays context-grounded AI synthesis streaming response with source citations.
- **Parameters**: `stream_generator` (Iterable), `retrieved_sources` (list).
- **Behavior**: Real-time token streaming text animation followed by expandable context source cards.

## Next Reading
- [19 Frontend Guidelines](19_FRONTEND_GUIDELINES.md)
