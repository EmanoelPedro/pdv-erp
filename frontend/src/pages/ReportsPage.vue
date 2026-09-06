<template>
  <section class="app-page flex flex-col gap-4">
    <div class="ops-kpi-grid">
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Receita filtrada</span>
        <strong class="ops-kpi-value">{{
          formatCurrency(filteredRevenue)
        }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Despesas filtradas</span>
        <strong class="ops-kpi-value">{{
          formatCurrency(filteredExpenses)
        }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Resultado estimado</span>
        <strong class="ops-kpi-value">{{
          formatCurrency(filteredResult)
        }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Método dominante</span>
        <strong class="ops-kpi-value">{{ dominantPaymentLabel }}</strong>
      </div>
    </div>

    <section class="pos-surface pos-stage-panel">
      <div class="ops-filter-grid analytics-filter-grid">
        <div class="flex flex-col gap-2">
          <label
            class="text-sm font-medium text-zinc-700"
            for="report-start-date"
            >Data inicial</label
          >
          <InputText
            id="report-start-date"
            v-model="filters.start_date"
            type="date"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="report-end-date"
            >Data final</label
          >
          <InputText
            id="report-end-date"
            v-model="filters.end_date"
            type="date"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="report-category"
            >Categoria</label
          >
          <Select
            id="report-category"
            v-model="filters.category_id"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="report-payment"
            >Pagamento</label
          >
          <Select
            id="report-payment"
            v-model="filters.payment_method"
            :options="paymentOptions"
            option-label="label"
            option-value="value"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="report-user"
            >Usuário</label
          >
          <Select
            id="report-user"
            v-model="filters.user_id"
            :options="userOptions"
            option-label="label"
            option-value="value"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="report-session"
            >Sessao</label
          >
          <Select
            id="report-session"
            v-model="filters.cash_register_session_id"
            :options="sessionOptions"
            option-label="label"
            option-value="value"
          />
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <Button label="Aplicar filtros" @click="loadReports" />
        <Button
          label="Hoje"
          severity="secondary"
          outlined
          @click="applyTodayFilter"
        />
        <Button
          label="Ultimos 7 dias"
          severity="secondary"
          outlined
          @click="applyLast7DaysFilter"
        />
        <Button
          label="Limpar"
          severity="secondary"
          text
          @click="clearFilters"
        />
      </div>
    </section>

    <section class="analytics-selector-grid">
      <button
        v-for="report in reportOptions"
        :key="report.value"
        class="analytics-selector-button"
        :class="{
          'analytics-selector-button-active': activeReport === report.value
        }"
        type="button"
        @click="activeReport = report.value"
      >
        <span class="font-semibold text-zinc-950">{{ report.label }}</span>
        <span class="text-sm text-zinc-500">{{ report.text }}</span>
      </button>
    </section>

    <section class="pos-surface pos-stage-panel">
      <div class="analytics-panel-header mb-4">
        <div>
          <div class="analytics-panel-kicker">Relatório ativo</div>
          <h2 class="analytics-panel-title">{{ activeReportMeta.label }}</h2>
        </div>
        <div class="text-sm text-zinc-500">{{ activeReportMeta.text }}</div>
      </div>

      <div
        v-if="isLoading"
        class="flex min-h-[18rem] items-center justify-center"
      >
        <ProgressSpinner stroke-width="4" />
      </div>

      <div
        v-else-if="activeRowsCount === 0"
        class="pos-empty-state !min-h-[16rem]"
      >
        <div class="text-4xl">📊</div>
        <div class="mt-2 text-base font-semibold text-zinc-700">
          Nenhum dado para este recorte
        </div>
        <div class="mt-1 text-sm text-zinc-500">
          Ajuste filtros, amplie o período ou escolha outro relatório.
        </div>
      </div>

      <div v-else class="flex flex-col gap-4">
        <template v-if="activeReport === 'sales'">
          <DataTable :value="salesSummary" size="small" striped-rows>
            <Column header="Data">
              <template #body="slotProps">{{
                formatDay(slotProps.data.report_date)
              }}</template>
            </Column>
            <Column field="sales_count" header="Vendas" />
            <Column header="Bruto">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.gross_sales)
              }}</template>
            </Column>
            <Column header="Descontos">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.discounts)
              }}</template>
            </Column>
            <Column header="Final">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.final_sales)
              }}</template>
            </Column>
            <Column header="Despesas">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.expenses)
              }}</template>
            </Column>
            <Column header="Resultado">
              <template #body="slotProps">
                <span
                  class="font-semibold"
                  :class="toneByAmount(slotProps.data.estimated_result)"
                  >{{ formatCurrency(slotProps.data.estimated_result) }}</span
                >
              </template>
            </Column>
          </DataTable>
        </template>

        <template v-else-if="activeReport === 'products'">
          <DataTable :value="productPerformance" size="small" striped-rows>
            <Column field="product_name" header="Produto" />
            <Column field="quantity_sold" header="Quantidade" />
            <Column header="Receita">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.revenue)
              }}</template>
            </Column>
            <Column header="Participação média">
              <template #body="slotProps">{{
                formatPercentage(slotProps.data.average_sale_participation)
              }}</template>
            </Column>
          </DataTable>
        </template>

        <template v-else-if="activeReport === 'categories'">
          <DataTable :value="categoryPerformance" size="small" striped-rows>
            <Column field="category_name" header="Categoria" />
            <Column field="units_sold" header="Unidades" />
            <Column header="Receita">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.revenue)
              }}</template>
            </Column>
            <Column header="% do total">
              <template #body="slotProps">{{
                formatPercentage(slotProps.data.percentage_of_total)
              }}</template>
            </Column>
          </DataTable>
        </template>

        <template v-else-if="activeReport === 'payments'">
          <div class="analytics-share-list">
            <div
              v-for="row in paymentMethods"
              :key="row.payment_method"
              class="analytics-share-row"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <div class="text-sm font-semibold text-zinc-950">
                    {{ paymentMethodLabel(row.payment_method) }}
                  </div>
                  <div class="text-xs text-zinc-500">
                    {{ row.transactions }} transações ·
                    {{ formatCurrency(row.revenue) }}
                  </div>
                </div>
                <div class="text-sm font-semibold text-zinc-950">
                  {{ formatPercentage(row.percentage_of_total) }}
                </div>
              </div>
              <div class="analytics-progress-track mt-2">
                <div
                  class="analytics-progress-fill"
                  :style="{ width: `${Number(row.percentage_of_total)}%` }"
                ></div>
              </div>
            </div>
          </div>

          <DataTable :value="paymentMethods" size="small" striped-rows>
            <Column header="Método">
              <template #body="slotProps">
                <Tag
                  :severity="
                    slotProps.data.payment_method === 'CASH'
                      ? 'success'
                      : 'secondary'
                  "
                  :value="paymentMethodLabel(slotProps.data.payment_method)"
                />
              </template>
            </Column>
            <Column field="transactions" header="Transações" />
            <Column header="Receita">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.revenue)
              }}</template>
            </Column>
            <Column header="% do total">
              <template #body="slotProps">{{
                formatPercentage(slotProps.data.percentage_of_total)
              }}</template>
            </Column>
          </DataTable>
        </template>

        <template v-else-if="activeReport === 'hourly'">
          <div class="analytics-column-chart analytics-column-chart-wide">
            <div
              v-for="row in hourlySales"
              :key="row.hour"
              class="analytics-column-item analytics-column-item-wide"
            >
              <div class="analytics-column-value">
                {{
                  Number(row.revenue) > 0
                    ? formatCompactCurrency(row.revenue)
                    : ''
                }}
              </div>
              <div class="analytics-column-track">
                <div
                  class="analytics-column-fill analytics-column-fill-amber"
                  :style="{
                    height: `${columnHeight(row.revenue, hourlyReportMax)}%`
                  }"
                ></div>
              </div>
              <div class="analytics-column-label">
                {{ row.hour.slice(0, 2) }}
              </div>
            </div>
          </div>

          <DataTable :value="hourlySales" size="small" striped-rows>
            <Column field="hour" header="Hora" />
            <Column field="sales_count" header="Vendas" />
            <Column header="Receita">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.revenue)
              }}</template>
            </Column>
          </DataTable>
        </template>

        <template v-else-if="activeReport === 'cash-registers'">
          <DataTable :value="cashRegisters" size="small" striped-rows>
            <Column header="Data">
              <template #body="slotProps">{{
                formatDate(slotProps.data.opened_at)
              }}</template>
            </Column>
            <Column header="Abertura">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.opening_amount)
              }}</template>
            </Column>
            <Column header="Esperado">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.expected_amount)
              }}</template>
            </Column>
            <Column header="Fechamento">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.closing_amount ?? '0.00')
              }}</template>
            </Column>
            <Column header="Diferença">
              <template #body="slotProps">
                <span
                  class="font-semibold"
                  :class="differenceTone(slotProps.data.difference_amount)"
                  >{{
                    formatCurrency(slotProps.data.difference_amount ?? '0.00')
                  }}</span
                >
              </template>
            </Column>
            <Column header="Vendas">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.totals.sales_amount)
              }}</template>
            </Column>
            <Column header="Despesas">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.totals.expenses_amount)
              }}</template>
            </Column>
            <Column header="Status">
              <template #body="slotProps">
                <Tag
                  :severity="
                    slotProps.data.status === 'OPEN' ? 'success' : 'secondary'
                  "
                  :value="
                    slotProps.data.status === 'OPEN' ? 'Aberto' : 'Fechado'
                  "
                />
              </template>
            </Column>
            <Column header="Ações">
              <template #body="slotProps">
                <Button
                  label="Detalhes"
                  size="small"
                  severity="secondary"
                  outlined
                  @click="openDetails(slotProps.data.id)"
                />
              </template>
            </Column>
          </DataTable>
        </template>

        <template v-else>
          <div v-if="flaggedExpenseRows.length > 0" class="analytics-flag-grid">
            <div
              v-for="row in flaggedExpenseRows"
              :key="row.category"
              class="analytics-flag-card"
            >
              <div class="analytics-panel-kicker">Atenção</div>
              <div class="mt-2 text-lg font-semibold text-zinc-950">
                {{ expenseCategoryLabel(row.category) }}
              </div>
              <div class="mt-1 text-sm text-zinc-500">
                {{ formatCurrency(row.amount) }} ·
                {{ formatPercentage(row.percentage_of_total) }} do total
                filtrado
              </div>
            </div>
          </div>

          <DataTable :value="expenseAnalysis" size="small" striped-rows>
            <Column header="Categoria">
              <template #body="slotProps">
                <Tag
                  :severity="expenseTagSeverity(slotProps.data.category)"
                  :value="expenseCategoryLabel(slotProps.data.category)"
                />
              </template>
            </Column>
            <Column field="count" header="Lancamentos" />
            <Column header="Valor">
              <template #body="slotProps">{{
                formatCurrency(slotProps.data.amount)
              }}</template>
            </Column>
            <Column header="% do total">
              <template #body="slotProps">{{
                formatPercentage(slotProps.data.percentage_of_total)
              }}</template>
            </Column>
          </DataTable>
        </template>
      </div>
    </section>

    <Dialog
      v-model:visible="showDetailDialog"
      modal
      header="Resumo da sessão"
      :style="{ width: '56rem', maxWidth: '96vw' }"
    >
      <div
        v-if="detailLoading"
        class="flex min-h-[16rem] items-center justify-center"
      >
        <ProgressSpinner stroke-width="4" />
      </div>

      <div v-else-if="selectedSession" class="flex flex-col gap-4">
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Abertura
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.opening_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Fechamento
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.closing_amount ?? '0.00') }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Esperado
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.expected_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Diferença
            </div>
            <div
              class="mt-2 text-lg font-semibold"
              :class="differenceTone(selectedSession.difference_amount)"
            >
              {{ formatCurrency(selectedSession.difference_amount ?? '0.00') }}
            </div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Dinheiro
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.cash_sales_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Pix
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.pix_sales_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Débito
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{
                formatCurrency(selectedSession.totals.debit_card_sales_amount)
              }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Crédito
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{
                formatCurrency(selectedSession.totals.credit_card_sales_amount)
              }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Misto
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.mixed_sales_amount) }}
            </div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Total de vendas
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.sales_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Total de despesas
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.expenses_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Despesa em dinheiro
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(selectedSession.totals.cash_expenses_amount) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Ultima venda
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{
                selectedSession.totals.last_sale_at
                  ? formatDateTime(selectedSession.totals.last_sale_at)
                  : '--'
              }}
            </div>
          </div>
        </div>

        <div class="pos-summary-tile-soft">
          <div class="text-sm font-semibold text-zinc-950">
            Despesas da sessão
          </div>
          <div
            v-if="selectedSessionExpenses.length === 0"
            class="mt-2 text-sm text-zinc-500"
          >
            Nenhuma despesa vinculada a esta sessão.
          </div>
          <div v-else class="mt-3 grid gap-2">
            <div
              v-for="expense in selectedSessionExpenses"
              :key="expense.id"
              class="flex items-center justify-between gap-3 rounded-xl border border-zinc-200 bg-white px-3 py-2"
            >
              <div>
                <div class="text-sm font-semibold text-zinc-950">
                  {{ expense.description }}
                </div>
                <div class="text-xs text-zinc-500">
                  {{ expenseCategoryLabel(expense.category) }} ·
                  {{ paymentMethodLabel(expense.payment_method) }} ·
                  {{ formatDateTime(expense.expense_date) }}
                </div>
              </div>
              <div class="text-sm font-semibold text-zinc-950">
                {{ formatCurrency(expense.amount) }}
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Aberto em
            </div>
            <div class="mt-2 text-sm font-semibold text-zinc-950">
              {{ formatDateTime(selectedSession.opened_at) }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Fechado em
            </div>
            <div class="mt-2 text-sm font-semibold text-zinc-950">
              {{
                selectedSession.closed_at
                  ? formatDateTime(selectedSession.closed_at)
                  : 'Ainda aberto'
              }}
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Fechar"
          severity="secondary"
          @click="showDetailDialog = false"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showErrorDialog"
      modal
      header="Atenção"
      :style="{ width: '28rem', maxWidth: '92vw' }"
    >
      <div class="text-sm leading-6 text-zinc-700">{{ errorMessage }}</div>

      <template #footer>
        <Button
          label="Fechar"
          severity="secondary"
          @click="showErrorDialog = false"
        />
      </template>
    </Dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watchEffect } from 'vue'
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import ProgressSpinner from 'primevue/progressspinner'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import { useAppTopbar } from '@/composables/useAppTopbar'
import {
  listCashRegisterReport,
  listCategoryReport,
  listExpenseAnalysisReport,
  listHourlySalesReport,
  listPaymentMethodReport,
  listProductReport,
  listSalesReport
} from '@/services/analytics'
import {
  getCashRegisterSession,
  listCashRegisterHistory
} from '@/services/cashRegister'
import { listCategories } from '@/services/catalog'
import { listExpenses } from '@/services/expenses'
import { ApiError } from '@/services/http'
import { listUsers } from '@/services/auth'
import type { AuthUser } from '@/types/auth'
import type { CashRegisterSession } from '@/types/cashRegister'
import type { Category } from '@/types/catalog'
import type { Expense, ExpenseCategory } from '@/types/expense'
import type {
  CashRegisterReportRow,
  CategoryPerformanceRow,
  ExpenseAnalysisRow,
  HourlySalesRow,
  PaymentMethodReportRow,
  ProductPerformanceRow,
  SalesSummaryRow
} from '@/types/report'
import type { PaymentMethod } from '@/types/sale'

