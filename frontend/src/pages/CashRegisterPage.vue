<template>
  <section class="pos-workspace">
    <div class="pos-topbar">
      <div class="pos-topbar-brand">
        <div class="rounded-xl bg-emerald-50 p-2 text-emerald-700">☑</div>
        <div>
          <div class="text-base font-semibold text-zinc-950">PDV Local</div>
          <div
            class="text-[11px] font-medium uppercase tracking-[0.16em] text-emerald-600"
          >
            ONLINE
          </div>
        </div>
      </div>

      <div class="pos-topbar-group">
        <div class="flex items-center gap-2">
          <Tag :severity="statusSeverity" :value="statusLabel" />
          <span class="text-sm font-semibold text-emerald-700">{{
            openedTimeTitle
          }}</span>
        </div>
        <span class="text-xs text-zinc-500"
          >Abertura:
          {{ formatCurrency(session?.opening_amount ?? '0.00') }}</span
        >
      </div>

      <div class="pos-topbar-metrics">
        <div class="pos-topbar-metric">
          <span class="pos-topbar-metric-label">Qtd. vendas</span>
          <span class="pos-topbar-metric-value">{{
            session?.totals.sales_count ?? 0
          }}</span>
        </div>

        <div class="pos-topbar-metric">
          <span class="pos-topbar-metric-label">Total recebido</span>
          <span class="pos-topbar-metric-value">{{
            formatCurrency(session?.totals.total_received_amount ?? '0.00')
          }}</span>
        </div>

        <div class="pos-topbar-metric">
          <span class="pos-topbar-metric-label">Ultima venda</span>
          <span class="pos-topbar-metric-value">{{ lastSaleLabel }}</span>
        </div>

        <div class="pos-topbar-metric">
          <span class="pos-topbar-metric-label">Diferença do caixa</span>
          <span
            class="pos-topbar-metric-value"
            :class="
              Number(closingDifferenceDisplay) < 0
                ? 'text-rose-600'
                : 'text-zinc-950'
            "
          >
            {{ formatCurrency(closingDifferenceDisplay) }}
          </span>
        </div>
      </div>

      <div class="pos-topbar-actions">
        <Button
          size="small"
          label="Mais opções (F11)"
          severity="secondary"
          outlined
          @click="openMoreOptions"
        />
        <Button
          size="small"
          label="Atalhos (F2)"
          severity="secondary"
          outlined
          @click="showShortcutDialog = true"
        />
        <Button
          size="small"
          label="Fechar caixa (F12)"
          severity="danger"
          outlined
          :disabled="viewState !== 'open' || !authStore.isOwner"
          @click="requestCloseConfirmation"
        />
      </div>

      <div class="pos-topbar-user">
        <div class="text-sm font-semibold text-zinc-950">
          {{ authStore.user?.full_name ?? 'Sem sessão' }}
        </div>
        <div class="text-xs text-zinc-500">
          {{ authStore.isOwner ? 'Proprietário' : 'Funcionário' }}
        </div>
      </div>

      <Button
        size="small"
        label="Sair"
        severity="secondary"
        outlined
        @click="handleLogout"
      />
    </div>

    <div
      v-if="isLoading"
      class="flex min-h-[26rem] items-center justify-center"
    >
      <ProgressSpinner stroke-width="4" />
    </div>

    <div
      v-else-if="viewState !== 'open'"
      class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]"
    >
      <Card class="border border-zinc-200">
        <template #title>Abrir caixa</template>
        <template #content>
          <form
            class="flex max-w-md flex-col gap-4"
            @submit.prevent="submitOpen"
          >
            <div class="flex flex-col gap-2">
              <label
                class="text-sm font-medium text-zinc-700"
                for="opening-amount"
                >Valor inicial</label
              >
              <InputText
                id="opening-amount"
                v-model="openingAmount"
                type="number"
                inputmode="decimal"
                min="0"
                step="0.01"
              />
            </div>

            <Button
              type="submit"
              :label="isSubmitting ? 'Abrindo...' : 'Abrir caixa'"
              :loading="isSubmitting"
            />
          </form>
        </template>
      </Card>

      <Card class="border border-zinc-200">
        <template #title>{{
          session && viewState === 'closed'
            ? 'Último fechamento'
            : 'Caixa fechado'
        }}</template>
        <template #content>
          <div
            v-if="session && viewState === 'closed'"
            class="grid gap-3 md:grid-cols-3"
          >
            <div class="pos-summary-tile">
              <div
                class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
              >
                Abertura
              </div>
              <div class="mt-2 text-lg font-semibold text-zinc-950">
                {{ formatCurrency(session.opening_amount) }}
              </div>
            </div>
            <div class="pos-summary-tile">
              <div
                class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
              >
                Fechamento
              </div>
              <div class="mt-2 text-lg font-semibold text-zinc-950">
                {{ formatCurrency(session.closing_amount ?? '0.00') }}
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
                :class="
                  Number(session.difference_amount ?? '0') < 0
                    ? 'text-rose-600'
                    : 'text-zinc-950'
                "
              >
                {{ formatCurrency(session.difference_amount ?? '0.00') }}
              </div>
            </div>
          </div>

          <p v-else class="text-sm text-zinc-600">
            Abra o caixa para liberar vendas neste terminal.
          </p>
        </template>
      </Card>
    </div>

    <template v-else>
      <div class="pos-main-grid">
        <section class="pos-surface pos-stage-panel pos-products-panel">
          <InputGroup>
            <InputGroupAddon>⌕</InputGroupAddon>
            <InputText
              id="pos-product-search"
              v-model="productSearch"
              placeholder="Buscar produto (digite o nome ou código)"
            />
            <InputGroupAddon>
              <Tag severity="secondary" value="F3" />
            </InputGroupAddon>
          </InputGroup>

          <PosCategoryFilter
            v-model="selectedCategoryId"
            :categories="categories"
          />

          <Message
            v-if="filteredProducts.length === 0"
            severity="warn"
            :closable="false"
            >Nenhum produto encontrado.</Message
          >

          <div v-else class="pos-product-grid">
            <PosProductCard
              v-for="(product, index) in visibleShortcutProducts"
              :key="product.id"
              :product="product"
              :category-label="categoryNameById(product.category_id)"
              :shortcut="productShortcutLabel(index)"
              :active="selectedCartProductId === product.id"
              @add="addToCart"
            />
          </div>

          <div class="pos-products-footer">
            <div class="grid gap-2">
              <Button
                class="pos-quick-action"
                severity="danger"
                outlined
                @click="cancelSelectedItem"
              >
                <template #default>
                  <div class="flex w-full flex-col items-start gap-1 text-left">
                    <span class="text-base font-semibold">Cancelar item</span>
                    <span class="text-xs opacity-70">F6</span>
                  </div>
                </template>
              </Button>
            </div>
          </div>
        </section>

        <div class="flex min-h-0 flex-col gap-4">
          <PosCartPanel
            :lines="cart"
            :total="cartTotal"
            :selected-product-id="selectedCartProductId"
            @select="selectCartItem"
            @clear="clearCart"
            @increase="increaseQuantity"
            @decrease="decreaseQuantity"
            @remove="removeFromCart"
          />

          <section class="pos-surface pos-stage-panel flex flex-col gap-4">
            <div class="text-lg font-semibold text-zinc-950">Pagamento</div>

            <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              <Button
                v-for="method in paymentMethods"
                :key="method.value"
                fluid
                class="pos-payment-button"
                :severity="
                  selectedPaymentMethod === method.value
                    ? 'success'
                    : 'secondary'
                "
                :outlined="selectedPaymentMethod !== method.value"
                @click="selectPaymentMethod(method.value)"
              >
                <template #default>
                  <div class="flex w-full items-center justify-between gap-3">
                    <span class="text-2xl leading-none">{{ method.icon }}</span>
                    <span class="text-sm font-semibold">{{
                      method.label
                    }}</span>
                  </div>
                </template>
              </Button>
            </div>

            <div
              v-if="selectedPaymentMethod === 'CASH'"
              class="grid gap-4 sm:grid-cols-2"
            >
              <div class="flex flex-col gap-2">
                <label
                  class="text-sm font-medium text-zinc-700"
                  for="cash-received-amount"
                  >Valor recebido</label
                >
                <InputText
                  id="cash-received-amount"
                  v-model="cashReceivedAmount"
                  type="number"
                  inputmode="decimal"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                />
              </div>

              <div class="pos-summary-tile">
                <div
                  class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
                >
                  Troco
                </div>
                <div class="mt-1 text-xl font-semibold text-sky-700">
                  {{ changePreview }}
                </div>
              </div>
            </div>

            <div
              v-if="selectedPaymentMethod === 'MIXED'"
              class="grid gap-3 sm:grid-cols-2"
            >
              <div
                v-for="field in mixedFields"
                :key="field.key"
                class="flex flex-col gap-2"
              >
                <label class="text-sm font-medium text-zinc-700">{{
                  field.label
                }}</label>
                <InputText
                  v-model="paymentSplit[field.key]"
                  type="number"
                  inputmode="decimal"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>

            <div class="grid gap-3 md:grid-cols-2">
              <div class="pos-summary-tile">
                <div class="text-sm font-medium text-zinc-500">
                  Total da venda
                </div>
                <div class="mt-1 text-3xl font-semibold text-emerald-700">
                  {{ formatCurrency(cartTotal) }}
                </div>
              </div>

              <div class="pos-summary-tile">
                <div class="text-sm font-medium text-zinc-500">
                  Status do pagamento
                </div>
                <div
                  class="mt-2 text-lg font-semibold"
                  :class="paymentStatusTone"
                >
                  {{ paymentStatusLabel }}
                </div>
                <div class="mt-1 text-sm text-zinc-500">
                  {{ paymentStatusDetail }}
                </div>
              </div>
            </div>

            <Button
              class="pos-payment-button"
              size="large"
              severity="success"
              :disabled="cart.length === 0"
              @click="requestSaleConfirmation"
            >
              <template #default>
                <div class="flex w-full items-center justify-between gap-4">
                  <div class="flex flex-col items-start text-left">
                    <span class="text-xs uppercase tracking-[0.2em] opacity-80"
                      >F10</span
                    >
                    <span class="text-base font-semibold">Confirmar venda</span>
                  </div>
                  <span class="text-xl font-semibold">{{
                    formatCurrency(cartTotal)
                  }}</span>
                </div>
              </template>
            </Button>
          </section>
        </div>
      </div>
    </template>

    <Dialog
      v-model:visible="showConfirmSaleDialog"
      modal
      header="Confirmar venda"
      :style="{ width: '32rem', maxWidth: '95vw' }"
    >
      <div class="flex flex-col gap-4">
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Itens
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ cartItemCount }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Pagamento
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ selectedPaymentLabel }}
            </div>
          </div>
        </div>

        <div
          class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-5"
        >
          <div class="text-sm font-medium text-emerald-700">
            Total confirmado
          </div>
          <div class="mt-2 text-4xl font-semibold text-emerald-700">
            {{ formatCurrency(cartTotal) }}
          </div>
          <div class="mt-2 text-sm text-emerald-700/80">
            {{ paymentStatusDetail }}
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Voltar"
          severity="secondary"
          text
          @click="showConfirmSaleDialog = false"
        />
        <Button
          label="Finalizar venda"
          severity="success"
          :loading="isSubmitting"
          @click="submitSale"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showCloseDialog"
      modal
      header="Fechar caixa"
      :style="{ width: '32rem', maxWidth: '95vw' }"
    >
      <div class="flex flex-col gap-4">
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Abertura
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(session?.opening_amount ?? '0.00') }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Caixa esperado
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(session?.expected_amount ?? '0.00') }}
            </div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Venda dinheiro
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(session?.totals.cash_sales_amount ?? '0.00') }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Venda pix
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(session?.totals.pix_sales_amount ?? '0.00') }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Venda débito
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{
                formatCurrency(
                  session?.totals.debit_card_sales_amount ?? '0.00'
                )
              }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Venda crédito
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{
                formatCurrency(
                  session?.totals.credit_card_sales_amount ?? '0.00'
                )
              }}
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Venda mista
            </div>
            <div class="mt-2 text-base font-semibold text-zinc-950">
              {{ formatCurrency(session?.totals.mixed_sales_amount ?? '0.00') }}
            </div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Despesas
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{ formatCurrency(session?.totals.expenses_amount ?? '0.00') }}
            </div>
            <div class="mt-1 text-xs text-zinc-500">
              Total de saidas registradas
            </div>
          </div>
          <div class="pos-summary-tile">
            <div
              class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500"
            >
              Despesas em dinheiro
            </div>
            <div class="mt-2 text-lg font-semibold text-zinc-950">
              {{
                formatCurrency(session?.totals.cash_expenses_amount ?? '0.00')
              }}
            </div>
            <div class="mt-1 text-xs text-zinc-500">Sai do caixa fisico</div>
          </div>
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <div class="flex flex-col gap-2">
            <label
              class="text-sm font-medium text-zinc-700"
              for="closing-amount-modal"
              >Valor contado (dinheiro)</label
            >
            <InputText
              id="closing-amount-modal"
              v-model="closingAmount"
              type="number"
              inputmode="decimal"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label
              class="text-sm font-medium text-zinc-700"
              for="owner-pin-close"
              >PIN do proprietário</label
            >
            <Password
              id="owner-pin-close"
              v-model="ownerPin"
              toggle-mask
              :feedback="false"
              inputmode="numeric"
              fluid
            />
          </div>
        </div>

        <div class="rounded-2xl border border-zinc-200 bg-zinc-50 px-4 py-4">
          <div class="text-sm font-medium text-zinc-500">
            Diferença do fechamento
          </div>
          <div
            class="mt-2 text-3xl font-semibold"
            :class="closingDifferenceTone"
          >
            {{ formatCurrency(closingDifferenceDisplay) }}
          </div>
          <div class="mt-1 text-sm font-medium" :class="closingDifferenceTone">
            {{ closingDifferenceLabel }}
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Voltar"
          severity="secondary"
          text
          @click="showCloseDialog = false"
        />
        <Button
          label="Confirmar fechamento"
          severity="danger"
          :loading="isSubmitting"
          @click="submitClose"
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

    <PosShortcutDialog v-model="showShortcutDialog" />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'

