<template>
  <section class="app-page dashboard-screen flex flex-col gap-3">
    <section v-if="isLoading" class="dashboard-loading-state">
      <ProgressSpinner stroke-width="4" />
    </section>

    <template v-else-if="summary">
      <div class="dashboard-grid">
        <section class="dashboard-kpis-row">
          <article v-for="card in kpiCards" :key="card.title" class="dashboard-kpi-card">
            <div class="dashboard-kpi-head">
              <span class="dashboard-kpi-icon" :class="card.iconTone">
                <i :class="card.icon"></i>
              </span>
              <span class="dashboard-kpi-label">{{ card.title }}</span>
            </div>

            <strong class="dashboard-kpi-value">{{ card.value }}</strong>

            <div class="dashboard-kpi-foot" :class="card.deltaTone">
              <i :class="card.deltaIcon"></i>
              <span>{{ card.deltaLabel }}</span>
              <span class="dashboard-kpi-foot-muted">vs ontem</span>
            </div>
          </article>
        </section>

        <section class="dashboard-panel dashboard-cash-panel lg:col-span-6">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Situacao do caixa</div>
              <h2 class="dashboard-panel-title">Fechamento e conferencia</h2>
            </div>
            <Tag :value="cashStatus.label" :severity="cashStatus.severity" rounded />
          </div>

          <div class="dashboard-cash-stats">
            <div class="dashboard-cash-item">
              <span class="dashboard-mini-label">Esperado</span>
              <strong class="dashboard-cash-value">{{ formatCurrency(cashSummary.expected) }}</strong>
            </div>

            <div class="dashboard-cash-item">
              <span class="dashboard-mini-label">Contado</span>
              <strong class="dashboard-cash-value">{{ formatNullableCurrency(cashSummary.counted) }}</strong>
            </div>

            <div class="dashboard-cash-item">
              <span class="dashboard-mini-label">Diferenca</span>
              <strong class="dashboard-cash-value" :class="cashStatus.textClass">{{ formatNullableCurrency(cashSummary.difference) }}</strong>
            </div>

            <div class="dashboard-cash-item dashboard-cash-status-box">
              <span class="dashboard-mini-label">Status</span>
              <Tag :value="cashStatus.label" :severity="cashStatus.severity" rounded />
              <span class="dashboard-cash-caption">{{ cashStatus.caption }}</span>
            </div>
          </div>

          <div class="dashboard-cash-progress-shell">
            <ProgressBar :value="cashBalanceProgress" :show-value="false" :class="cashStatus.progressClass" />
          </div>

          <div class="dashboard-cash-bottom">
            <div class="dashboard-meta-inline">
              <i class="pi pi-clock"></i>
              <span>{{ cashTimestampLabel }}</span>
            </div>

            <Button label="Ver fechamento" size="small" severity="secondary" outlined @click="router.push('/relatorios')" />
          </div>
        </section>

        <section class="dashboard-panel dashboard-highlights-panel lg:col-span-6">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Destaques de hoje</div>
              <h2 class="dashboard-panel-title">Leitura comercial imediata</h2>
            </div>
          </div>

          <div class="dashboard-highlights-grid">
            <article v-for="item in highlightCards" :key="item.title" class="dashboard-highlight-card">
              <span class="dashboard-highlight-icon" :class="item.iconTone">
                <i :class="item.icon"></i>
              </span>

              <div class="min-w-0">
                <div class="dashboard-mini-label">{{ item.title }}</div>
                <strong class="dashboard-highlight-title">{{ item.value }}</strong>
                <div class="dashboard-highlight-subtitle">{{ item.meta }}</div>
              </div>
            </article>
          </div>
        </section>

        <section class="dashboard-panel dashboard-chart-panel lg:col-span-6">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Vendas por hora</div>
              <h2 class="dashboard-panel-title">Hoje</h2>
            </div>
            <span class="dashboard-note-chip">{{ strongestHour.value }}</span>
          </div>

          <div class="dashboard-chart-shell dashboard-chart-shell-bar">
            <Chart v-if="hasHourlySales" type="bar" :data="hourlyChartData" :options="hourlyChartOptions" class="dashboard-chart" />
            <div v-else class="dashboard-chart-empty">Nenhuma venda registrada hoje.</div>
          </div>
        </section>

        <section class="dashboard-panel dashboard-chart-panel lg:col-span-6">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Receita dos ultimos 7 dias</div>
              <h2 class="dashboard-panel-title">Tendencia recente</h2>
            </div>
            <span class="dashboard-note-chip" :class="salesTrend.toneClass">{{ salesTrend.label }}</span>
          </div>

          <div class="dashboard-chart-shell dashboard-chart-shell-line">
            <Chart type="line" :data="weeklyRevenueChartData" :options="weeklyRevenueChartOptions" class="dashboard-chart" />
          </div>
        </section>

        <section class="dashboard-panel dashboard-alerts-panel lg:col-span-6">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Alertas e observacoes</div>
              <h2 class="dashboard-panel-title">O que precisa de atencao</h2>
            </div>
          </div>

          <div class="dashboard-alert-list">
            <article v-for="alert in alerts" :key="alert.title" class="dashboard-alert-card" :class="alert.cardClass">
              <span class="dashboard-alert-icon" :class="alert.iconTone">
                <i :class="alert.icon"></i>
              </span>

              <div class="min-w-0 flex-1">
                <div class="dashboard-alert-head">
                  <strong class="dashboard-alert-title">{{ alert.title }}</strong>
                  <Tag :value="alert.badge" :severity="alert.severity" rounded />
                </div>
                <p class="dashboard-alert-text">{{ alert.text }}</p>
              </div>
            </article>
          </div>
        </section>

        <section class="dashboard-panel dashboard-summary-panel lg:col-span-3">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Resumo rapido</div>
              <h2 class="dashboard-panel-title">Fechamento do dia</h2>
            </div>
          </div>

          <div class="dashboard-summary-list">
            <div v-for="item in quickSummaryItems" :key="item.label" class="dashboard-summary-row">
              <span class="dashboard-summary-label">{{ item.label }}</span>
              <strong class="dashboard-summary-value" :class="item.toneClass">{{ item.value }}</strong>
            </div>
          </div>
        </section>

        <section class="dashboard-panel dashboard-payments-panel lg:col-span-3">
          <div class="dashboard-panel-header">
            <div>
              <div class="dashboard-panel-kicker">Distribuicao de pagamentos</div>
              <h2 class="dashboard-panel-title">Hoje</h2>
            </div>
          </div>

          <div class="dashboard-payment-layout">
            <div class="dashboard-donut-shell">
              <Chart v-if="paymentReport.length > 0" type="doughnut" :data="paymentChartData" :options="paymentChartOptions" class="dashboard-chart" />
              <div v-else class="dashboard-chart-empty dashboard-chart-empty-small">Sem pagamentos no dia.</div>
            </div>

            <div class="dashboard-payment-legend">
              <div v-for="item in paymentLegend" :key="item.label" class="dashboard-payment-row">
                <div class="dashboard-payment-row-main">
                  <span class="dashboard-payment-dot" :style="{ backgroundColor: item.color }"></span>
                  <span class="dashboard-payment-label">{{ item.label }}</span>
                </div>
                <div class="dashboard-payment-values">
                  <strong>{{ item.value }}</strong>
                  <span>{{ item.share }}</span>
                </div>
              </div>
            </div>
          </div>

          <Button label="Ver todos os relatorios" size="small" severity="secondary" outlined class="mt-auto" @click="router.push('/relatorios')" />
        </section>
      </div>
    </template>

    <Dialog v-model:visible="showErrorDialog" modal header="Atencao" :style="{ width: '28rem', maxWidth: '92vw' }">
      <div class="text-sm leading-6 text-zinc-700">{{ errorMessage }}</div>

      <template #footer>
        <Button label="Fechar" severity="secondary" @click="showErrorDialog = false" />
      </template>
    </Dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import type { ChartData, ChartOptions } from 'chart.js'
