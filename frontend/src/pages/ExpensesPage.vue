<template>
  <section class="app-page flex flex-col gap-4">
    <div class="ops-kpi-grid">
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Despesas filtradas</span>
        <strong class="ops-kpi-value">{{ expenses.length }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Total filtrado</span>
        <strong class="ops-kpi-value">{{ formatCurrency(totalExpenses) }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Saida em dinheiro</span>
        <strong class="ops-kpi-value">{{ formatCurrency(cashExpenses) }}</strong>
      </div>
      <div class="ops-kpi-card">
        <span class="ops-kpi-label">Sessao aberta</span>
        <strong class="ops-kpi-value">{{ currentSession ? sessionLabel(currentSession.id) : 'Sem caixa aberto' }}</strong>
      </div>
    </div>

    <section class="pos-surface pos-stage-panel">
      <div class="ops-filter-grid">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="expense-start-date">Data inicial</label>
          <InputText id="expense-start-date" v-model="filters.start_date" type="date" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="expense-end-date">Data final</label>
          <InputText id="expense-end-date" v-model="filters.end_date" type="date" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="expense-category-filter">Categoria</label>
          <Select id="expense-category-filter" v-model="filters.category" :options="categoryFilterOptions" option-label="label" option-value="value" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="expense-session-filter">Sessao</label>
          <Select id="expense-session-filter" v-model="filters.cash_register_session_id" :options="sessionFilterOptions" option-label="label" option-value="value" />
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <Button label="Aplicar filtros" @click="loadExpenses" />
        <Button label="Hoje" severity="secondary" outlined @click="applyTodayFilter" />
        <Button label="Limpar" severity="secondary" text @click="clearFilters" />
      </div>
    </section>

    <section class="pos-surface pos-stage-panel">
      <div v-if="isLoading" class="flex min-h-[16rem] items-center justify-center">
        <ProgressSpinner stroke-width="4" />
      </div>

      <div v-else class="flex flex-col gap-4">
        <div v-if="expenses.length === 0" class="pos-empty-state !min-h-[14rem]">
          <div class="text-4xl">💸</div>
          <div class="mt-2 text-base font-semibold text-zinc-700">Nenhuma despesa encontrada</div>
          <div class="mt-1 text-sm text-zinc-500">Ajuste o filtro ou registre uma nova saida.</div>
        </div>

        <DataTable v-else :value="expenses" size="small" striped-rows>
          <Column header="Data">
            <template #body="slotProps">
              {{ formatDate(slotProps.data.expense_date) }}
            </template>
          </Column>

          <Column field="description" header="Descricao" />

          <Column header="Categoria">
            <template #body="slotProps">
              <Tag severity="secondary" :value="categoryLabel(slotProps.data.category)" />
            </template>
          </Column>

          <Column header="Pagamento">
            <template #body="slotProps">
              <Tag :severity="slotProps.data.payment_method === 'CASH' ? 'success' : 'secondary'" :value="paymentMethodLabel(slotProps.data.payment_method)" />
            </template>
          </Column>

          <Column header="Sessao">
            <template #body="slotProps">
              {{ sessionLabel(slotProps.data.cash_register_session_id) }}
            </template>
          </Column>

          <Column header="Valor">
            <template #body="slotProps">
              <span class="font-semibold text-zinc-950">{{ formatCurrency(slotProps.data.amount) }}</span>
            </template>
          </Column>

          <Column header="Acoes">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button label="Editar" size="small" severity="secondary" outlined @click="openEditDialog(slotProps.data)" />
                <Button label="Excluir" size="small" severity="danger" text @click="confirmDelete(slotProps.data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </section>

    <Dialog v-model:visible="showFormDialog" modal :header="editingExpenseId ? 'Editar despesa' : 'Nova despesa'" :style="{ width: '40rem', maxWidth: '95vw' }">
      <form class="flex flex-col gap-4" @submit.prevent="submitExpense">
        <div class="grid gap-4 md:grid-cols-2">
          <div class="flex flex-col gap-2 md:col-span-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-description">Descricao</label>
            <InputText id="expense-description" v-model="form.description" placeholder="Ex.: Compra de embalagem" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-amount">Valor</label>
            <InputText id="expense-amount" v-model="form.amount" type="number" inputmode="decimal" min="0" step="0.01" placeholder="0.00" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-date">Data da despesa</label>
            <InputText id="expense-date" v-model="form.expense_date" type="date" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-category">Categoria</label>
            <Select id="expense-category" v-model="form.category" :options="categoryOptions" option-label="label" option-value="value" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-payment">Pagamento</label>
            <Select id="expense-payment" v-model="form.payment_method" :options="paymentMethodOptions" option-label="label" option-value="value" />
          </div>

          <div class="flex flex-col gap-2 md:col-span-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-session">Vincular ao caixa</label>
            <Select id="expense-session" v-model="form.cash_register_session_id" :options="formSessionOptions" option-label="label" option-value="value" />
          </div>

          <div class="flex flex-col gap-2 md:col-span-2">
            <label class="text-sm font-medium text-zinc-700" for="expense-notes">Observacoes</label>
            <Textarea id="expense-notes" v-model="form.notes" rows="4" auto-resize />
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <Button label="Cancelar" severity="secondary" text @click="showFormDialog = false" />
          <Button type="submit" :label="isSubmitting ? 'Salvando...' : editingExpenseId ? 'Salvar alteracoes' : 'Criar despesa'" :loading="isSubmitting" />
        </div>
      </form>
    </Dialog>

    <Dialog v-model:visible="showDeleteDialog" modal header="Excluir despesa" :style="{ width: '28rem', maxWidth: '92vw' }">
      <div class="text-sm leading-6 text-zinc-700">
        Excluir a despesa <strong>{{ expenseToDelete?.description }}</strong> no valor de {{ formatCurrency(expenseToDelete?.amount ?? '0.00') }}?
      </div>

      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="showDeleteDialog = false" />
        <Button label="Excluir" severity="danger" :loading="isSubmitting" @click="removeExpense" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showErrorDialog" modal header="Atenção" :style="{ width: '28rem', maxWidth: '92vw' }">
      <div class="text-sm leading-6 text-zinc-700">{{ errorMessage }}</div>

      <template #footer>
        <Button label="Fechar" severity="secondary" @click="showErrorDialog = false" />
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
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'

import { useAppTopbar } from '@/composables/useAppTopbar'
import { getCurrentCashRegister, listCashRegisterHistory } from '@/services/cashRegister'
import { createExpense, deleteExpense, listExpenses, updateExpense } from '@/services/expenses'
import { ApiError } from '@/services/http'
import type { CashRegisterSession } from '@/types/cashRegister'
import type { Expense, ExpenseCategory, ExpensePayload } from '@/types/expense'
import type { PaymentMethod } from '@/types/sale'

interface ExpenseFormState {
  description: string
  amount: string
  category: ExpenseCategory
  payment_method: PaymentMethod
  notes: string
  cash_register_session_id: string
  expense_date: string
}

const toast = useToast()
const { setTopbar, clearTopbar } = useAppTopbar()

const expenses = ref<Expense[]>([])
const currentSession = ref<CashRegisterSession | null>(null)
const historySessions = ref<CashRegisterSession[]>([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const showFormDialog = ref(false)
const showDeleteDialog = ref(false)
const showErrorDialog = ref(false)
const editingExpenseId = ref<string | null>(null)
const expenseToDelete = ref<Expense | null>(null)
const errorMessage = ref('')

const filters = ref({
  start_date: todayDate(),
  end_date: todayDate(),
  category: '',
  cash_register_session_id: ''
})

const form = ref<ExpenseFormState>(createEmptyForm())

const categoryOptions: Array<{ label: string; value: ExpenseCategory }> = [
  { label: 'Ingredientes', value: 'INGREDIENTS' },
  { label: 'Embalagens', value: 'PACKAGING' },
  { label: 'Utilidades', value: 'UTILITIES' },
  { label: 'Manutencao', value: 'MAINTENANCE' },
  { label: 'Limpeza', value: 'CLEANING' },
  { label: 'Retirada', value: 'WITHDRAWAL' },
  { label: 'Uso pessoal', value: 'PERSONAL_USE' },
  { label: 'Outros', value: 'OTHER' }
]

const paymentMethodOptions: Array<{ label: string; value: PaymentMethod }> = [
  { label: 'Dinheiro', value: 'CASH' },
  { label: 'Pix', value: 'PIX' },
  { label: 'Debito', value: 'DEBIT_CARD' },
  { label: 'Credito', value: 'CREDIT_CARD' },
  { label: 'Misto', value: 'MIXED' }
]

const categoryFilterOptions = computed(() => [{ label: 'Todas', value: '' }, ...categoryOptions])

const sessionOptions = computed(() => {
  const seen = new Set<string>()
  const items = [currentSession.value, ...historySessions.value].filter(
    (session): session is CashRegisterSession => Boolean(session)
  )

  return items.filter((session) => {
    if (seen.has(session.id)) {
      return false
    }
    seen.add(session.id)
    return true
  })
})

const sessionFilterOptions = computed(() => [
  { label: 'Todas as sessoes', value: '' },
  ...sessionOptions.value.map((session) => ({ label: sessionLabel(session.id), value: session.id }))
])

const formSessionOptions = computed(() => [
  { label: 'Sem vinculo de caixa', value: '' },
  ...sessionOptions.value.map((session) => ({ label: sessionLabel(session.id), value: session.id }))
])

const totalExpenses = computed(() =>
  expenses.value.reduce((sum, expense) => sum + Number(expense.amount), 0).toFixed(2)
)

const cashExpenses = computed(() =>
  expenses.value
    .filter((expense) => expense.payment_method === 'CASH')
    .reduce((sum, expense) => sum + Number(expense.amount), 0)
    .toFixed(2)
)

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const dateFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})

function todayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function createEmptyForm(): ExpenseFormState {
  return {
    description: '',
    amount: '',
    category: 'INGREDIENTS',
    payment_method: 'CASH',
    notes: '',
    cash_register_session_id: '',
    expense_date: todayDate()
  }
}

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value || '0'))
}