import PosCartPanel from '@/components/pos/PosCartPanel.vue'
import PosCategoryFilter from '@/components/pos/PosCategoryFilter.vue'
import PosProductCard from '@/components/pos/PosProductCard.vue'
import PosShortcutDialog from '@/components/pos/PosShortcutDialog.vue'
import { PRODUCT_SHORTCUT_KEYS } from '@/components/pos/visuals'
import { usePosKeyboardShortcuts } from '@/composables/usePosKeyboardShortcuts'
import { listCategories, listProducts } from '@/services/catalog'
import {
  clearLastClosedSession,
  closeCashRegister,
  getCurrentCashRegister,
  getLastClosedSession,
  openCashRegister,
  saveLastClosedSession
} from '@/services/cashRegister'
import { ApiError } from '@/services/http'
import { createSale } from '@/services/sales'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import type { Category, Product } from '@/types/catalog'
import type { CashRegisterSession } from '@/types/cashRegister'
import type { CreateSalePayload, PaymentMethod } from '@/types/sale'

type ViewState = 'loading' | 'empty' | 'open' | 'closed'

interface CartLine {
  product: Product
  quantity: number
  total: string
}

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()
const uiStore = useUiStore()

const isLoading = ref(true)
const isSubmitting = ref(false)
const viewState = ref<ViewState>('loading')
const session = ref<CashRegisterSession | null>(null)
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const productSearch = ref('')
const selectedCategoryId = ref('all')
const openingAmount = ref('0.00')
const closingAmount = ref('')
const ownerPin = ref('')
const cart = ref<CartLine[]>([])
const selectedCartProductId = ref<string | null>(null)
const selectedPaymentMethod = ref<PaymentMethod>('CASH')
const cashReceivedAmount = ref('')
const showShortcutDialog = ref(false)
const showConfirmSaleDialog = ref(false)
const showCloseDialog = ref(false)
const showErrorDialog = ref(false)
const paymentSplit = ref({
  cash_amount: '',
  pix_amount: '',
  debit_card_amount: '',
  credit_card_amount: ''
})
const errorMessage = ref('')

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
  hour: '2-digit',
  minute: '2-digit'
})