import Button from 'primevue/button'
import Chart from 'primevue/chart'
import Dialog from 'primevue/dialog'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'

import { useAppTopbar } from '@/composables/useAppTopbar'
import { getDashboardSummary, listPaymentMethodReport, listSalesReport } from '@/services/analytics'
import { getCurrentCashRegister, getLastClosedSession, listCashRegisterHistory } from '@/services/cashRegister'
import { ApiError } from '@/services/http'
import type { DashboardSummary } from '@/types/dashboard'
import type { CashRegisterSession } from '@/types/cashRegister'
import type { PaymentMethodReportRow, SalesSummaryRow } from '@/types/report'

interface KpiCard {
  title: string
  value: string
  deltaLabel: string
  deltaTone: string
  deltaIcon: string
  icon: string
  iconTone: string
}

interface HighlightCard {
  title: string
  value: string
  meta: string
  icon: string
  iconTone: string
}

interface DashboardAlert {
  title: string
  text: string
  badge: string
  severity: 'success' | 'warn' | 'danger' | 'info' | 'secondary'
  icon: string
  iconTone: string
  cardClass: string
}

const router = useRouter()
const { setTopbar, clearTopbar } = useAppTopbar()

const summary = ref<DashboardSummary | null>(null)
const paymentReport = ref<PaymentMethodReportRow[]>([])
const salesRows = ref<SalesSummaryRow[]>([])
const currentSession = ref<CashRegisterSession | null>(null)
const lastClosedSession = ref<CashRegisterSession | null>(null)
const isLoading = ref(true)
const showErrorDialog = ref(false)
const errorMessage = ref('')

const dashboardPalette = {
  emerald: '#16a34a',
  emeraldSoft: 'rgba(22, 163, 74, 0.12)',
  emeraldMid: '#34d399',
  blue: '#2563eb',
  amber: '#f59e0b',
  red: '#ef4444',
  zinc: '#64748b',
  grid: 'rgba(148, 163, 184, 0.18)'
}

