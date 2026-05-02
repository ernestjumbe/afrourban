# COMPONENT_GUIDE

Use this format when implementing or documenting components.

## Component Template

For each component, capture:

1. Purpose
2. When to use
3. When not to use
4. Anatomy
5. Variants
6. Styling rules
7. Accessibility rules
8. Example file

---

## Page Shell

### Purpose

Provides the Design 4 page frame: gold trim, sticky nav, themed canvas, background pattern, and main content wrapper.

### When to use

- major landing pages
- index pages
- detail pages with editorial framing

### When not to use

- embedded widgets
- tiny in-page modules

### Anatomy

- gold trim strip
- sticky nav
- optional background pattern
- padded content container

### Variants

- dark default
- light alternate

### Styling rules

- keep top trim at `6px`
- use blurred translucent nav background
- use `max-w-[1400px]` style content shell

### Accessibility rules

- navigation must be keyboard reachable
- decorative SVG patterns must be `aria-hidden`

### Example file

- `examples/components/page-shell.tsx`

---

## Navigation

### Purpose

Primary site wayfinding and utility actions.

### When to use

- all full-page Design 4 views

### When not to use

- modal internals
- small panel headers

### Anatomy

- logo
- category links
- search trigger
- auth action
- theme toggle when page supports theme switching
- mobile menu trigger

### Variants

- desktop horizontal nav
- mobile drawer nav

### Styling rules

- labels are uppercase sans with tracking
- active item may use gold
- nav border remains subtle in both themes

### Accessibility rules

- clear button labels for search/menu
- focusable drawer controls

### Example file

- `examples/system/navigation.tsx`

---

## Search Overlay

### Purpose

Full-screen lightweight search entry.

### When to use

- global content search
- quick search entry across editorial pages

### When not to use

- dense filter forms
- inline local search fields

### Anatomy

- blurred backdrop
- close button
- oversized search input

### Variants

- dark
- light

### Styling rules

- keep chrome minimal
- use large type for the input
- rely on a single strong divider line or low-contrast field

### Accessibility rules

- dialog semantics
- escape closes
- autofocus input

### Example file

- `examples/components/search-overlay.tsx`

---

## Category Chip Rail

### Purpose

Lets users scan and filter content categories.

### When to use

- stories
- quizzes
- directory filtering

### When not to use

- primary navigation

### Anatomy

- horizontally wrapping pills
- active state
- optional count

### Variants

- category chips
- filter chips
- presence toggles

### Styling rules

- small pill radius or full pill
- terracotta accent is preferred for category identity
- inactive chips stay low contrast

### Accessibility rules

- selected state must be clear
- buttons must be keyboard reachable

### Example file

- `examples/components/category-chip-rail.tsx`

---

## Editorial Card

### Purpose

Reusable story, event, or directory preview surface.

### When to use

- content grids
- supporting content strips
- archive views

### When not to use

- dense data tables

### Anatomy

- media
- category or meta row
- headline
- short excerpt or supporting detail
- optional CTA or arrow icon

### Variants

- story card
- event card
- organization card

### Styling rules

- large radius
- soft border
- restrained overlay treatments
- serif for major headline, sans for metadata

### Accessibility rules

- entire card may be clickable, but preserve clear link target semantics
- images need useful alt text unless decorative

### Example file

- `examples/components/editorial-card.tsx`

---

## Directory Filters

### Purpose

Refine index results without turning the page into a dashboard.

### When to use

- directories
- searchable indexes

### When not to use

- forms unrelated to discovery

### Anatomy

- search field
- chip or segmented filters
- dropdown filters
- sort control
- pagination

### Variants

- inline filter row
- compact mobile stack

### Styling rules

- preserve editorial whitespace
- controls should look like curated tools, not admin UI

### Accessibility rules

- dropdown state must be obvious
- filters need clear text labels

### Example file

- `examples/components/directory-filters.tsx`

---

## Auth Form

### Purpose

Registration and login with editorial-brand framing.

### When to use

- login
- registration
- credential flows

### When not to use

- long settings forms

### Anatomy

- branded shell
- mode toggle
- labeled inputs
- validation hints
- primary CTA
- optional alternate auth actions

### Variants

- passphrase mode
- password mode

### Styling rules

- forms live inside large-radius cards or controlled content columns
- inputs stay minimal and calm
- primary CTA uses gold

### Accessibility rules

- labels remain visible
- error/help text should be associated to inputs
- reveal/hide password controls need accessible labels

### Example file

- `examples/components/auth-form.tsx`

---

## Long Settings Form

### Purpose

Profile and organization editing without losing brand tone.

### When to use

- account settings
- organization management

### When not to use

- quick auth flows

### Anatomy

- grouped sections
- labels and helper text
- media upload area
- toggles or checkboxes
- danger zone block

### Variants

- profile edit
- organization edit

### Styling rules

- separate groups with whitespace and subtle dividers
- avoid admin-dashboard density

### Accessibility rules

- every control needs a label
- destructive actions must be explicit

### Example file

- `examples/system/forms.tsx`

---

## Detail Hero

### Purpose

Lead section for story, event, profile, or organization detail pages.

### When to use

- page-opening feature context

### When not to use

- small section intros

### Anatomy

- hero media or banner
- title
- meta row
- supporting actions

### Variants

- editorial story hero
- event hero
- organization banner
- profile cover and avatar

### Styling rules

- strong image-to-text hierarchy
- serif heading when the page is narrative or editorial

### Accessibility rules

- action buttons must have readable contrast
- hero imagery should not obscure text

### Example file

- `examples/components/detail-hero.tsx`

---

## Agent Rule

Do not invent new component language if an existing pattern above fits the problem. Match the closest example file and keep changes inside the Design 4 vocabulary.