type ReportKey =
  | 'sales'
  | 'products'
  | 'categories'
  | 'payments'
  | 'hourly'
  | 'cash-registers'
  | 'expenses'

interface ReportFiltersState {
  start_date: string
  end_date: string
  category_id: string
  payment_method: '' | PaymentMethod
  user_id: string
  cash_register_session_id: string
}

const { setTopbar, clearTopbar } = useAppTopbar()

const reportOptions: Array<{ value: ReportKey; label: string; text: string }> =
  [
    {
      value: 'sales',
      label: 'Resumo de vendas',
      text: 'Quanto vendemos, gastamos e sobrou por dia.'
    },
    {
      value: 'products',
      label: 'Produtos',
      text: 'O que gira mais e participa mais das vendas.'
    },
    {
      value: 'categories',
      label: 'Categorias',
      text: 'Qual categoria concentra mais receita.'
    },
    {
      value: 'payments',
      label: 'Pagamentos',
      text: 'Quais meios dominam o faturamento.'
    },
    {
      value: 'hourly',
      label: 'Horas fortes',
      text: 'Picos e vales de movimento no recorte.'
    },
    {
      value: 'cash-registers',
      label: 'Caixas',
      text: 'Histórico operacional e diferenças reais.'
    },
    {
      value: 'expenses',
      label: 'Despesas',
      text: 'Para onde o dinheiro saiu no período.'
    }
  ]

