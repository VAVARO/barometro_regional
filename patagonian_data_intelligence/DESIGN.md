---
name: Patagonian Data Intelligence
colors:
  surface: '#f8f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f8f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#43474d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#74777e'
  outline-variant: '#c4c6ce'
  surface-tint: '#49607e'
  primary: '#000f22'
  on-primary: '#ffffff'
  primary-container: '#0a2540'
  on-primary-container: '#768dad'
  inverse-primary: '#b0c8eb'
  secondary: '#00658d'
  on-secondary: '#ffffff'
  secondary-container: '#41befd'
  on-secondary-container: '#004b69'
  tertiary: '#000f22'
  on-tertiary: '#ffffff'
  tertiary-container: '#142538'
  on-tertiary-container: '#7c8ca4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d2e4ff'
  primary-fixed-dim: '#b0c8eb'
  on-primary-fixed: '#001c37'
  on-primary-fixed-variant: '#314865'
  secondary-fixed: '#c6e7ff'
  secondary-fixed-dim: '#81cfff'
  on-secondary-fixed: '#001e2d'
  on-secondary-fixed-variant: '#004c6b'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f8f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.01em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 32px
  gutter: 24px
  margin-sm: 16px
  margin-md: 32px
  margin-lg: 64px
---

## Brand & Style
The design system is engineered for the "Barómetro Regional de la Universidad de Aysén," balancing academic authority with the crystalline, forward-looking aesthetic of the Aysén region. The target audience includes researchers, policymakers, and the general public, requiring a UI that feels both intellectually rigorous and highly accessible.

The design style is **Modern Corporate with Glassmorphic Accents**. It leverages high-end data analytics aesthetics—prioritizing clarity, expansive whitespace, and subtle depth. By mixing "Institutional Blue" for stability with "Ice Turquoise" for interactivity, the system evokes a sense of cold, clear precision. Glassmorphism is used sparingly on overlay elements (tooltips, dropdowns, and modal headers) to provide a sense of lightness and technical sophistication without compromising legibility.

## Colors
The palette is rooted in the deep tones of the Patagonian waters and the clarity of glacial ice. 

- **Primary (#0A2540):** Used for navigation, high-level headers, and primary data series. It provides the "Institutional" anchor.
- **Secondary/Accent (#00A3E0):** Reserved for interactive states, call-to-actions, and highlight data points. This color should be used as a gradient when paired with the primary blue to signify momentum.
- **Background (#F4F6F8):** A cool-toned gray that reduces eye strain during long periods of data analysis.
- **Surface (#FFFFFF):** Pure white for cards and containers to maximize contrast against the background.
- **Semantic Colors:** Success (Emerald), Warning (Amber), and Error (Rose) should be desaturated to match the professional tone of the system.

## Typography
This design system utilizes a dual-font strategy. **Plus Jakarta Sans** is used for headings to provide a modern, slightly rounded, and welcoming character to regional data. **Inter** is used for all body text, data tables, and labels due to its exceptional legibility at small sizes and its neutral, systematic feel.

For data visualization, use `label-md` for axis titles and `caption` for tick marks. Numbers in dashboards should prioritize tabular lining figures to ensure vertical alignment in data columns.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a max-width of 1440px for dashboard views. 

- **Desktop:** 12-column grid, 24px gutters, 32px side margins.
- **Tablet:** 8-column grid, 16px gutters, 24px side margins.
- **Mobile:** 4-column grid, 16px gutters, 16px side margins.

Data cards should span 3, 4, 6, or 12 columns. Vertical spacing follows an 8px scale, ensuring that related data points are grouped tightly (8-16px) while major sections are separated by significant whitespace (48-64px) to maintain the "ultra-clean" aesthetic.

## Elevation & Depth
Hierarchy is established through a mix of **Tonal Layering** and **Ambient Shadows**.

1.  **Level 0 (Background):** The `#F4F6F8` canvas.
2.  **Level 1 (Cards):** Pure white surfaces with a `shadow-sm` (0 2px 4px rgba(10, 37, 64, 0.05)).
3.  **Level 2 (Active/Hover States):** Enhanced cards with a `shadow-md` (0 12px 24px rgba(10, 37, 64, 0.08)).
4.  **Level 3 (Interactive Overlays):** Tooltips and menus use a glassmorphic effect: `Background: rgba(255, 255, 255, 0.8)`, `Backdrop-filter: blur(12px)`, and a 1px border of `rgba(255, 255, 255, 0.5)`.

Avoid heavy black shadows; instead, use low-opacity versions of the Primary Blue to keep the shadows "cool" and integrated with the brand.

## Shapes
The shape language is purposefully soft to contrast with the "hard" nature of data. 

- **Cards & Containers:** Use `rounded-lg` (16px) for main dashboard modules.
- **Interactive Elements:** Buttons and input fields use `rounded-md` (8px).
- **Selection Indicators:** Pills and tags use a fully rounded `9999px` radius.

Charts should also reflect this: bar charts should have slightly rounded caps (4px), and line charts should use smooth bezier curves rather than sharp angles.

## Components

- **Buttons:** Primary buttons use a gradient from Institutional Blue to Ice Turquoise. Secondary buttons use a ghost style with a 1px border and Ice Turquoise text.
- **Data Cards:** Cards must include a padding of 24px. Headers within cards should use `label-md` in uppercase with slight letter spacing to differentiate sections.
- **Input Fields:** Fields are white with a 1px border of `#E2E8F0`. On focus, the border changes to Ice Turquoise with a subtle outer glow.
- **Charts:** Use a custom color ramp starting from Ice Turquoise for the highest values, transitioning through Primary Blue for mid-tones, and Gray for baseline data. Grid lines in charts must be extremely subtle (`#F1F5F9`).
- **Chips/Filters:** Use a light tint of Ice Turquoise (`rgba(0, 163, 224, 0.1)`) for background and the full-strength color for text to indicate active filter states.
- **Navigation:** A vertical sidebar using the Primary Blue as the background, with active links highlighted by an Ice Turquoise vertical "glacier" bar on the left edge.