const paymentMethods: Array<{
  value: PaymentMethod
  label: string
  icon: string
}> = [
  { value: 'CASH', label: 'Dinheiro', icon: '💵' },
  { value: 'PIX', label: 'Pix', icon: '🔗' },
  { value: 'DEBIT_CARD', label: 'Débito', icon: '💳' },
  { value: 'CREDIT_CARD', label: 'Crédito', icon: '💠' },
  { value: 'MIXED', label: 'Misto', icon: '🧾' }
]

const mixedFields = [
  { key: 'cash_amount', label: 'Dinheiro' },
  { key: 'pix_amount', label: 'Pix' },
  { key: 'debit_card_amount', label: 'Débito' },
  { key: 'credit_card_amount', label: 'Crédito' }
] as const

const cartTotalNumber = computed(() =>
  cart.value.reduce((sum, line) => sum + Number(line.total), 0)
)

const cartTotal = computed(() => cartTotalNumber.value.toFixed(2))
const cartItemCount = computed(() =>
  cart.value.reduce((sum, line) => sum + line.quantity, 0)
)
const cashReceivedNumber = computed(() =>
  Number(cashReceivedAmount.value || '0')
)
const mixedTotalNumber = computed(() =>
  Object.values(paymentSplit.value).reduce(
    (sum, amount) => sum + Number(amount || '0'),
    0
  )
)
const closingDifferenceDisplay = computed(() => {
  if (!session.value) {
    return '0.00'
  }
  if (closingAmount.value) {
    return (
      Number(closingAmount.value) - Number(session.value.expected_amount)
    ).toFixed(2)
  }
  return session.value.difference_amount ?? '0.00'
})
const closingDifferenceNumber = computed(() =>
  Number(closingDifferenceDisplay.value || '0')
)
const closingDifferenceTone = computed(() => {
  if (closingDifferenceNumber.value > 0) {
    return 'text-emerald-700'
  }
  if (closingDifferenceNumber.value < 0) {
    return 'text-rose-600'
  }
  return 'text-zinc-950'
})
const closingDifferenceLabel = computed(() => {
  if (closingDifferenceNumber.value > 0) {
    return 'Sobra no caixa'
  }
  if (closingDifferenceNumber.value < 0) {
    return 'Falta no caixa'
  }
  return 'Caixa equilibrado'
})

