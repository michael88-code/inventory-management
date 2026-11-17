# Design Tokens and Polish

## Contents
- Token block (CSS)
- Why these scales
- Adapting to an existing palette
- Polish checklist

## Token block

Put this on `:root` in the global stylesheet. Values are a neutral slate/blue baseline; replace the accent and neutrals with the app's existing brand colors if it has them.

```css
:root {
  /* Spacing: 4px base. Use only these values for margin, padding and gap. */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Neutrals */
  --color-bg: #f8fafc;          /* app background behind cards */
  --color-surface: #ffffff;     /* cards, sidebar, top bar */
  --color-surface-muted: #f1f5f9; /* hover fills, table headers */
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-secondary: #475569;
  --color-text-muted: #64748b;

  /* Accent */
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;
  --color-accent-soft: #eff6ff;  /* active nav item background */

  /* Status */
  --color-success: #16a34a;
  --color-info: #2563eb;
  --color-warning: #d97706;
  --color-danger: #dc2626;

  /* Radius */
  --radius-sm: 6px;   /* inputs, buttons, nav items */
  --radius-md: 8px;   /* cards */
  --radius-lg: 12px;  /* modals, large panels */

  /* Shadow: keep subtle; borders do most of the separation work */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.12);

  /* Type scale */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-xs: 0.75rem;   /* 12px: table headers, captions */
  --text-sm: 0.875rem;  /* 14px: body in dense UI, nav items */
  --text-base: 1rem;    /* 16px */
  --text-lg: 1.125rem;  /* 18px: card titles */
  --text-xl: 1.25rem;   /* 20px: page title in top bar */
  --text-2xl: 1.5rem;   /* 24px: KPI numbers */
  --text-3xl: 1.875rem; /* 30px: hero KPI numbers */

  /* Layout */
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 64px;
  --topbar-height: 60px;
  --content-max-width: 1440px;
  --content-padding: var(--space-8);

  /* Motion */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;

  /* Focus */
  --focus-ring: 0 0 0 3px rgba(37, 99, 235, 0.35);
}
```

## Why these scales

- **4px spacing base**: small enough for dense dashboards, and multiples line up visually. Inconsistent spacing is the most common reason a UI looks amateur, and the fix is restricting choices, not picking better one-off values.
- **Rhythm**: use `--space-6` (24px) as the default gap between cards and sections, `--space-5`/`--space-6` for card inner padding, `--space-2`/`--space-3` within compact components. Page padding `--space-8`.
- **Borders over shadows**: SaaS dashboards (Linear, Stripe, Vercel) separate surfaces mainly with 1px borders and very light shadows. Heavy shadows read as dated.
- **14px body in the shell**: nav items and table text at 14px look denser and more professional than 16px in data-heavy apps.

## Adapting to an existing palette

- If the app already uses a palette (e.g. slate grays with a blue accent), map its existing hex values to these token names instead of introducing new colors. The redesign should feel like the same product, refined.
- If the project documents design constraints (status colors, chart colors, "no emojis"), they win over these defaults.
- After adding tokens, replace hard-coded hex values in shared styles with tokens. You don't need to chase every value in every scoped style. Prioritize the shell, cards, tables, buttons and page headers.

## Polish checklist

- Visible keyboard focus on every interactive element (`:focus-visible { box-shadow: var(--focus-ring); outline: none; }`).
- Hover and active transitions of 150-200ms on nav items, buttons and table rows. No transitions on layout properties except the sidebar width.
- Numbers in tables and KPIs use `font-variant-numeric: tabular-nums` and are right-aligned in table columns.
- Muted secondary text (`--color-text-muted`) for labels, captions and metadata, so the primary values stand out.
- KPI cards: small muted label above, large semibold number, optional delta/status below; same height across a row.
- Table headers: `--text-xs`, uppercase or medium weight, `letter-spacing: 0.02em`, muted color, `--color-surface-muted` background.
- Status badges: soft tinted background + darker text of the same hue, `--radius-sm`, `--text-xs`, medium weight.
- Empty and loading states use the same card styling as filled states, so the layout doesn't jump.
- Consistent page structure: every view starts at the same vertical offset with the same heading treatment.
- `body` has an explicit background (`--color-bg`) and font (`--font-sans`) with `-webkit-font-smoothing: antialiased`.