const paymentColors: Record<string, string> = {
  PIX: '#16a34a',
  CASH: '#86efac',
  DEBIT_CARD: '#fbbf24',
  CREDIT_CARD: '#f87171',
  MIXED: '#60a5fa'
}

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const compactCurrencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumFractionDigits: 1
})

const dayFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit'
})

const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})

const todayIso = computed(() => summary.value?.report_date ?? todayDate())

const yesterdaySalesRow = computed(() => {
  const yesterday = shiftDate(todayIso.value, -1)
  return salesRows.value.find((row) => row.report_date === yesterday) ?? null
})

const displayHourlyPoints = computed(() =>
  (summary.value?.sales_by_hour_today ?? []).filter((point) => {
    const hour = Number(point.hour.slice(0, 2))
    return hour >= 8 && hour <= 22
  })
)

const hasHourlySales = computed(() => displayHourlyPoints.value.some((point) => Number(point.revenue) > 0))

const strongestHour = computed(() => {
  const top = [...displayHourlyPoints.value].sort((left, right) => Number(right.revenue) - Number(left.revenue))[0]

  if (!top || Number(top.revenue) <= 0) {
    return { value: 'Sem pico', meta: 'Nenhuma venda no dia' }
  }

  return {
    value: `${top.hour.slice(0, 2)}h`,
    meta: `${formatCurrency(top.revenue)} · ${top.sales_count} vendas`
  }
})

const dominantPayment = computed(() => {
  const top = paymentReport.value[0]

  if (!top) {
    return {
      title: 'Sem pagamentos',
      meta: 'Nenhuma forma predominante hoje'
    }
  }

  return {
    title: paymentMethodLabel(top.payment_method),
    meta: `${formatCurrency(top.revenue)} (${formatPercentage(top.percentage_of_total)})`
  }
})

const salesTrend = computed(() => {
  const todayValue = Number(summary.value?.revenue_today ?? '0')
  const yesterdayValue = Number(yesterdaySalesRow.value?.final_sales ?? '0')
  const label = buildDeltaLabel(todayValue, yesterdayValue)

  if (todayValue > yesterdayValue) {
    return { label, toneClass: 'dashboard-trend-good' }
  }
  if (todayValue < yesterdayValue) {
    return { label, toneClass: 'dashboard-trend-bad' }
  }
  return { label: 'Estavel', toneClass: 'dashboard-trend-neutral' }
})

const cashSummary = computed(() => {
  if (lastClosedSession.value) {
    return {
      expected: lastClosedSession.value.expected_amount,
      counted: lastClosedSession.value.closing_amount,
      difference: lastClosedSession.value.difference_amount
    }
  }

  return {
    expected: currentSession.value?.expected_amount ?? '0.00',
    counted: null,
    difference: null
  }
})

const cashStatus = computed(() => {
  const difference = Math.abs(Number(cashSummary.value.difference ?? '0'))

  if (cashSummary.value.difference !== null) {
    if (difference === 0) {
      return {
        label: 'Balanceado',
        severity: 'success' as const,
        caption: 'Fechamento sem diferenca',
        textClass: 'dashboard-text-good',
        progressClass: 'dashboard-progress-good'
      }
    }
    if (difference <= 10) {
      return {
        label: 'Atencao',
        severity: 'warn' as const,
        caption: 'Pequena divergencia',
        textClass: 'dashboard-text-warn',
        progressClass: 'dashboard-progress-warn'
      }
    }

    return {
      label: 'Problema',
      severity: 'danger' as const,
      caption: 'Divergencia relevante',
      textClass: 'dashboard-text-bad',
      progressClass: 'dashboard-progress-bad'
    }
  }

  return {
    label: currentSession.value ? 'Em aberto' : 'Sem caixa',
    severity: currentSession.value ? 'secondary' as const : 'warn' as const,
    caption: currentSession.value ? 'Aguardando fechamento' : 'Nenhum caixa ativo',
    textClass: 'dashboard-text-neutral',
    progressClass: 'dashboard-progress-neutral'
  }
})

const cashBalanceProgress = computed(() => {
  const expected = Math.max(Number(cashSummary.value.expected || '0'), 1)
  const difference = Math.abs(Number(cashSummary.value.difference ?? '0'))

  if (cashSummary.value.difference === null) {
    return 42
  }

  return Math.max(6, Math.min(100, 100 - (difference / expected) * 100))
})

const cashTimestampLabel = computed(() => {
  if (lastClosedSession.value?.closed_at) {
    return `Ultimo fechamento: ${formatDateTime(lastClosedSession.value.closed_at)}`
  }
  if (currentSession.value?.opened_at) {
    return `Caixa atual aberto em ${formatDateTime(currentSession.value.opened_at)}`
  }
  return 'Sem historico de fechamento'
})

