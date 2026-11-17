---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - replaces a horizontal top nav bar with a collapsible vertical sidebar on the left, introduces a design-token system (spacing, color, radius, shadow, type scale), and applies consistent spacing and polish across every view. Use this skill whenever the user wants to modernize, restyle, refresh, or "make professional" a Vue app's layout or look, move navigation into a sidebar or side rail, make an app look like Linear/Stripe/Vercel-style dashboards, fix inconsistent spacing across pages, or do an app-wide visual overhaul of a Vue 3 / vue-router project - even if they don't say "SaaS" or "sidebar" explicitly.
---

# Vue 3 SaaS Redesign

Turn a Vue 3 app with a top navigation bar into a polished SaaS-style shell: a collapsible left sidebar, a slim top bar for page context and utilities, and a consistent token-driven spacing and color system applied to every view.

The goal is a visual and structural redesign, not a functional one. Every route, filter, modal, event, i18n string and data flow that worked before must still work afterwards. Users judge a redesign by what broke as much as by how it looks, so treat behavior preservation as the first requirement and aesthetics as the second.

## Workflow

Work through these phases in order. Each depends on what the previous one found.

### 1. Discover the app

Before changing anything, build a picture of how the app is put together. Read rather than guess, since Vue apps vary a lot in where layout lives.

- **Project rules**: read `CLAUDE.md` / `AGENTS.md` / README. Respect anything they say about who edits `.vue` files (some projects require delegating to a specific subagent), design constraints (e.g. "no emojis in UI", a fixed palette), and how to run the app.
- **Router**: find the routes (`router/index.js`, `main.js`, or wherever `createRouter` is called). List every route's path, name and the label it shows in the nav today. The sidebar must cover all of them.
- **Root layout**: usually `App.vue` or a `layouts/` component. Note the current header markup, everything in it besides links (logo, subtitle, language switcher, profile menu, search, notifications), and anything rendered between the header and `<router-view>` (filter bars, banners, breadcrumbs).
- **Global styles**: where the base CSS lives (`App.vue` unscoped `<style>`, `style.css`, `main.css`, Tailwind config), and whether CSS variables already exist. Note the existing palette and font so the redesign evolves the brand rather than replacing it.
- **Views**: skim each view in `views/` (or `pages/`) for its outer wrapper, page heading, card/panel classes, tables, and hard-coded spacing values. You are looking for the shared patterns you will normalize in phase 4.
- **i18n**: if nav labels use `t('...')`, the sidebar must use the same keys. Never hard-code a label that was translated before.
- **Styling approach**: plain CSS, SCSS, Tailwind, or a component library (Vuetify, PrimeVue, Element Plus, Naive UI). If a component library provides its own layout/drawer components, prefer configuring those over hand-building a parallel system - mixing two layout systems produces subtle spacing conflicts.

Summarize what you found (routes, header contents, style location, constraints) to the user in a few lines before editing. It catches misreadings early and costs little.

### 2. Establish design tokens

Add a single token block (CSS custom properties on `:root`) in the global stylesheet. Read `references/design-tokens.md` for the full recommended set and the reasoning behind each scale. In short:

- A **4px-based spacing scale** (`--space-1` … `--space-12`). Consistent spacing comes from only ever using values on the scale, not from picking "nice" numbers per component.
- **Neutral + accent color tokens** derived from the app's existing palette when it has one.
- **Radius, shadow, border, type scale, and layout tokens** (`--sidebar-width`, `--sidebar-width-collapsed`, `--topbar-height`, `--content-max-width`).

If the project already has variables, extend and rename carefully rather than duplicating them. If it uses Tailwind, put the tokens in `tailwind.config` `theme.extend` instead, and use utility classes.

### 3. Build the shell

Replace the top nav with a sidebar + main-column layout. Read `references/sidebar-shell.md` for a complete reference implementation (component, collapse logic, CSS). Adapt it to what discovery found rather than pasting it verbatim. The essentials:

