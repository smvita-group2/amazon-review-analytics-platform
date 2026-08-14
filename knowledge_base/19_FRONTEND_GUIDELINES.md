# 19 Frontend Guidelines

## Purpose
Establishes engineering best practices, layout rules, state management standards, and accessibility guidelines for building Streamlit UI interfaces.

## Related Files
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
- [17 Design System](17_DESIGN_SYSTEM.md)
- [18 UI Components](18_UI_COMPONENTS.md)

## Key Concepts
- **UI Philosophy**: Professional, high-contrast e-commerce intelligence platform wowed by clean typography, structured metric cards, and responsive charts.
- **Streamlit Best Practices**: Encapsulating global theme injection, maintaining session state cleanliness, avoiding heavy computations on main render threads.

## Content

### Development Standards & Guidelines

#### 1. Theme & Styling Injection Rules
- Always invoke `inject_amazon_theme()` at the top of every new page module immediately after `st.set_page_config()`.
- Never insert inline raw CSS styles inside page scripts; define all CSS utility classes inside `streamlit_app/theme.py`.

#### 2. Layout & Spacing Consistency
- Maintain max grid container width of `1440px`.
- Use standard vertical padding (`1rem`) and horizontal page margins (`1.5rem`).
- Group related form controls using `st.container()` or `st.columns()` rather than loose unaligned controls.

#### 3. Session State & Execution Efficiency
- Store expensive model references (vector DB client, tokenizer, embedding models) in `st.session_state` or wrap loader methods with `@st.cache_resource`.
- Wrap tabular dataframe loading methods with `@st.cache_data`.

#### 4. Responsiveness & Accessibility
- Design multi-column layouts to stack gracefully on smaller viewports.
- Maintain high text contrast ratios against white card backgrounds.
- Provide descriptive labels and placeholders on all text input and select box widgets.

#### 5. Error & Loading UX
- Wrap async RAG queries in `st.spinner("Retrieving product reviews and synthesizing answer...")`.
- Catch API exceptions cleanly and present user-friendly error banners (`st.error`) without exposing raw stack traces.

## Next Reading
- [20 Agent Index](20_AGENT_INDEX.md)
