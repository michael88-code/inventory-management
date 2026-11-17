<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="candidates.length === 0" class="card empty-state">
      {{ t('restocking.noCandidates') }}
    </div>
    <div v-else>
      <div class="card budget-card">
        <div class="budget-header">
          <label for="budget-slider" class="budget-label">{{ t('restocking.budget') }}</label>
          <span class="budget-value">{{ money(budget) }}</span>
        </div>
        <input
          id="budget-slider"
          v-model.number="budget"
          type="range"
          class="budget-slider"
          min="0"
          :max="maxBudget"
          :step="budgetStep"
          :style="{ '--fill': budgetFillPercent + '%' }"
        />
        <div class="budget-scale">
          <span>{{ money(0) }}</span>
          <span>{{ money(maxBudget) }}</span>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.recommendedTotal') }}</div>
          <div class="stat-value">{{ money(recommendedTotal) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ money(remainingBudget) }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.leadTime') }}</div>
          <div class="stat-value">
            {{ orderLines.length ? t('restocking.leadTimeDays', { days: orderLeadTime }) : '—' }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ orderLines.length }}/{{ candidates.length }})</h3>
        </div>
        <p class="how-it-works">{{ t('restocking.howItWorks') }}</p>
        <div class="table-container">
          <table class="restock-table">
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.demandGap') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in recommendations"
                :key="row.sku"
                :class="{ unfunded: row.quantity === 0 }"
              >
                <td><strong>{{ row.sku }}</strong></td>
                <td>{{ translateProductName(row.name) }}</td>
                <td><span :class="['badge', row.trend]">{{ t(`trends.${row.trend}`) }}</span></td>
                <td class="num">{{ row.gap.toLocaleString() }}</td>
                <td class="num">
                  <template v-if="row.quantity === 0">
                    <span class="muted">{{ t('restocking.notFunded') }}</span>
                  </template>
                  <template v-else>
                    <strong>{{ row.quantity.toLocaleString() }}</strong>
                    <span v-if="row.quantity < row.gap" class="badge warning partial">{{ t('restocking.partial') }}</span>
                  </template>
                </td>
                <td class="num">{{ moneyExact(row.unitCost) }}</td>
                <td class="num">{{ row.quantity ? moneyExact(row.lineTotal) : '—' }}</td>
                <td class="num">{{ t('restocking.leadTimeDays', { days: row.leadTimeDays }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="order-actions">
          <div class="order-feedback">
            <span v-if="submitError" class="feedback error-text">{{ t('restocking.orderFailed') }}: {{ submitError }}</span>
            <span v-else-if="lastOrder" class="feedback success-text">
              {{ t('restocking.orderPlaced', { number: lastOrder.order_number, days: lastOrder.lead_time_days }) }}
              <router-link to="/orders">{{ t('restocking.viewInOrders') }}</router-link>
            </span>
            <span v-else-if="orderLines.length === 0" class="feedback muted">{{ t('restocking.nothingToOrder') }}</span>
          </div>
          <button
            type="button"
            class="place-order-btn"
            :disabled="orderLines.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

// Funding order: growing demand first, then flat, then shrinking.
const TREND_RANK = { increasing: 0, stable: 1, decreasing: 2 }

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)
    const submitting = ref(false)
    const submitError = ref(null)
    const lastOrder = ref(null)

    const money = (amount) => formatCurrency(amount, currentCurrency.value)
    const moneyExact = (amount) => formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

    // Items worth restocking: only those whose forecast exceeds current demand.
    // The gap (forecast minus current) is the most we would ever order.
    const candidates = computed(() => {
      return forecasts.value
        .map(f => ({
          sku: f.item_sku,
          name: f.item_name,
          trend: f.trend,
          gap: f.forecasted_demand - f.current_demand,
          growth: (f.forecasted_demand - f.current_demand) / f.current_demand,
          unitCost: f.unit_cost,
          leadTimeDays: f.lead_time_days
        }))
        .filter(c => c.gap > 0)
        .sort((a, b) =>
          (TREND_RANK[a.trend] ?? 3) - (TREND_RANK[b.trend] ?? 3) ||
          b.gap - a.gap ||
          b.growth - a.growth
        )
    })

    // Cost of covering every gap in full: the top of the slider.
    const fullCost = computed(() =>
      candidates.value.reduce((sum, c) => sum + c.gap * c.unitCost, 0)
    )
    const budgetStep = 50
    const maxBudget = computed(() => Math.max(budgetStep, Math.ceil(fullCost.value / 500) * 500))
    const budgetFillPercent = computed(() => (budget.value / maxBudget.value) * 100)

    // Greedy fill in priority order. When an item doesn't fully fit, it gets as
    // many units as the remaining budget allows, and the loop keeps going so
    // cheaper lower-priority items can still use what's left.
    // Math is done in whole cents to avoid floating-point drift (e.g. 0.1 + 0.2).
    const recommendations = computed(() => {
      let remainingCents = Math.round(budget.value * 100)
      return candidates.value.map(c => {
        const unitCents = Math.round(c.unitCost * 100)
        const quantity = Math.min(c.gap, Math.floor(remainingCents / unitCents))
        remainingCents -= quantity * unitCents
        return { ...c, quantity, lineTotal: (quantity * unitCents) / 100 }
      })
    })

    const orderLines = computed(() => recommendations.value.filter(r => r.quantity > 0))
    const recommendedTotal = computed(() =>
      orderLines.value.reduce((sum, r) => sum + r.lineTotal, 0)
    )
    const remainingBudget = computed(() => Math.max(0, budget.value - recommendedTotal.value))
    // Matches the backend rule: the order arrives when its slowest item does.
    const orderLeadTime = computed(() =>
      orderLines.value.reduce((max, r) => Math.max(max, r.leadTimeDays), 0)
    )

    // Clear the last result once the user starts planning a different order.
    watch(budget, () => {
      submitError.value = null
      lastOrder.value = null
    })

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        // Start halfway so the first view shows both funded and unfunded items.
        budget.value = Math.round(maxBudget.value / 2 / budgetStep) * budgetStep
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
        console.error('Load error:', err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (orderLines.value.length === 0 || submitting.value) return
      try {
        submitting.value = true
        submitError.value = null
        const order = await api.createRestockOrder({
          budget: budget.value,
          items: orderLines.value.map(r => ({ sku: r.sku, quantity: r.quantity }))
        })
        lastOrder.value = order
      } catch (err) {
        submitError.value = err.response?.data?.detail || err.message
        console.error('Place order error:', err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      translateProductName,
      loading,
      error,
      budget,
      budgetStep,
      maxBudget,
      budgetFillPercent,
      candidates,
      recommendations,
      orderLines,
      recommendedTotal,
      remainingBudget,
      orderLeadTime,
      submitting,
      submitError,
      lastOrder,
      placeOrder,
      money,
      moneyExact
    }
  }
}
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.5rem;
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.budget-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  width: 100%;
  height: 6px;
  appearance: none;
  -webkit-appearance: none;
  border-radius: 999px;
  background: linear-gradient(to right, #3b82f6 var(--fill), #e2e8f0 var(--fill));
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #3b82f6;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #3b82f6;
}

.budget-slider:focus-visible {
  outline: 2px solid #93c5fd;
  outline-offset: 4px;
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.813rem;
  color: #64748b;
}

.how-it-works {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #64748b;
}

.restock-table .num {
  text-align: right;
  white-space: nowrap;
}

.restock-table tr.unfunded td {
  color: #94a3b8;
}

.partial {
  margin-left: 0.5rem;
}

.muted {
  color: #94a3b8;
}

.empty-state {
  color: #64748b;
  text-align: center;
  padding: 2rem;
}

.order-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
}

.feedback {
  font-size: 0.875rem;
}

.success-text {
  color: #15803d;
}

.success-text a {
  margin-left: 0.5rem;
  color: #2563eb;
  font-weight: 600;
}

.error-text {
  color: #dc2626;
}

.place-order-btn {
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.place-order-btn:hover:not(:disabled) {
  background: #1e293b;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}
</style>