const salesSummary = ref<SalesSummaryRow[]>([])
const productPerformance = ref<ProductPerformanceRow[]>([])
const categoryPerformance = ref<CategoryPerformanceRow[]>([])
const paymentMethods = ref<PaymentMethodReportRow[]>([])
const hourlySales = ref<HourlySalesRow[]>([])
const cashRegisters = ref<CashRegisterReportRow[]>([])
const expenseAnalysis = ref<ExpenseAnalysisRow[]>([])
const categories = ref<Category[]>([])
const users = ref<AuthUser[]>([])
const filterSessions = ref<CashRegisterSession[]>([])
const selectedSession = ref<CashRegisterSession | null>(null)
const selectedSessionExpenses = ref<Expense[]>([])
const activeReport = ref<ReportKey>('sales')
const isLoading = ref(true)
const detailLoading = ref(false)
const showDetailDialog = ref(false)
const showErrorDialog = ref(false)
const errorMessage = ref('')

const filters = ref<ReportFiltersState>({
  start_date: daysAgo(6),
  end_date: todayDate(),
  category_id: '',
  payment_method: '',
  user_id: '',
  cash_register_session_id: ''
})

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

const dateFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric'
})

const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})

const paymentOptions: Array<{ label: string; value: '' | PaymentMethod }> = [
  { label: 'Todos', value: '' },
  { label: 'Dinheiro', value: 'CASH' },
  { label: 'Pix', value: 'PIX' },
  { label: 'Débito', value: 'DEBIT_CARD' },
  { label: 'Crédito', value: 'CREDIT_CARD' },
  { label: 'Misto', value: 'MIXED' }
]