const filteredProducts = computed(() => {
  const searchTerm = productSearch.value.trim().toLowerCase()

  return products.value.filter((product) => {
    const matchesCategory =
      selectedCategoryId.value === 'all' ||
      product.category_id === selectedCategoryId.value
    const matchesSearch =
      !searchTerm || product.name.toLowerCase().includes(searchTerm)

    return product.is_active && matchesCategory && matchesSearch
  })
})

const visibleShortcutProducts = computed(() =>
  filteredProducts.value.slice(0, PRODUCT_SHORTCUT_KEYS.length)
)

const statusSeverity = computed(() =>
  viewState.value === 'open' ? 'success' : 'secondary'
)
const statusLabel = computed(() =>
  viewState.value === 'open' ? 'ABERTO' : 'FECHADO'
)
const openedTimeTitle = computed(() => {
  if (!session.value?.opened_at) {
    return 'Caixa fechado'
  }
  return `Caixa aberto as ${timeFormatter.format(new Date(session.value.opened_at))}`
})

const selectedPaymentLabel = computed(() => {
  return (
    paymentMethods.find(
      (method) => method.value === selectedPaymentMethod.value
    )?.label ?? 'Dinheiro'
  )
})

const changePreview = computed(() => {
  if (selectedPaymentMethod.value !== 'CASH') {
    return formatCurrency('0.00')
  }

  const change = Math.max(cashReceivedNumber.value - cartTotalNumber.value, 0)
  return formatCurrency(change.toFixed(2))
})

