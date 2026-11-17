# Sidebar Shell Reference Implementation

A complete, dependency-free shell for Vue 3 + vue-router. Adapt names, i18n calls and the list of utilities to the app; don't paste blindly.

## Contents
- Collapse state composable
- AppSidebar.vue
- Root layout (App.vue)
- Shell CSS

## Collapse state composable

`composables/useSidebar.js`. Module-level state means every component that calls `useSidebar()` shares the same ref.

```js
import { ref, watch } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'
const MOBILE_BREAKPOINT = 768

function readStored() {
  // Storage can throw (private mode, blocked site data), so fall back to the default.
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v !== null) return v === 'true'
  } catch (e) { /* ignore */ }
  // No saved preference: start collapsed on narrow screens so content keeps its width.
  return typeof window !== 'undefined' && window.innerWidth < MOBILE_BREAKPOINT
}

const collapsed = ref(readStored())

watch(collapsed, (v) => {
  try { localStorage.setItem(STORAGE_KEY, String(v)) } catch (e) { /* ignore */ }
})

export function useSidebar() {
  const toggle = () => { collapsed.value = !collapsed.value }
  return { collapsed, toggle }
}
```

## AppSidebar.vue

Drive the nav from an array so the template stays small and every route is covered. Use the app's own i18n keys for labels.

```vue
<template>
  <aside class="sidebar" :class="{ collapsed }" aria-label="Main navigation">
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true">{{ brandInitial }}</div>
      <div class="brand-text">
        <span class="brand-name">{{ brandName }}</span>
        <span v-if="brandSubtitle" class="brand-subtitle">{{ brandSubtitle }}</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <!-- custom slot so each item can choose exact vs prefix matching for its active state -->
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        custom
        v-slot="{ href, navigate, isActive, isExactActive }"
      >
        <a
          :href="href"
          class="nav-item"
          :class="{ 'is-active': item.exact ? isExactActive : isActive }"
          :aria-current="(item.exact ? isExactActive : isActive) ? 'page' : undefined"
          :title="collapsed ? item.label : undefined"
          :aria-label="collapsed ? item.label : undefined"
          @click="navigate"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true" v-html="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
        </a>
      </router-link>
    </nav>

    <button
      type="button"
      class="sidebar-toggle"
      :aria-expanded="!collapsed"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      @click="toggle"
    >
      <svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path :d="collapsed ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'" />
      </svg>
      <span class="nav-label">Collapse</span>
    </button>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useSidebar } from '../composables/useSidebar'

const props = defineProps({
  brandName: { type: String, required: true },
  brandSubtitle: { type: String, default: '' },
  // [{ to: '/', label: 'Overview', icon: '<path .../>', exact: true }, ...]
  items: { type: Array, required: true }
})

const { collapsed, toggle } = useSidebar()
const brandInitial = computed(() => props.brandName.charAt(0).toUpperCase())
</script>
```

Notes:
- `v-html` on the `<svg>` is safe here only because icon markup comes from static constants in the codebase, never from user or API data.
- The "Collapse" label and toggle aria-labels are English placeholders: route them through the app's i18n if it has one.
- `exact: true` for `/`; every other item uses prefix matching so nested routes (e.g. `/orders/123`) keep their parent highlighted.
- Labels stay in the DOM when collapsed (hidden with CSS), so screen readers still read them.

## Root layout (App.vue)

```vue
<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': collapsed }">
    <AppSidebar :brand-name="t('nav.companyName')" :brand-subtitle="t('nav.subtitle')" :items="navItems" />

    <div class="main-column">
      <header class="topbar">
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-actions">
          <!-- Utilities moved from the old header, bindings unchanged -->
          <LanguageSwitcher />
          <ProfileMenu @show-profile-details="showProfileDetails = true" @show-tasks="showTasks = true" />
        </div>
      </header>

      <!-- Anything that sat between the old header and router-view -->
      <FilterBar />

      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- Root-level modals stay here, outside the grid -->
  </div>
</template>
```

Build `navItems` as a `computed` so labels re-evaluate when the locale changes. Derive `currentTitle` from the nav item matching `route.path` (or from `route.meta.title` if routes define it).

## Shell CSS

Global (unscoped) so the grid applies to the root.

```css
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
  transition: grid-template-columns var(--transition-base);
}
.app-shell.sidebar-collapsed {
  grid-template-columns: var(--sidebar-width-collapsed) 1fr;
}

/* Sidebar sticks while the document scrolls: one scrollbar, no nested scrolling. */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: var(--space-4) var(--space-3);
  overflow: hidden; /* safe: the sidebar hosts no dropdowns */
  z-index: 50;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-1) var(--space-1) var(--space-6);
  min-height: 40px;
}
.brand-mark {
  flex: 0 0 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: var(--text-sm);
}
.brand-text { display: flex; flex-direction: column; min-width: 0; }
.brand-name { font-weight: 600; font-size: var(--text-sm); color: var(--color-text); white-space: nowrap; }
.brand-subtitle { font-size: var(--text-xs); color: var(--color-text-muted); white-space: nowrap; }

.sidebar-nav { display: flex; flex-direction: column; gap: var(--space-1); flex: 1; }

.nav-item,
.sidebar-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 36px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: background var(--transition-fast), color var(--transition-fast);
}
.nav-item:hover,
.sidebar-toggle:hover { background: var(--color-surface-muted); color: var(--color-text); }
.nav-item.is-active { background: var(--color-accent-soft); color: var(--color-accent); }

.sidebar-toggle {
  border: none;
  background: none;
  cursor: pointer;
  font: inherit;
  margin-top: var(--space-2);
}

.nav-icon {
  flex: 0 0 20px;
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.75;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Collapsed: hide text without removing it, so screen readers keep it and items don't jump. */
.nav-label,
.brand-text { transition: opacity var(--transition-fast); }
.sidebar.collapsed .nav-label,
.sidebar.collapsed .brand-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}
.sidebar.collapsed .nav-item,
.sidebar.collapsed .sidebar-toggle { justify-content: center; padding: 0; gap: 0; }
.sidebar.collapsed .sidebar-brand { justify-content: center; padding-left: 0; padding-right: 0; gap: 0; }

.main-column { min-width: 0; display: flex; flex-direction: column; }

.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: 0 var(--content-padding);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--color-border);
  /* No overflow:hidden here: profile/language dropdowns must escape the bar. */
}
.topbar-title { font-size: var(--text-xl); font-weight: 600; color: var(--color-text); letter-spacing: -0.01em; }
.topbar-actions { display: flex; align-items: center; gap: var(--space-3); }

.content {
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--content-padding) var(--space-12);
}

@media (max-width: 768px) {
  :root { --content-padding: var(--space-4); }
}
```

If a filter bar or other secondary bar was `position: sticky` under the old header, set its `top` to `var(--topbar-height)` so it docks under the new top bar.