const categoryOptions = computed(() => [
  { label: 'Todas', value: '' },
  ...categories.value.map((category) => ({
    label: category.name,
    value: category.id
  }))
])

const userOptions = computed(() => [
  { label: 'Todos', value: '' },
  ...users.value.map((user) => ({
    label: `${user.full_name} (@${user.username})`,
    value: user.id
  }))
])

const sessionOptions = computed(() => {
  const seen = new Set<string>()
  const sessionPool = [...filterSessions.value, ...cashRegisters.value].filter(
    (session) => {
      if (seen.has(session.id)) {
        return false
      }
      seen.add(session.id)
      return true
    }
  )

  return [
    { label: 'Todas as sessões', value: '' },
    ...sessionPool.map((session) => ({
      label: sessionLabel(session.id),
      value: session.id
    }))
  ]
})

const filteredRevenue = computed(() =>
  salesSummary.value
    .reduce((sum, row) => sum + Number(row.final_sales), 0)
    .toFixed(2)
)

const filteredExpenses = computed(() =>
  expenseAnalysis.value
    .reduce((sum, row) => sum + Number(row.amount), 0)
    .toFixed(2)
)

const filteredResult = computed(() =>
  (Number(filteredRevenue.value) - Number(filteredExpenses.value)).toFixed(2)
)