const paymentErrorMessage = computed(() => {
  if (cart.value.length === 0) {
    return ''
  }

  if (selectedPaymentMethod.value === 'CASH') {
    if (!cashReceivedAmount.value) {
      return 'Informe o valor recebido ou deixe o sistema assumir pagamento exato.'
    }

    if (cashReceivedNumber.value < cartTotalNumber.value) {
      return 'O valor recebido em dinheiro não pode ser menor que o total da venda.'
    }
  }

  if (selectedPaymentMethod.value === 'MIXED') {
    const difference = cartTotalNumber.value - mixedTotalNumber.value
    if (Math.abs(difference) > 0.009) {
      return difference > 0
        ? `Faltam ${formatCurrency(difference.toFixed(2))} para fechar o pagamento misto.`
        : `O pagamento misto excedeu o total em ${formatCurrency(Math.abs(difference).toFixed(2))}.`
    }
  }

  return ''
})

const paymentStatusLabel = computed(() => {
  if (!cart.value.length) {
    return 'Aguardando itens'
  }

  if (paymentErrorMessage.value) {
    return 'Ajuste necessario'
  }

  if (selectedPaymentMethod.value === 'CASH') {
    return changePreview.value === formatCurrency('0.00')
      ? 'Pagamento exato'
      : 'Troco calculado'
  }

  if (selectedPaymentMethod.value === 'MIXED') {
    return 'Misto conferido'
  }

  return 'Pronto para confirmar'
})

