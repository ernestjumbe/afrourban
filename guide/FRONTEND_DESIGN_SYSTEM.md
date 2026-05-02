# FRONTEND_DESIGN_SYSTEM

## Purpose

Minimal source of truth for implementing AfroUrban Design 4 in related projects.

## Design Summary

- dark-first editorial interface
- Scandinavian restraint plus African geometric identity
- serif-led storytelling
- uppercase tracked sans for navigation, chips, and labels
- gold for primary action
- terracotta for category identity
- large-radius cards, soft borders, restrained motion

## Theme Rules

- Default to dark.
- Light mode keeps the same structure and hierarchy.
- Do not redesign components between themes.
- Dark surfaces use near-black plus low-contrast white overlays.
- Light surfaces use white or off-white plus subtle dark borders.

## Core Tokens

### Colors

| Token | Value | Use |
| --- | --- | --- |
| `--color-white` | `#ffffff` | light surface |
| `--color-black` | `#1a1a1a` | primary text, dark base |
| `--color-off-white` | `#f5f5f5` | secondary light surface |
| `--color-mid-gray` | `#757575` | muted text |
| `--color-light-gray` | `#999999` | tertiary text |
| `--color-gold` | `#d4a017` | primary action, trim |
| `--color-gold-light` | `#f5a623` | hover accent |
| `--color-terracotta` | `#c65d3e` | chips, category accents |
| `--color-terracotta-dark` | `#a14b2f` | terracotta hover |
| `--color-divider` | `#e0e0e0` | light borders |
| `--color-dark-bg` | `#1a1a1a` | dark canvas |
| `--color-dark-surface` | `#2a2a2a` | elevated dark surface |
| `--color-dark-divider` | `#3d3d3d` | dark borders |
| `--color-pattern-cream` | `#f5e6d0` | pattern fill |
| `--bg-overlay` | `rgba(0,0,0,0.45)` | image overlay |
| `--bg-tag` | `rgba(196,93,62,0.1)` | chip background |

### Spacing

4px base scale.

| Token | Value |
| --- | --- |
| `--space-micro` | `4px` |
| `--space-xs` | `8px` |
| `--space-sm` | `12px` |
| `--space-md` | `16px` |
| `--space-default` | `20px` |
| `--space-lg` | `24px` |
| `--space-xl` | `32px` |
| `--space-2xl` | `40px` |
| `--space-3xl` | `48px` |
| `--space-4xl` | `64px` |

Rules:

- Prefer whitespace before borders.
- Desktop content width commonly caps near `1400px`.
- Page shells use generous horizontal padding.

## Typography

- Wordmark and labels: condensed or clean sans, uppercase, tracked.
- H1/H2: serif, bold, tight line-height.
- Body: humanist sans, calm and readable.
- Metadata: small sans, subdued contrast.

## Layout Vocabulary

### Gold Trim

- Thin gold strip at page top.
- Typical height: `6px`.
- Optional subtle geometric overlay.

### Sticky Nav

- translucent background
- backdrop blur
- thin bottom border
- logo left, utilities right
- desktop category row
- mobile side drawer

### Pattern Usage

- Use geometric African-inspired pattern in heroes, edge trims, or very low-contrast background fields.
- Use diamonds, chevrons, triangles, woven rhythms.
- Never place loud pattern behind long-form body copy.

### Surfaces

- Border radius usually `20px` to `24px`.
- Borders stay subtle.
- Dark cards often use translucent white on black.
- Light cards stay white or off-white.

## Motion

- short, understated transitions
- fades, slide-ins, small translate shifts
- no bounce, no playful overshoot

## Implementation Rules

- Keep dark-first default.
- Reuse token names exactly when possible.
- Use serif for narrative emphasis, sans for interface structure.
- Gold is for primary action.
- Terracotta is for category identity.
- Mobile layouts should feel composed, not just stacked.

## Avoid

- generic SaaS visual language
- bright blue primary accents
- heavy shadows
- neon gradients
- dense dashboard composition
- decorative pattern behind readable paragraphs