const dominantPaymentLabel = computed(() => {
  const leading = paymentMethods.value[0]
  if (!leading) {
    return 'Sem dados'
  }
  return `${paymentMethodLabel(leading.payment_method)} · ${formatPercentage(leading.percentage_of_total)}`
})

const activeReportMeta = computed(
  () =>
    reportOptions.find((option) => option.value === activeReport.value) ??
    reportOptions[0]
)

const activeRowsCount = computed(() => {
  switch (activeReport.value) {
    case 'sales':
      return salesSummary.value.length
    case 'products':
      return productPerformance.value.length
    case 'categories':
      return categoryPerformance.value.length
    case 'payments':
      return paymentMethods.value.length
    case 'hourly':
      return hourlySales.value.length
    case 'cash-registers':
      return cashRegisters.value.length
    case 'expenses':
      return expenseAnalysis.value.length
  }

  return 0
})

const hourlyReportMax = computed(() =>
  Math.max(1, ...hourlySales.value.map((row) => Number(row.revenue)))
)

const flaggedExpenseRows = computed(() =>
  expenseAnalysis.value.filter(
    (row) => row.category === 'WITHDRAWAL' || row.category === 'PERSONAL_USE'
  )
)

function todayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function daysAgo(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().slice(0, 10)
}

function buildFilters() {
  return {
    start_date: filters.value.start_date || undefined,
    end_date: filters.value.end_date || undefined,
    category_id: filters.value.category_id || undefined,
    payment_method: filters.value.payment_method || undefined,
    user_id: filters.value.user_id || undefined,
    cash_register_session_id:
      filters.value.cash_register_session_id || undefined
  }
}

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value || '0'))
}