const paymentStatusDetail = computed(() => {
  if (!cart.value.length) {
    return 'Adicione itens para iniciar a venda.'
  }

  if (paymentErrorMessage.value) {
    return paymentErrorMessage.value
  }

  if (selectedPaymentMethod.value === 'CASH') {
    return `Troco previsto: ${changePreview.value}`
  }

  if (selectedPaymentMethod.value === 'MIXED') {
    return 'Os valores mistos fecham exatamente a venda.'
  }

  return 'Sem pendencias de pagamento.'
})

const paymentStatusTone = computed(() => {
  if (!cart.value.length) {
    return 'text-zinc-500'
  }
  return paymentErrorMessage.value ? 'text-amber-600' : 'text-emerald-700'
})

const lastSaleLabel = computed(() => {
  const value = session.value?.totals.last_sale_at
  if (!value) {
    return '--:--'
  }
  return timeFormatter.format(new Date(value))
})

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value))
}

function productShortcutLabel(index: number): string {
  return PRODUCT_SHORTCUT_KEYS[index] ?? ''
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

function resetMessages(): void {
  errorMessage.value = ''
  showErrorDialog.value = false
}

function displayError(message: string): void {
  errorMessage.value = message
  showErrorDialog.value = true
}

function focusSearchInput(): void {
  requestAnimationFrame(() => {
    const input = document.getElementById('pos-product-search')
    if (input instanceof HTMLInputElement) {
      input.focus()
      input.select()
    }
  })
}

function categoryNameById(categoryId: string): string {
  return (
    categories.value.find((category) => category.id === categoryId)?.name ??
    'Sem categoria'
  )
}

function syncSelectedCartProduct(): void {
  if (
    selectedCartProductId.value &&
    cart.value.some((line) => line.product.id === selectedCartProductId.value)
  ) {
    return
  }

  selectedCartProductId.value = cart.value.at(-1)?.product.id ?? null
}

function selectCartItem(productId: string): void {
  selectedCartProductId.value = productId
}

function addToCart(product: Product): void {
  const existing = cart.value.find((line) => line.product.id === product.id)

  if (existing) {
    existing.quantity += 1
    existing.total = (Number(product.price) * existing.quantity).toFixed(2)
    cart.value = [...cart.value]
  } else {
    cart.value = [
      ...cart.value,
      { product, quantity: 1, total: Number(product.price).toFixed(2) }
    ]
  }

  selectedCartProductId.value = product.id
}

function increaseQuantity(productId: string): void {
  const line = cart.value.find((item) => item.product.id === productId)

  if (!line) {
    return
  }

  line.quantity += 1
  line.total = (Number(line.product.price) * line.quantity).toFixed(2)
  cart.value = [...cart.value]
  selectedCartProductId.value = productId
}

function decreaseQuantity(productId: string): void {
  const line = cart.value.find((item) => item.product.id === productId)

  if (!line) {
    return
  }

  if (line.quantity === 1) {
    removeFromCart(productId)
    return
  }

  line.quantity -= 1
  line.total = (Number(line.product.price) * line.quantity).toFixed(2)
  cart.value = [...cart.value]
  selectedCartProductId.value = productId
}

function removeFromCart(productId: string): void {
  cart.value = cart.value.filter((line) => line.product.id !== productId)
  syncSelectedCartProduct()
}

function clearCart(): void {
  if (cart.value.length === 0) {
    return
  }

  cart.value = []
  selectedCartProductId.value = null
  cashReceivedAmount.value = ''
  paymentSplit.value = {
    cash_amount: '',
    pix_amount: '',
    debit_card_amount: '',
    credit_card_amount: ''
  }
  toast.add({
    severity: 'secondary',
    summary: 'Carrinho limpo',
    life: 1800
  })
}

function cancelSelectedItem(): void {
  const productId = selectedCartProductId.value ?? cart.value.at(-1)?.product.id

  if (!productId) {
    toast.add({
      severity: 'warn',
      summary: 'Nenhum item para cancelar',
      life: 1800
    })
    return
  }

  removeFromCart(productId)
}

function openMoreOptions(): void {
  uiStore.openSidebar()
}

function handleProductShortcut(shortcut: string): void {
  if (viewState.value !== 'open') {
    return
  }

  const index = PRODUCT_SHORTCUT_KEYS.indexOf(
    shortcut as (typeof PRODUCT_SHORTCUT_KEYS)[number]
  )
  const product = visibleShortcutProducts.value[index]

  if (product) {
    addToCart(product)
  }
}

function selectPaymentMethod(method: PaymentMethod): void {
  selectedPaymentMethod.value = method

  if (method !== 'MIXED') {
    paymentSplit.value = {
      cash_amount: '',
      pix_amount: '',
      debit_card_amount: '',
      credit_card_amount: ''
    }
  }

  if (method !== 'CASH') {
    cashReceivedAmount.value = ''
  }
}

function buildSalePayload(): CreateSalePayload | null {
  if (cart.value.length === 0 || viewState.value !== 'open') {
    return null
  }

  if (selectedPaymentMethod.value === 'CASH' && !cashReceivedAmount.value) {
    cashReceivedAmount.value = cartTotal.value
  }

  if (paymentErrorMessage.value) {
    displayError(paymentErrorMessage.value)
    return null
  }

  return {
    items: cart.value.map((line) => ({
      product_id: line.product.id,
      quantity: line.quantity
    })),
    payment_method: selectedPaymentMethod.value,
    ...(selectedPaymentMethod.value === 'MIXED' ? paymentSplit.value : {})
  }
}

function requestSaleConfirmation(): void {
  resetMessages()
  const payload = buildSalePayload()

  if (!payload) {
    return
  }

  showConfirmSaleDialog.value = true
}

function requestCloseConfirmation(): void {
  resetMessages()

  if (!session.value || !authStore.isOwner || viewState.value !== 'open') {
    return
  }

  if (!closingAmount.value) {
    closingAmount.value = session.value.expected_amount
  }
  ownerPin.value = ''

  showCloseDialog.value = true
}

async function loadCatalog(): Promise<void> {
  const [nextCategories, nextProducts] = await Promise.all([
    listCategories(),
    listProducts()
  ])
  categories.value = nextCategories
  products.value = nextProducts
}

async function loadCurrentSession(): Promise<void> {
  try {
    const currentSession = await getCurrentCashRegister()
    session.value = currentSession
    viewState.value = currentSession.status === 'OPEN' ? 'open' : 'closed'

    if (currentSession.status === 'OPEN') {
      clearLastClosedSession()
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      const lastClosedSession = getLastClosedSession()
      session.value = lastClosedSession
      viewState.value = lastClosedSession ? 'closed' : 'empty'
      return
    }

    displayError(readError(error, 'Não foi possível carregar o caixa.'))
    viewState.value = 'empty'
  }
}

async function refreshPage(): Promise<void> {
  isLoading.value = true
  resetMessages()

  try {
    await Promise.all([loadCatalog(), loadCurrentSession()])
    if (viewState.value === 'open') {
      focusSearchInput()
    }
  } finally {
    isLoading.value = false
  }
}

async function submitOpen(): Promise<void> {
  if (!openingAmount.value) {
    displayError('Informe o valor de abertura.')
    return
  }

  isSubmitting.value = true
  resetMessages()

  try {
    const openedSession = await openCashRegister({
      opening_amount: openingAmount.value
    })
    session.value = openedSession
    clearLastClosedSession()
    viewState.value = 'open'
    toast.add({
      severity: 'success',
      summary: 'Caixa aberto',
      detail: `Abertura registrada em ${formatCurrency(openedSession.opening_amount)}`,
      life: 2200
    })
    focusSearchInput()
  } catch (error) {
    displayError(readError(error, 'Não foi possível abrir o caixa.'))
  } finally {
    isSubmitting.value = false
  }
}

async function submitSale(): Promise<void> {
  const payload = buildSalePayload()
  if (!payload) {
    showConfirmSaleDialog.value = false
    return
  }

  isSubmitting.value = true
  resetMessages()

  try {
    const paymentLabel = selectedPaymentLabel.value
    const response = await createSale(payload)
    session.value = response.cash_register_session
    cart.value = []
    selectedCartProductId.value = null
    selectPaymentMethod('CASH')
    showConfirmSaleDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Venda confirmada',
      detail: `${formatCurrency(response.sale.total_amount)} em ${paymentLabel}`,
      life: 2200
    })
    focusSearchInput()
  } catch (error) {
    showConfirmSaleDialog.value = false
    displayError(readError(error, 'Não foi possível confirmar a venda.'))

    if (error instanceof ApiError && error.status === 409) {
      await loadCurrentSession()
    }
  } finally {
    isSubmitting.value = false
  }
}