const kpiCards = computed<KpiCard[]>(() => {
  if (!summary.value) {
    return []
  }

  const todayRevenue = Number(summary.value.revenue_today)
  const yesterdayRevenue = Number(yesterdaySalesRow.value?.final_sales ?? '0')
  const todayExpenses = Number(summary.value.expenses_today)
  const yesterdayExpenses = Number(yesterdaySalesRow.value?.expenses ?? '0')
  const todayProfit = Number(summary.value.profit_estimate_today)
  const yesterdayProfit = Number(yesterdaySalesRow.value?.estimated_result ?? '0')
  const todaySalesCount = summary.value.sales_count_today
  const yesterdaySalesCount = yesterdaySalesRow.value?.sales_count ?? 0
  const todayTicket = Number(summary.value.average_ticket_today)
  const yesterdayTicket = yesterdaySalesCount > 0 ? Number(yesterdaySalesRow.value?.final_sales ?? '0') / yesterdaySalesCount : 0

  return [
    {
      title: 'Receita hoje',
      value: formatCurrency(summary.value.revenue_today),
      deltaLabel: buildDeltaLabel(todayRevenue, yesterdayRevenue),
      deltaTone: deltaClass(todayRevenue, yesterdayRevenue),
      deltaIcon: deltaIcon(todayRevenue, yesterdayRevenue),
      icon: 'pi pi-dollar',
      iconTone: 'dashboard-icon-good'
    },
    {
      title: 'Despesas hoje',
      value: formatCurrency(summary.value.expenses_today),
      deltaLabel: buildDeltaLabel(todayExpenses, yesterdayExpenses),
      deltaTone: deltaClassReversed(todayExpenses, yesterdayExpenses),
      deltaIcon: deltaIconReversed(todayExpenses, yesterdayExpenses),
      icon: 'pi pi-trash',
      iconTone: 'dashboard-icon-bad'
    },
    {
      title: 'Resultado estimado',
      value: formatCurrency(summary.value.profit_estimate_today),
      deltaLabel: buildDeltaLabel(todayProfit, yesterdayProfit),
      deltaTone: deltaClass(todayProfit, yesterdayProfit),
      deltaIcon: deltaIcon(todayProfit, yesterdayProfit),
      icon: 'pi pi-chart-line',
      iconTone: 'dashboard-icon-good'
    },
    {
      title: 'Ticket medio',
      value: formatCurrency(summary.value.average_ticket_today),
      deltaLabel: buildDeltaLabel(todayTicket, yesterdayTicket),
      deltaTone: deltaClass(todayTicket, yesterdayTicket),
      deltaIcon: deltaIcon(todayTicket, yesterdayTicket),
      icon: 'pi pi-receipt',
      iconTone: 'dashboard-icon-warn'
    },
    {
      title: 'Vendas hoje',
      value: String(summary.value.sales_count_today),
      deltaLabel: buildDeltaLabel(todaySalesCount, yesterdaySalesCount),
      deltaTone: deltaClass(todaySalesCount, yesterdaySalesCount),
      deltaIcon: deltaIcon(todaySalesCount, yesterdaySalesCount),
      icon: 'pi pi-shopping-bag',
      iconTone: 'dashboard-icon-info'
    }
  ]
})

const highlightCards = computed<HighlightCard[]>(() => [
  {
    title: 'Produto mais vendido',
    value: summary.value?.best_selling_product_today?.product_name ?? 'Sem vendas',
    meta: summary.value?.best_selling_product_today
      ? `${summary.value.best_selling_product_today.quantity_sold} unidades`
      : 'Nenhum item saiu hoje',
    icon: 'pi pi-shop',
    iconTone: 'dashboard-highlight-amber'
  },
  {
    title: 'Categoria com mais receita',
    value: summary.value?.best_category_today?.category_name ?? 'Sem categoria lider',
    meta: summary.value?.best_category_today
      ? formatCurrency(summary.value.best_category_today.revenue)
      : 'Sem receita relevante',
    icon: 'pi pi-tag',
    iconTone: 'dashboard-highlight-amber'
  },
  {
    title: 'Forma de pagamento',
    value: dominantPayment.value.title,
    meta: dominantPayment.value.meta,
    icon: 'pi pi-wallet',
    iconTone: 'dashboard-highlight-teal'
  },
  {
    title: 'Melhor horario',
    value: strongestHour.value.value,
    meta: strongestHour.value.meta,
    icon: 'pi pi-clock',
    iconTone: 'dashboard-highlight-violet'
  }
])