function formatCompactCurrency(value: string): string {
  return compactCurrencyFormatter.format(Number(value || '0'))
}

function formatPercentage(value: string): string {
  return `${Number(value || '0').toFixed(2)}%`
}

function formatDate(value: string): string {
  return dateFormatter.format(new Date(value))
}

function formatDateTime(value: string): string {
  return dateTimeFormatter.format(new Date(value))
}

function formatDay(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

function sessionLabel(sessionId: string | null): string {
  if (!sessionId) {
    return 'Sem sessão'
  }

  const session = [...filterSessions.value, ...cashRegisters.value].find(
    (item) => item.id === sessionId
  )
  const base = session
    ? new Date(session.opened_at).toLocaleDateString('pt-BR')
    : sessionId.slice(0, 8).toUpperCase()
  return session?.status === 'OPEN' ? `${base} · Aberto` : base
}

function paymentMethodLabel(value: PaymentMethod): string {
  return {
    CASH: 'Dinheiro',
    PIX: 'Pix',
    DEBIT_CARD: 'Débito',
    CREDIT_CARD: 'Crédito',
    MIXED: 'Misto'
  }[value]
}

function expenseCategoryLabel(value: ExpenseCategory): string {
  return {
    INGREDIENTS: 'Ingredientes',
    PACKAGING: 'Embalagens',
    UTILITIES: 'Utilidades',
    MAINTENANCE: 'Manutencao',
    CLEANING: 'Limpeza',
    WITHDRAWAL: 'Retirada',
    PERSONAL_USE: 'Uso pessoal',
    OTHER: 'Outros'
  }[value]
}

function differenceTone(value: string | null): string {
  const amount = Number(value || '0')
  if (amount > 0) {
    return 'text-emerald-700'
  }
  if (amount < 0) {
    return 'text-rose-600'
  }
  return 'text-zinc-950'
}

function toneByAmount(value: string): string {
  const amount = Number(value || '0')
  if (amount > 0) {
    return 'text-emerald-700'
  }
  if (amount < 0) {
    return 'text-rose-600'
  }
  return 'text-zinc-950'
}

function expenseTagSeverity(
  value: ExpenseCategory
): 'danger' | 'warn' | 'secondary' {
  if (value === 'WITHDRAWAL' || value === 'PERSONAL_USE') {
    return 'danger'
  }
  if (value === 'UTILITIES' || value === 'MAINTENANCE') {
    return 'warn'
  }
  return 'secondary'
}

function columnHeight(value: string, maxValue: number): number {
  const amount = Number(value || '0')
  if (amount <= 0) {
    return 0
  }
  return Math.max(14, Math.round((amount / maxValue) * 100))
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

function displayError(message: string): void {
  errorMessage.value = message
  showErrorDialog.value = true
}

function applyTodayFilter(): void {
  const today = todayDate()
  filters.value.start_date = today
  filters.value.end_date = today
  void loadReports()
}

function applyLast7DaysFilter(): void {
  filters.value.start_date = daysAgo(6)
  filters.value.end_date = todayDate()
  void loadReports()
}

function clearFilters(): void {
  filters.value.start_date = ''
  filters.value.end_date = ''
  filters.value.category_id = ''
  filters.value.payment_method = ''
  filters.value.user_id = ''
  filters.value.cash_register_session_id = ''
  void loadReports()
}

async function loadReferenceData(): Promise<void> {
  const [loadedCategories, loadedUsers, loadedSessions] = await Promise.all([
    listCategories(),
    listUsers(),
    listCashRegisterHistory()
  ])

  categories.value = loadedCategories
  users.value = loadedUsers
  filterSessions.value = loadedSessions
}

async function loadReports(): Promise<void> {
  isLoading.value = true

  try {
    const reportFilters = buildFilters()
    const [
      sales,
      products,
      categoriesReport,
      payments,
      hourly,
      cashReport,
      expenses
    ] = await Promise.all([
      listSalesReport(reportFilters),
      listProductReport(reportFilters),
      listCategoryReport(reportFilters),
      listPaymentMethodReport(reportFilters),
      listHourlySalesReport(reportFilters),
      listCashRegisterReport(reportFilters),
      listExpenseAnalysisReport(reportFilters)
    ])

    salesSummary.value = sales
    productPerformance.value = products
    categoryPerformance.value = categoriesReport
    paymentMethods.value = payments
    hourlySales.value = hourly
    cashRegisters.value = cashReport
    expenseAnalysis.value = expenses
  } catch (error) {
    displayError(readError(error, 'Não foi possível carregar os relatórios.'))
  } finally {
    isLoading.value = false
  }
}

async function refreshPage(): Promise<void> {
  isLoading.value = true

  try {
    await loadReferenceData()
    await loadReports()
  } catch (error) {
    isLoading.value = false
    displayError(
      readError(error, 'Não foi possível atualizar os dados dos relatórios.')
    )
  }
}

async function openDetails(sessionId: string): Promise<void> {
  detailLoading.value = true
  showDetailDialog.value = true

  try {
    const [sessionDetail, sessionExpenses] = await Promise.all([
      getCashRegisterSession(sessionId),
      listExpenses({ cash_register_session_id: sessionId })
    ])
    selectedSession.value = sessionDetail
    selectedSessionExpenses.value = sessionExpenses
  } catch (error) {
    showDetailDialog.value = false
    displayError(
      readError(error, 'Não foi possível carregar os detalhes da sessão.')
    )
  } finally {
    detailLoading.value = false
  }
}

watchEffect(() => {
  setTopbar({
    badge: {
      value: activeReportMeta.value.label,
      severity: 'secondary'
    },
    actions: [
      {
        key: 'refresh-reports',
        label: 'Atualizar',
        severity: 'secondary',
        outlined: true,
        onClick: () => {
          void refreshPage()
        }
      }
    ]
  })
})

onMounted(async () => {
  await refreshPage()
})

onBeforeUnmount(() => {
  clearTopbar()
})
</script>
