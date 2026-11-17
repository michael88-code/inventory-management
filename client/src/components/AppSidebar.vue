<template>
  <aside class="sidebar" :class="{ collapsed }" :aria-label="t('nav.mainNavigation')">
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
      :aria-label="toggleLabel"
      :title="collapsed ? toggleLabel : undefined"
      @click="toggle"
    >
      <svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path :d="collapsed ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'" />
      </svg>
      <span class="nav-label">{{ t('nav.collapseSidebar') }}</span>
    </button>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useSidebar } from '../composables/useSidebar'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  brandName: { type: String, required: true },
  brandSubtitle: { type: String, default: '' },
  // [{ to: '/', label: 'Overview', icon: '<path .../>', exact: true }, ...]
  items: { type: Array, required: true }
})

const { t } = useI18n()
const { collapsed, toggle } = useSidebar()
const brandInitial = computed(() => props.brandName.charAt(0).toUpperCase())
const toggleLabel = computed(() => (collapsed.value ? t('nav.expandSidebar') : t('nav.collapseSidebar')))
</script>