function formatDate(value: string): string {
  return dateFormatter.format(new Date(value))
}

function paymentMethodLabel(value: PaymentMethod): string {
  return paymentMethodOptions.find((option) => option.value === value)?.label ?? value
}

function categoryLabel(value: ExpenseCategory): string {
  return categoryOptions.find((option) => option.value === value)?.label ?? value
}

function sessionLabel(sessionId: string | null): string {
  if (!sessionId) {
    return 'Sem sessao'
  }

  const session = sessionOptions.value.find((item) => item.id === sessionId)
  const base = session ? new Date(session.opened_at).toLocaleDateString('pt-BR') : sessionId.slice(0, 8).toUpperCase()
  return session?.status === 'OPEN' ? `${base} · Aberto` : base
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

function expenseDateToIso(value: string): string | null {
  if (!value) {
    return null
  }
  return new Date(`${value}T12:00:00`).toISOString()
}

function buildFilters() {
  return {
    start_date: filters.value.start_date || undefined,
    end_date: filters.value.end_date || undefined,
    category: (filters.value.category || undefined) as ExpenseCategory | undefined,
    cash_register_session_id: filters.value.cash_register_session_id || undefined
  }
}

function buildPayload(): ExpensePayload {
  return {
    description: form.value.description.trim(),
    amount: form.value.amount,
    category: form.value.category,
    payment_method: form.value.payment_method,
    notes: form.value.notes.trim() || null,
    cash_register_session_id: form.value.cash_register_session_id || null,
    expense_date: expenseDateToIso(form.value.expense_date)
  }
}

function applyTodayFilter(): void {
  filters.value.start_date = todayDate()
  filters.value.end_date = todayDate()
}

function clearFilters(): void {
  filters.value = {
    start_date: '',
    end_date: '',
    category: '',
    cash_register_session_id: ''
  }
  void loadExpenses()
}

function openCreateDialog(): void {
  editingExpenseId.value = null
  form.value = createEmptyForm()
  if (currentSession.value?.status === 'OPEN') {
    form.value.cash_register_session_id = currentSession.value.id
  }
  showFormDialog.value = true
}

function openEditDialog(expense: Expense): void {
  editingExpenseId.value = expense.id
  form.value = {
    description: expense.description,
    amount: expense.amount,
    category: expense.category,
    payment_method: expense.payment_method,
    notes: expense.notes ?? '',
    cash_register_session_id: expense.cash_register_session_id ?? '',
    expense_date: expense.expense_date.slice(0, 10)
  }
  showFormDialog.value = true
}

function confirmDelete(expense: Expense): void {
  expenseToDelete.value = expense
  showDeleteDialog.value = true
}

async function loadSupportingData(): Promise<void> {
  const [nextCurrent, nextHistory] = await Promise.all([
    getCurrentCashRegister().catch((error: unknown) => {
      if (error instanceof ApiError && error.status === 404) {
        return null
      }
      throw error
    }),
    listCashRegisterHistory().catch(() => [])
  ])

  currentSession.value = nextCurrent
  historySessions.value = nextHistory
}

async function loadExpenses(): Promise<void> {
  isLoading.value = true

  try {
    expenses.value = await listExpenses(buildFilters())
  } catch (error) {
    displayError(readError(error, 'Nao foi possivel carregar as despesas.'))
  } finally {
    isLoading.value = false
  }
}

async function refreshPage(): Promise<void> {
  isLoading.value = true

  try {
    await Promise.all([loadSupportingData(), loadExpenses()])
  } catch (error) {
    displayError(readError(error, 'Nao foi possivel carregar a tela de despesas.'))
    isLoading.value = false
  }
}

async function submitExpense(): Promise<void> {
  isSubmitting.value = true

  try {
    const payload = buildPayload()

    if (editingExpenseId.value) {
      await updateExpense(editingExpenseId.value, payload)
      toast.add({ severity: 'success', summary: 'Despesa atualizada', life: 2200 })
    } else {
      await createExpense(payload)
      toast.add({ severity: 'success', summary: 'Despesa registrada', life: 2200 })
    }

    showFormDialog.value = false
    form.value = createEmptyForm()
    await refreshPage()
  } catch (error) {
    displayError(readError(error, 'Nao foi possivel salvar a despesa.'))
  } finally {
    isSubmitting.value = false
  }
}

async function removeExpense(): Promise<void> {
  if (!expenseToDelete.value) {
    return
  }

  isSubmitting.value = true

  try {
    await deleteExpense(expenseToDelete.value.id)
    showDeleteDialog.value = false
    expenseToDelete.value = null
    toast.add({ severity: 'success', summary: 'Despesa excluida', life: 2200 })
    await refreshPage()
  } catch (error) {
    displayError(readError(error, 'Nao foi possivel excluir a despesa.'))
  } finally {
    isSubmitting.value = false
  }
}

watchEffect(() => {
  setTopbar({
    actions: [
      {
        key: 'refresh-expenses',
        label: 'Atualizar',
        severity: 'secondary',
        outlined: true,
        onClick: () => {
          void refreshPage()
        }
      },
      {
        key: 'create-expense',
        label: 'Nova despesa',
        severity: 'contrast',
        onClick: openCreateDialog
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
