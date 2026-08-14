# Task Prompt: Streamlit Frontend Development

## Context Files to Load
Before beginning work on Streamlit UI pages, components, or theme styling, you MUST load the following knowledge files:
1. `knowledge_base/00_PROJECT_OVERVIEW.md`
2. `knowledge_base/09_STREAMLIT_OVERVIEW.md`
3. `knowledge_base/09_STREAMLIT_PAGES.md`
4. `knowledge_base/17_DESIGN_SYSTEM.md`
5. `knowledge_base/18_UI_COMPONENTS.md`
6. `knowledge_base/19_FRONTEND_GUIDELINES.md`

## Instructions
- Adhere strictly to the Amazon Light design system tokens defined in `streamlit_app/theme.py`.
- Call `inject_amazon_theme()` at the top of every page module.
- Maintain maximum layout container width of 1440px.
- Use high-contrast foreground text colors on tab elements and card backgrounds.
- Wrap heavy resource initializations with `@st.cache_resource` and DataFrame loaders with `@st.cache_data`.