const alerts = computed<DashboardAlert[]>(() => {
  const nextAlerts: DashboardAlert[] = []
  const todayRevenue = Number(summary.value?.revenue_today ?? '0')
  const yesterdayRevenue = Number(yesterdaySalesRow.value?.final_sales ?? '0')
  const todayExpenses = Number(summary.value?.expenses_today ?? '0')
  const previousExpenses = salesRows.value
    .filter((row) => row.report_date !== todayIso.value)
    .map((row) => Number(row.expenses))
  const averagePastExpenses = previousExpenses.length > 0
    ? previousExpenses.reduce((sum, value) => sum + value, 0) / previousExpenses.length
    : 0
  const difference = Math.abs(Number(cashSummary.value.difference ?? '0'))

  if (cashSummary.value.difference !== null && difference > 0) {
    nextAlerts.push({
      title: difference > 10 ? 'Divergencia relevante no caixa' : 'Pequena divergencia no caixa',
      text: `Diferenca de ${formatNullableCurrency(cashSummary.value.difference)} no fechamento mais recente.`,
      badge: difference > 10 ? 'Atencao' : 'Monitorar',
      severity: difference > 10 ? 'danger' : 'warn',
      icon: difference > 10 ? 'pi pi-exclamation-triangle' : 'pi pi-info-circle',
      iconTone: difference > 10 ? 'dashboard-alert-bad' : 'dashboard-alert-warn',
      cardClass: difference > 10 ? 'dashboard-alert-card-bad' : 'dashboard-alert-card-warn'
    })
  }

  if (averagePastExpenses > 0 && todayExpenses > averagePastExpenses * 1.1) {
    const percent = ((todayExpenses - averagePastExpenses) / averagePastExpenses) * 100
    nextAlerts.push({
      title: 'Despesa acima da media',
      text: `Despesas de hoje estao ${percent.toFixed(1).replace('.', ',')}% acima da media dos ultimos dias.`,
      badge: 'Informacao',
      severity: 'info',
      icon: 'pi pi-info-circle',
      iconTone: 'dashboard-alert-info',
      cardClass: 'dashboard-alert-card-info'
    })
  }

  if (summary.value?.sales_count_today === 0) {
    nextAlerts.push({
      title: 'Nenhuma venda hoje',
      text: 'O caixa esta sem movimento registrado. Vale conferir se houve queda real ou venda fora do fluxo.',
      badge: 'Parado',
      severity: 'warn',
      icon: 'pi pi-shopping-cart',
      iconTone: 'dashboard-alert-warn',
      cardClass: 'dashboard-alert-card-warn'
    })
  } else if (todayRevenue > yesterdayRevenue) {
    nextAlerts.push({
      title: 'Bom desempenho',
      text: `Receita de hoje esta ${buildDeltaLabel(todayRevenue, yesterdayRevenue)} acima de ontem.`,
      badge: 'Positivo',
      severity: 'success',
      icon: 'pi pi-check-circle',
      iconTone: 'dashboard-alert-good',
      cardClass: 'dashboard-alert-card-good'
    })
  } else if (yesterdayRevenue > 0 && todayRevenue < yesterdayRevenue * 0.8) {
    nextAlerts.push({
      title: 'Queda incomum de receita',
      text: `Receita de hoje caiu ${buildDeltaLabel(todayRevenue, yesterdayRevenue)} contra ontem.`,
      badge: 'Oscilacao',
      severity: 'info',
      icon: 'pi pi-chart-line',
      iconTone: 'dashboard-alert-info',
      cardClass: 'dashboard-alert-card-info'
    })
  }

  if (nextAlerts.length === 0) {
    nextAlerts.push({
      title: 'Operacao estavel',
      text: 'Sem alertas operacionais fortes no momento.',
      badge: 'Ok',
      severity: 'success',
      icon: 'pi pi-check-circle',
      iconTone: 'dashboard-alert-good',
      cardClass: 'dashboard-alert-card-good'
    })
  }

  return nextAlerts.slice(0, 3)
})

const quickSummaryItems = computed(() => [
  {
    label: 'Recebimentos',
    value: formatCurrency(summary.value?.revenue_today ?? '0'),
    toneClass: ''
  },
  {
    label: 'Despesas',
    value: `- ${formatCurrency(summary.value?.expenses_today ?? '0')}`,
    toneClass: 'dashboard-text-neutral'
  },
  {
    label: 'Resultado estimado',
    value: formatCurrency(summary.value?.profit_estimate_today ?? '0'),
    toneClass: Number(summary.value?.profit_estimate_today ?? '0') >= 0 ? 'dashboard-text-good' : 'dashboard-text-bad'
  },
  {
    label: 'Vendas concluidas',
    value: String(summary.value?.sales_count_today ?? 0),
    toneClass: ''
  },
  {
    label: 'Ticket medio',
    value: formatCurrency(summary.value?.average_ticket_today ?? '0'),
    toneClass: ''
  },
  {
    label: 'Ultimo fechamento',
    value: lastClosedSession.value?.closed_at ? formatDateTime(lastClosedSession.value.closed_at) : 'Sem fechamento',
    toneClass: ''
  }
])

const paymentLegend = computed(() =>
  paymentReport.value.map((item) => ({
    label: paymentMethodLabel(item.payment_method),
    color: paymentColors[item.payment_method],
    value: formatCurrency(item.revenue),
    share: formatPercentage(item.percentage_of_total)
  }))
)