- **`AppSidebar.vue`** component: brand at the top, one nav item per route (icon + label), collapse toggle at the bottom. Use `router-link`'s own active tracking (`isActive` / `isExactActive` from its scoped slot) rather than hand-rolled `$route.path ===` checks: prefix matching keeps a parent highlighted on nested routes, and exact matching for `/` keeps it from lighting up on every page.
- **Collapsible to an icon rail**: full width (~240px) ⇄ icon-only (~64px). Persist the choice in `localStorage` (wrapped in try/catch, since storage can throw in private mode). When collapsed, labels are visually hidden but still available to screen readers, and each item gets a `title` / `aria-label` so the icon is not the only cue.
- **Icons**: each nav item needs an icon or the collapsed rail is unusable. Use inline SVG (see `references/nav-icons.md` for a ready set) unless the project already depends on an icon library. Never use emojis as icons; they render inconsistently across platforms and read as unprofessional.
- **Top bar**: a slim bar (≈56-64px) at the top of the main column holding the current page title on the left and the utilities that used to live in the header (language switcher, profile menu, etc.) on the right. Move those components; don't rewrite them, and keep every prop and event binding intact.
- **Content area**: secondary bars that sat under the old header (e.g. a global filter bar) go at the top of the main column, below the top bar. `<router-view>` sits inside a padded, max-width content container.
- **Small screens**: below ~768px default to the collapsed rail so content keeps usable width. This keeps the layout working on narrow windows without a full drawer implementation.
- **Modals**: anything mounted at the root (modals, toasts) stays at the root, outside the sidebar/main grid, so their positioning and z-index are unaffected.

Remove the old header markup and its now-dead CSS. Leftover `.top-nav` rules are a common source of mystery spacing.

### 4. Consistency pass across views

This is what makes the result look designed rather than reskinned. For each view:

- Give every page the same header pattern: title (and optional subtitle/actions) with the same size, weight and bottom margin. If the top bar already shows the page title, avoid a duplicate large heading; keep in-page headings for sections.
- Normalize card/panel styling to the tokens: one background, one border, one radius, one shadow, one inner padding.
- Replace hard-coded spacing (`margin: 18px`, `padding: 1.3rem`) with the nearest token. Use the same gap between cards in every grid.
- Tables: consistent header style (small uppercase or medium-weight muted text), row height, cell padding, and a subtle row hover.
- Buttons, inputs and selects: one height, one radius, one focus ring.

Prefer editing shared/global classes over touching each view when the views already share class names. Only touch scoped styles where a view diverges. Keep diffs focused on styling and layout. Don't refactor script logic in the same change, because it makes regressions hard to spot.

Read `references/design-tokens.md` → "Polish checklist" for the details that separate polished from merely tidy (focus states, transitions, number alignment, empty states).

### 5. Verify in the browser

Run the app (use the project's documented start command or start skill) and check it, ideally with a browser automation tool and screenshots:

1. Every route is reachable from the sidebar and shows the correct active state, including `/`.
2. Collapse and expand work, the state survives a reload, and the collapsed rail shows tooltips/labels on hover.
3. Utilities moved to the top bar still work (open the profile menu, switch language and confirm the sidebar labels change too, open any modals).
4. Global filters still apply to the data.
5. At ~1440px and ~800px widths nothing overflows horizontally and the content isn't cramped.
6. The browser console shows no new errors or Vue warnings.
7. Run the project's existing frontend tests if any exist.

Take before/after screenshots of at least the main dashboard view and show them to the user. The visual comparison is how they'll judge the work.

## Things that commonly go wrong

- **Active state on `/` always lit**: use exact matching (`isExactActive`) for the root route.
- **Double scrollbars**: let the main column scroll (`overflow-y: auto` on the main area with the shell at `height: 100vh`), or let the document scroll with a `position: sticky` sidebar, but not both.
- **Sticky elements misaligned**: elements that used `position: sticky; top: 70px` relative to the old header need their offset updated to the new top bar height (use `var(--topbar-height)`).
- **Dropdowns clipped**: profile/language menus that were positioned relative to the old header can be clipped by `overflow: hidden` on the new top bar. Don't put `overflow: hidden` on containers that host dropdowns.
- **Lost translations**: sidebar labels hard-coded in English when the old nav used `t()`.
- **Text flash on collapse**: hide labels with opacity + width transitions, or `v-show`, rather than `v-if`, so items don't jump.
