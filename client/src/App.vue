<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': collapsed }">
    <AppSidebar
      :brand-name="t('nav.companyName')"
      :brand-subtitle="t('nav.subtitle')"
      :items="navItems"
    />

    <div class="main-column">
      <header class="topbar">
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-actions">
          <LanguageSwitcher />
          <ProfileMenu
            @show-profile-details="showProfileDetails = true"
            @show-tasks="showTasks = true"
          />
        </div>
      </header>

      <FilterBar />

      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- Root-level modals stay outside the grid so their positioning is unaffected -->
    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppSidebar from './components/AppSidebar.vue'
import { navIcons } from './components/navIcons'
import { useSidebar } from './composables/useSidebar'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    AppSidebar
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const { collapsed } = useSidebar()

    // Computed so labels re-evaluate when the locale changes
    const navItems = computed(() => [
      { to: '/', label: t('nav.overview'), icon: navIcons.dashboard, exact: true },
      { to: '/inventory', label: t('nav.inventory'), icon: navIcons.inventory },
      { to: '/orders', label: t('nav.orders'), icon: navIcons.orders },
      { to: '/spending', label: t('nav.finance'), icon: navIcons.finance },
      { to: '/demand', label: t('nav.demandForecast'), icon: navIcons.forecast },
      { to: '/restocking', label: t('nav.restocking'), icon: navIcons.restock },
      { to: '/reports', label: t('nav.reports'), icon: navIcons.reports }
    ])

    // Top bar title: label of the nav item matching the current route (exact for '/', prefix otherwise)
    const currentTitle = computed(() => {
      const match = navItems.value.find(i =>
        i.exact ? route.path === i.to : route.path === i.to || route.path.startsWith(i.to + '/')
      )
      return match ? match.label : t('nav.companyName')
    })
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      collapsed,
      navItems,
      currentTitle,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
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

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  font-size: var(--text-sm);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

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
  /* above FilterBar (90) so top bar dropdowns are not covered by it */
  z-index: 100;
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

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-1);
  letter-spacing: -0.01em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

/* The top bar already shows the page title as the h1. A lone h2 (no description) would
   only repeat it, so keep it for screen readers and hide it visually. */
.page-header h2:only-child {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.stat-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.625rem;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: #ea580c;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.danger .stat-value {
  color: #dc2626;
}

.stat-card.info .stat-value {
  color: #2563eb;
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-surface-muted);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-3);
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-3);
  font-variant-numeric: tabular-nums;
  border-top: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--color-bg);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.badge.increasing {
  background: #d1fae5;
  color: #065f46;
}

.badge.decreasing {
  background: #fecaca;
  color: #991b1b;
}

.badge.stable {
  background: #e0e7ff;
  color: #3730a3;
}

.badge.high {
  background: #fecaca;
  color: #991b1b;
}

.badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
  font-size: 0.938rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: 0.938rem;
}
</style>