const hourlyChartData = computed<ChartData<'bar'>>(() => ({
  labels: displayHourlyPoints.value.map((point) => `${point.hour.slice(0, 2)}h`),
  datasets: [
    {
      label: 'Receita',
      data: displayHourlyPoints.value.map((point) => Number(point.revenue)),
      backgroundColor: dashboardPalette.emeraldMid,
      borderRadius: 6,
      borderSkipped: false,
      maxBarThickness: 22
    }
  ]
}))

const hourlyChartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => ` ${currencyFormatter.format(Number(context.raw ?? 0))}`
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: dashboardPalette.zinc, font: { size: 10, weight: 'bold' } },
      border: { display: false }
    },
    y: {
      beginAtZero: true,
      ticks: {
        color: dashboardPalette.zinc,
        font: { size: 10 },
        callback: (value) => compactCurrencyFormatter.format(Number(value))
      },
      grid: { color: dashboardPalette.grid, drawBorder: false },
      border: { display: false }
    }
  }
}))

const weeklyRevenueChartData = computed<ChartData<'line'>>(() => ({
  labels: (summary.value?.revenue_last_7_days ?? []).map((point) => formatDayShort(point.report_date)),
  datasets: [
    {
      label: 'Receita',
      data: (summary.value?.revenue_last_7_days ?? []).map((point) => Number(point.revenue)),
      borderColor: dashboardPalette.emerald,
      backgroundColor: dashboardPalette.emeraldSoft,
      fill: true,
      tension: 0.35,
      borderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 4,
      pointBackgroundColor: dashboardPalette.emerald,
      pointBorderWidth: 0
    }
  ]
}))

const weeklyRevenueChartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => ` ${currencyFormatter.format(Number(context.raw ?? 0))}`
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: dashboardPalette.zinc, font: { size: 10, weight: 'bold' } },
      border: { display: false }
    },
    y: {
      beginAtZero: true,
      ticks: {
        color: dashboardPalette.zinc,
        font: { size: 10 },
        callback: (value) => compactCurrencyFormatter.format(Number(value))
      },
      grid: { color: dashboardPalette.grid, drawBorder: false },
      border: { display: false }
    }
  }
}))

const paymentChartData = computed<ChartData<'doughnut'>>(() => ({
  labels: paymentReport.value.map((item) => paymentMethodLabel(item.payment_method)),
  datasets: [
    {
      data: paymentReport.value.map((item) => Number(item.revenue)),
      backgroundColor: paymentReport.value.map((item) => paymentColors[item.payment_method]),
      borderWidth: 0,
      hoverOffset: 2
    }
  ]
}))

const paymentChartOptions = computed<ChartOptions<'doughnut'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '67%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => {
          const value = Number(context.raw ?? 0)
          const total = paymentReport.value.reduce((sum, item) => sum + Number(item.revenue), 0)
          const share = total > 0 ? (value / total) * 100 : 0
          return ` ${currencyFormatter.format(value)} (${share.toFixed(1)}%)`
        }
      }
    }
  }
}))

function todayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function shiftDate(value: string, deltaDays: number): string {
  const date = new Date(`${value}T00:00:00`)
  date.setDate(date.getDate() + deltaDays)
  return date.toISOString().slice(0, 10)
}

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value || '0'))
}

function formatNullableCurrency(value: string | null): string {
  return value ? formatCurrency(value) : '--'
}

