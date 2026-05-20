---
version: alpha
name: Zocdoc Clear Light
description: A friendly, high-trust healthcare marketplace system with bright accent color, soft cards, and minimal chrome.
colors:
  primary: "#fff04b"
  secondary: "#333333"
  tertiary: "#ffffff"
  neutral: "#f7f8f9"
  surface: "#ffffff"
  on-surface: "#333333"
  error: "#d64545"
typography:
  headline-display:
    fontFamily: "Sharp Sans Medium, fallback-font, Arial, sans-serif"
    fontSize: 44px
    fontWeight: 400
    lineHeight: 60px
    letterSpacing: 0px
  headline-lg:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 34px
    fontWeight: 400
    lineHeight: 41px
    letterSpacing: 0px
  headline-md:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 27px
    fontWeight: 400
    lineHeight: 32px
    letterSpacing: 0px
  headline-sm:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 21px
    fontWeight: 400
    lineHeight: 24px
    letterSpacing: 0px
  body-lg:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 26px
    letterSpacing: 0px
  body-md:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 26px
    letterSpacing: 0px
  body-sm:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 22px
    letterSpacing: 0px
  label-lg:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
    letterSpacing: 0px
  label-md:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
    letterSpacing: 0px
  label-sm:
    fontFamily: "Sharp Sans Medium, fallback-font, Arial, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 16px
    letterSpacing: 0px
  button-md:
    fontFamily: "Sharp Sans Semibold, fallback-font, Arial, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
    letterSpacing: 0px
  caption:
    fontFamily: "Sharp Sans Medium, fallback-font, Arial, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 16px
    letterSpacing: 0px
rounded:
  none: 0px
  sm: 4px
  md: 5px
  lg: 8px
  xl: 12px
  full: 9999px
spacing:
  xs: 2px
  sm: 10px
  md: 20px
  lg: 24px
  xl: 40px
  base: 16px
  gutter: 24px
  section: 40px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.secondary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
    size: "352px"
    height: "48px"
  button-primary-hover:
    backgroundColor: "#ffe92c"
    textColor: "{colors.secondary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
    size: "352px"
    height: "48px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.secondary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
    size: "352px"
    height: "48px"
  button-link:
    backgroundColor: "transparent"
    textColor: "{colors.secondary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.none}"
    padding: "0px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "20px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
  search-bar:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  topbar:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.tertiary}"
    typography: "{typography.label-sm}"
    height: "36px"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.secondary}"
    typography: "{typography.label-md}"
    padding: "0px"
  promo-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.sm}"
    padding: "20px"
---

# Zocdoc Clear Light

## Overview
Zocdoc’s visual system feels approachable, trustworthy, and lightly playful, which fits a healthcare search experience where clarity matters more than spectacle. The interface is spacious and airy, with a warm off-white background, a bright yellow accent, and restrained text styling that keeps the experience calm. It targets broad consumer audiences who need quick, low-friction decisions, so the design favors legibility, familiar controls, and gentle hierarchy.

