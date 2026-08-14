# 17 Design System

## Purpose
Defines the Amazon Light design system tokens, typography, layout grid, UI states, component aesthetics, and accessibility rules implemented in `streamlit_app/theme.py`.

## Related Files
- [09 Streamlit Overview](09_STREAMLIT_OVERVIEW.md)
- [18 UI Components](18_UI_COMPONENTS.md)
- [19 Frontend Guidelines](19_FRONTEND_GUIDELINES.md)

## Key Concepts
- **Design Tokens**: Standardized CSS variables defining background, accent, text, and border colors.
- **Amazon Light Aesthetics**: High-contrast, clean e-commerce UI featuring Amazon `#FF9900` orange accents on `#131921` dark navigation containers.
- **Typography Standard**: Google Font `Plus Jakarta Sans` applied globally.

## Content

### Design System Tokens (`theme.py`)

#### Color Palette
- **Page Background (`--bg-page`)**: `#F7F9FC`
- **Card Surface (`--bg-card`)**: `#FFFFFF`
- **Primary Orange (`--primary-orange`)**: `#FF9900` (Hover: `#E68A00`)
- **Primary Dark (`--primary-dark`)**: `#131921` (Hover: `#232F3E`)
- **Secondary Blue (`--secondary-blue`)**: `#2563EB`
- **Heading Text (`--heading-color`)**: `#172033`
- **Body Text (`--body-text`)**: `#475569`
- **Muted Text (`--muted-text`)**: `#64748B`
- **Border Neutral (`--border-color`)**: `#D9E2EC`
- **Light Orange Tint (`--light-orange`)**: `#FFF3E0`
- **Success Green (`--success-green`)**: `#15803D`

#### Typography & Spacing
- **Font Family**: `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif`
- **Max Page Width**: `1440px` (Padding: `1rem 1.5rem`)
- **Border Radius**: Cards (`12px`), Buttons/Badges (`8px`), Sidebar (`8px`)
- **Box Shadows**: Cards (`0 4px 20px rgba(0,0,0,0.04)`), Navbar (`0 4px 15px rgba(0,0,0,0.12)`)

#### Component States
- **Tab Selection**: Amazon Orange (`#FF9900`) bottom indicator line (3px height).
- **Loading States**: Animated pulsing placeholders and Streamlit native spinners (`st.spinner`).
- **Error States**: Muted red background tint (`#FEF2F2`) with dark red text (`#991B1B`).
- **Success States**: Light green container (`#F0FDF4`) with green text (`#15803D`).
- **Accessibility**: High contrast contrast ratio (> 4.5:1) between body text (`#475569`) and card background (`#FFFFFF`).

## Next Reading
- [18 UI Components](18_UI_COMPONENTS.md)