async function submitClose(): Promise<void> {
  if (!session.value || !authStore.isOwner || viewState.value !== 'open') {
    return
  }

  if (!closingAmount.value) {
    displayError('Informe o valor contado para fechar o caixa.')
    return
  }

  if (!ownerPin.value) {
    displayError('Informe o PIN do proprietário para fechar o caixa.')
    return
  }

  isSubmitting.value = true
  resetMessages()

  try {
    const closedSession = await closeCashRegister(session.value.id, {
      closing_amount: closingAmount.value,
      owner_pin: ownerPin.value
    })
    saveLastClosedSession(closedSession)
    session.value = closedSession
    viewState.value = 'closed'
    closingAmount.value = ''
    ownerPin.value = ''
    showCloseDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Fechamento concluído',
      detail: `Diferença final ${formatCurrency(closedSession.difference_amount ?? '0.00')}`,
      life: 2200
    })
  } catch (error) {
    showCloseDialog.value = false
    displayError(readError(error, 'Não foi possível fechar o caixa.'))
  } finally {
    isSubmitting.value = false
  }
}

usePosKeyboardShortcuts({
  onOpenHelp: () => {
    showShortcutDialog.value = true
  },
  onOpenMoreOptions: openMoreOptions,
  onFocusSearch: () => {
    if (viewState.value === 'open') {
      focusSearchInput()
    }
  },
  onClearCart: clearCart,
  onCancelItem: cancelSelectedItem,
  onConfirmSale: requestSaleConfirmation,
  onCloseCashRegister: () => {
    if (!authStore.isOwner) {
      displayError('Apenas o proprietário pode fechar o caixa.')
      return
    }

    requestCloseConfirmation()
  },
  onSelectProductShortcut: handleProductShortcut
})

onMounted(async () => {
  await refreshPage()
})

async function handleLogout(): Promise<void> {
  await authStore.logout()
  await router.replace('/login')
}
</script>