## Colors
- **Primary (#fff04b):** A bright sunflower yellow used for the main brand accent, especially primary CTAs like the “Find care” button and logo mark. It signals action and optimism without feeling aggressive.
- **Secondary (#333333):** The deep charcoal text color used for headlines, body copy, icons, and outlined controls. It provides strong contrast while staying softer than pure black.
- **Tertiary (#ffffff):** Pure white used for cards, inputs, and surface elements that need to sit cleanly above the light background.
- **Neutral (#f7f8f9):** The pale site background, creating a soft paper-like canvas that makes content blocks and white cards feel elevated.
- **Surface (#ffffff):** The default card and field surface color. It supports a clean, clinical feel that works well for healthcare browsing.
- **On-surface (#333333):** The default text color on white surfaces, matching the main charcoal tone for consistent readability.
- **Error (#d64545):** A reserved alert color for validation and destructive states. It is not prominent in the screenshot, so it should be used sparingly.

## Typography
The system uses Sharp Sans as the core voice, with Medium and Semibold styles providing a polished, modern, slightly rounded personality. Headlines are large and highly legible, with no visible letter-spacing tricks and comfortable line heights that support scanning. Body text remains similarly weighty and clean, which makes the interface feel sturdy and accessible rather than ultra-minimal.

- **Headline-display / headline-lg / headline-md / headline-sm:** Use Sharp Sans for large marketing and page-intro messages. The visual rhythm is generous and editorial, but not decorative.
- **Body-lg / body-md:** Use for descriptions, supporting copy, and form text. The line height should stay open and readable in dense search flows.
- **Body-sm / label-lg / label-md / label-sm:** Use for utility labels, nav items, and helper text. These levels keep the interface concise while preserving readability.
- **Button-md / caption:** Use for controls and top-bar utility text. Uppercase styling is not a visible pattern; text should stay in sentence case with minimal letter spacing.

## Layout
The layout is built around a wide, responsive desktop canvas with clear sectional separation rather than a rigid boxed layout. Content tends to align to left edges with large horizontal breathing room, while interactive modules like the search bar and doctor cards sit in neat rows. Spacing follows a soft modular rhythm based on 2px, 10px, 20px, 24px, and 40px increments, which keeps the page feeling tidy without becoming overly segmented.

Primary sections should use generous vertical padding, especially around hero content and card carousels. Inputs and cards prefer compact internal padding, with 20px card padding and 16px/20px button padding giving controls a substantial but efficient footprint. The search module benefits from long, horizontal proportions, while smaller navigation and insurance tiles use tighter, evenly spaced grid treatment.

## Elevation & Depth
Depth is intentionally subtle. Instead of dramatic shadows, the system relies on white surfaces against a pale neutral background, with a delicate 1px shadow/border treatment on cards to imply layering. This creates a calm, trustworthy interface appropriate for healthcare and keeps the focus on content rather than decoration.

Use tonal contrast and thin borders to separate interactive regions. Shadows should remain minimal and soft; surfaces should never feel heavy or glossy. When emphasis is needed, prefer color and placement, especially the yellow CTA accent, over stronger elevation effects.

## Shapes
The shape language is restrained and friendly, with small radii that soften the interface without making it feel toy-like. Buttons use a 4px radius, cards sit at 5px, and inputs remain similarly compact. Overall, the system communicates precision and approachability through modest rounding rather than pill-shaped or heavily ornamental forms.

## Components
**Buttons:** Primary actions use `button-primary` with a yellow fill, dark text, 4px radius, and a compact 48px height. Secondary actions use `button-secondary`, which is outlined and transparent, keeping the same size and padding for parity. Link-style actions use `button-link` with no border or fill and underlined text for low-emphasis navigation.

Primary buttons should feel substantial, with at least 16px vertical padding and strong width treatment when used in search modules. Hover states may slightly deepen or warm the yellow, but should not change the overall tone. Disabled states should reduce contrast rather than introducing new colors.

**Cards:** Use `card` for content blocks such as insurance logos, doctor results, and promotion modules. Cards are white, lightly outlined by shadow, and padded by 20px. They should maintain clean alignment and consistent spacing between title, body copy, and action rows.

**Inputs and search fields:** Use `input` and `search-bar` for the main search experience. Fields should be white, bordered only by subtle separation, with 16px/20px padding and compact internal labels. The main search bar works best as a single horizontal row with segmented areas and a clearly distinguished action button.

**Chips and insurance tiles:** Use `chip` for compact selectable items and `card` for larger insurer tiles. These should remain low-chroma and rectangular, emphasizing recognition and scannability over ornament.

**Navigation and utility text:** Use `topbar` and `nav-link` for the header and global controls. The top bar is dark with light text, while the main nav stays minimal and text-led. Dropdown indicators and small utility labels should remain understated.

## Do's and Don'ts
- Do keep the interface bright, calm, and trust-oriented with a strong yellow accent.
- Do use Sharp Sans consistently for both headings and body text to preserve the brand’s unified voice.
- Do favor soft white surfaces, subtle borders, and gentle shadows instead of deep elevation.
- Do keep buttons rectangular with small radii and clear padding; preserve the 48px minimum height.
- Don't introduce saturated secondary colors that compete with the primary yellow.
- Don't use heavy shadows, large corner radii, or glassy effects.
- Don't over-tighten spacing; the design depends on breathable whitespace and clear section separation.
- Don't switch to highly condensed, overly decorative, or uppercase-heavy typography.