function formatDay(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

function formatDayShort(value: string): string {
  return dayFormatter.format(new Date(`${value}T00:00:00`))
}

function formatDateTime(value: string): string {
  return dateTimeFormatter.format(new Date(value))
}

function formatPercentage(value: string): string {
  return `${Number(value || '0').toFixed(1)}%`
}

function buildDeltaLabel(current: number, previous: number): string {
  if (previous === 0) {
    return current === 0 ? '0,0%' : '+100,0%'
  }

  const percentage = ((current - previous) / previous) * 100
  return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(1).replace('.', ',')}%`
}

function deltaClass(current: number, previous: number): string {
  if (current > previous) {
    return 'dashboard-text-good'
  }
  if (current < previous) {
    return 'dashboard-text-bad'
  }
  return 'dashboard-text-neutral'
}

function deltaIcon(current: number, previous: number): string {
  if (current > previous) {
    return 'pi pi-arrow-up'
  }
  if (current < previous) {
    return 'pi pi-arrow-down'
  }
  return 'pi pi-minus'
}

function deltaClassReversed(current: number, previous: number): string {
  if (current < previous) {
    return 'dashboard-text-good'
  }
  if (current > previous) {
    return 'dashboard-text-bad'
  }
  return 'dashboard-text-neutral'
}

function deltaIconReversed(current: number, previous: number): string {
  if (current < previous) {
    return 'pi pi-arrow-down'
  }
  if (current > previous) {
    return 'pi pi-arrow-up'
  }
  return 'pi pi-minus'
}

function paymentMethodLabel(value: PaymentMethodReportRow['payment_method']): string {
  return {
    CASH: 'Dinheiro',
    PIX: 'PIX',
    DEBIT_CARD: 'Cartao Debito',
    CREDIT_CARD: 'Cartao Credito',
    MIXED: 'Misto'
  }[value]
}

function readError(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return fallback
}

async function getCurrentSessionOrNull(): Promise<CashRegisterSession | null> {
  try {
    return await getCurrentCashRegister()
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null
    }
    throw error
  }
}

async function loadDashboard(): Promise<void> {
  isLoading.value = true

  try {
    const today = todayDate()
    const sevenDaysAgo = shiftDate(today, -6)
    const [dashboardSummary, payments, salesHistory, currentCashSession, historySessions] = await Promise.all([
      getDashboardSummary(),
      listPaymentMethodReport({ start_date: today, end_date: today }),
      listSalesReport({ start_date: sevenDaysAgo, end_date: today }),
      getCurrentSessionOrNull(),
      listCashRegisterHistory()
    ])

    summary.value = dashboardSummary
    paymentReport.value = payments
    salesRows.value = salesHistory
    currentSession.value = currentCashSession?.status === 'OPEN' ? currentCashSession : null
    lastClosedSession.value = historySessions.find((session) => session.status === 'CLOSED') ?? getLastClosedSession()
  } catch (error) {
    errorMessage.value = readError(error, 'Nao foi possivel carregar o dashboard.')
    showErrorDialog.value = true
  } finally {
    isLoading.value = false
  }
}

watchEffect(() => {
  setTopbar({
    badge: {
      value: summary.value ? `Hoje, ${formatDay(summary.value.report_date)}` : 'Hoje',
      severity: 'secondary'
    },
    actions: [
      {
        key: 'refresh-dashboard',
        label: 'Atualizar',
        severity: 'secondary',
        outlined: true,
        size: 'small',
        onClick: () => {
          void loadDashboard()
        }
      }
    ]
  })
})

onMounted(async () => {
  await loadDashboard()
})

onBeforeUnmount(() => {
  clearTopbar()
})
</script>

<style scoped>
.dashboard-screen {
  min-height: calc(100vh - 1rem);
}

.dashboard-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfc 100%);
  padding: 0.75rem 0.95rem;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.04);
}

.dashboard-topbar-kicker,
.dashboard-panel-kicker,
.dashboard-mini-label,
.dashboard-kpi-label {
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.dashboard-topbar-title {
  margin: 0.18rem 0 0;
  font-size: 1.18rem;
  line-height: 1.1;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  align-content: start;
}

.dashboard-kpis-row {
  grid-column: 1 / -1;
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.dashboard-kpi-card,
.dashboard-panel,
.dashboard-loading-state {
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfc 100%);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.04);
}

.dashboard-kpi-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.85rem 0.95rem;
}

.dashboard-kpi-head {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.dashboard-kpi-icon,
.dashboard-highlight-icon,
.dashboard-alert-icon {
  display: inline-flex;
  height: 2rem;
  width: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  flex: 0 0 auto;
}

.dashboard-icon-good {
  background: rgba(22, 163, 74, 0.12);
  color: #16a34a;
}

.dashboard-icon-bad {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.dashboard-icon-warn {
  background: rgba(245, 158, 11, 0.14);
  color: #d97706;
}

.dashboard-icon-info {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.dashboard-kpi-value {
  margin-top: 0.1rem;
  font-size: 1.68rem;
  line-height: 1;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-kpi-foot {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 1rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.dashboard-kpi-foot-muted {
  font-weight: 600;
  color: #94a3b8;
}

.dashboard-panel {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.8rem;
  padding: 0.9rem 1rem;
}

.dashboard-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.dashboard-panel-title {
  margin: 0.2rem 0 0;
  font-size: 0.98rem;
  line-height: 1.15;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-note-chip {
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
}

.dashboard-trend-good {
  color: #16a34a;
}

.dashboard-trend-bad {
  color: #ef4444;
}

.dashboard-trend-neutral,
.dashboard-text-neutral {
  color: #64748b;
}

.dashboard-text-good {
  color: #16a34a;
}

.dashboard-text-warn {
  color: #d97706;
}

.dashboard-text-bad {
  color: #ef4444;
}

.dashboard-cash-stats,
.dashboard-highlights-grid {
  display: grid;
  gap: 0.65rem;
}

.dashboard-cash-stats {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-cash-item,
.dashboard-highlight-card {
  border: 1px solid #eceef2;
  border-radius: 0.9rem;
  background: linear-gradient(180deg, #ffffff 0%, #fcfcfd 100%);
  padding: 0.75rem 0.8rem;
}

.dashboard-cash-value {
  display: block;
  margin-top: 0.28rem;
  font-size: 1.2rem;
  line-height: 1.05;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-cash-status-box {
  display: flex;
  flex-direction: column;
  gap: 0.38rem;
}

.dashboard-cash-caption {
  font-size: 0.75rem;
  color: #64748b;
}

.dashboard-cash-progress-shell :deep(.p-progressbar) {
  height: 0.55rem;
  border-radius: 999px;
  background: #eef2f7;
}

.dashboard-progress-good :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, #16a34a 0%, #22c55e 100%);
}

.dashboard-progress-warn :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, #16a34a 0%, #16a34a 82%, #f59e0b 82%, #f59e0b 100%);
}

.dashboard-progress-bad :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, #16a34a 0%, #16a34a 68%, #ef4444 68%, #ef4444 100%);
}

.dashboard-progress-neutral :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, #94a3b8 0%, #64748b 100%);
}

.dashboard-cash-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.dashboard-meta-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.76rem;
  font-weight: 600;
  color: #64748b;
}

.dashboard-highlights-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-highlight-card {
  display: flex;
  min-width: 0;
  gap: 0.7rem;
  align-items: flex-start;
}

.dashboard-highlight-title {
  display: block;
  margin-top: 0.18rem;
  font-size: 0.98rem;
  line-height: 1.15;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-highlight-subtitle {
  margin-top: 0.16rem;
  font-size: 0.76rem;
  line-height: 1.4;
  color: #64748b;
}

.dashboard-highlight-amber {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.dashboard-highlight-teal {
  background: rgba(20, 184, 166, 0.12);
  color: #0f766e;
}

.dashboard-highlight-violet {
  background: rgba(99, 102, 241, 0.12);
  color: #4f46e5;
}

.dashboard-chart-panel {
  min-height: 13rem;
}

.dashboard-chart-shell {
  position: relative;
  min-height: 9.6rem;
}

.dashboard-chart-shell-bar {
  min-height: 10rem;
}

.dashboard-chart-shell-line {
  min-height: 10rem;
}

.dashboard-chart {
  height: 100%;
}

.dashboard-chart-empty {
  display: flex;
  min-height: 9rem;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 0.84rem;
  font-weight: 600;
  color: #64748b;
}

.dashboard-chart-empty-small {
  min-height: 7rem;
}

.dashboard-alert-list,
.dashboard-summary-list,
.dashboard-payment-legend {
  display: grid;
  gap: 0.6rem;
}

.dashboard-alert-card {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  border: 1px solid #eceef2;
  border-radius: 0.9rem;
  padding: 0.72rem 0.8rem;
}

.dashboard-alert-card-warn {
  background: linear-gradient(180deg, #fffaf0 0%, #fff7e6 100%);
  border-color: #fde68a;
}

.dashboard-alert-card-info {
  background: linear-gradient(180deg, #f5f9ff 0%, #eff6ff 100%);
  border-color: #bfdbfe;
}

.dashboard-alert-card-good {
  background: linear-gradient(180deg, #f3fff7 0%, #ecfdf3 100%);
  border-color: #bbf7d0;
}

.dashboard-alert-card-bad {
  background: linear-gradient(180deg, #fff5f5 0%, #fff1f2 100%);
  border-color: #fecaca;
}

.dashboard-alert-warn {
  background: rgba(245, 158, 11, 0.14);
  color: #d97706;
}

.dashboard-alert-info {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.dashboard-alert-good {
  background: rgba(22, 163, 74, 0.12);
  color: #16a34a;
}

.dashboard-alert-bad {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.dashboard-alert-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.dashboard-alert-title {
  font-size: 0.86rem;
  line-height: 1.2;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-alert-text {
  margin: 0.22rem 0 0;
  font-size: 0.76rem;
  line-height: 1.4;
  color: #64748b;
}

.dashboard-summary-row,
.dashboard-payment-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.dashboard-summary-label,
.dashboard-payment-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
}

.dashboard-summary-value {
  text-align: right;
  font-size: 0.84rem;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-payment-layout {
  display: grid;
  grid-template-columns: 7rem 1fr;
  gap: 0.8rem;
  align-items: center;
}

.dashboard-donut-shell {
  min-height: 7rem;
}

.dashboard-payment-row-main {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}

.dashboard-payment-dot {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 999px;
  flex: 0 0 auto;
}

.dashboard-payment-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.06rem;
  font-size: 0.73rem;
  color: #64748b;
}

.dashboard-payment-values strong {
  font-size: 0.78rem;
  color: #0f172a;
}

.dashboard-loading-state {
  display: flex;
  min-height: 20rem;
  align-items: center;
  justify-content: center;
}

@media (max-width: 1280px) {
  .dashboard-kpis-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-highlights-grid,
  .dashboard-cash-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .dashboard-topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .dashboard-kpis-row,
  .dashboard-highlights-grid,
  .dashboard-cash-stats,
  .dashboard-payment-layout {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-cash-panel,
  .dashboard-highlights-panel,
  .dashboard-chart-panel,
  .dashboard-alerts-panel,
  .dashboard-summary-panel,
  .dashboard-payments-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .dashboard-kpis-row,
  .dashboard-highlights-grid,
  .dashboard-cash-stats,
  .dashboard-payment-layout {
    grid-template-columns: 1fr;
  }

  .dashboard-cash-bottom,
  .dashboard-alert-head,
  .dashboard-summary-row,
  .dashboard-payment-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
