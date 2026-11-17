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

// Module-level state: every caller of useSidebar() shares the same ref.
const collapsed = ref(readStored())

watch(collapsed, (v) => {
  try { localStorage.setItem(STORAGE_KEY, String(v)) } catch (e) { /* ignore */ }
})

export function useSidebar() {
  const toggle = () => { collapsed.value = !collapsed.value }
  return { collapsed, toggle }
}
