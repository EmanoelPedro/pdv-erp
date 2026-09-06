<template>
  <Card class="h-full border border-zinc-200">
    <template #title>
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span>Carrinho</span>
          <span class="text-xs font-normal text-zinc-500"
            >({{ itemCount }} itens)</span
          >
        </div>
        <Button
          label="Limpar (F5)"
          severity="danger"
          text
          :disabled="lines.length === 0"
          @click="emit('clear')"
        />
      </div>
    </template>

    <template #content>
      <div class="flex flex-col gap-3">
        <div v-if="lines.length === 0" class="pos-empty-state">
          <div class="text-4xl">🛒</div>
          <div class="mt-2 text-base font-semibold text-zinc-700">
            Nenhum item no carrinho
          </div>
          <div class="mt-1 text-sm text-zinc-500">
            Adicione produtos para iniciar a venda.
          </div>
        </div>

        <div v-else class="max-h-[18rem] space-y-2 overflow-auto pr-1">
          <button
            v-for="line in lines"
            :key="line.product.id"
            type="button"
            class="pos-cart-line w-full text-left"
            :class="{
              'pos-cart-line-active': line.product.id === selectedProductId
            }"
            @click="emit('select', line.product.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="text-sm font-semibold text-zinc-950">
                  {{ line.product.name }}
                </div>
                <div class="mt-1 text-xs text-zinc-500">
                  {{ formatCurrency(line.product.price) }} cada
                </div>
              </div>
              <div class="text-right">
                <div class="text-xs text-zinc-500">Subtotal</div>
                <div class="text-base font-semibold text-zinc-950">
                  {{ formatCurrency(line.total) }}
                </div>
              </div>
            </div>

            <div class="mt-3 flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <Button
                  label="-"
                  size="small"
                  severity="secondary"
                  @click.stop="emit('decrease', line.product.id)"
                />
                <Tag severity="secondary" :value="String(line.quantity)" />
                <Button
                  label="+"
                  size="small"
                  severity="secondary"
                  @click.stop="emit('increase', line.product.id)"
                />
              </div>

              <Button
                label="Remover"
                size="small"
                severity="danger"
                text
                @click.stop="emit('remove', line.product.id)"
              />
            </div>
          </button>
        </div>

        <div
          class="rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-3"
        >
          <div class="flex items-end justify-between gap-4">
            <div>
              <div class="text-sm font-medium text-emerald-700">
                Total da venda
              </div>
              <div class="text-xs text-emerald-700/70">
                Confira antes de confirmar.
              </div>
            </div>
            <div class="text-xl font-semibold text-emerald-700">
              {{ formatCurrency(total) }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Tag from 'primevue/tag'

import type { Product } from '@/types/catalog'

interface CartLine {
  product: Product
  quantity: number
  total: string
}

const props = defineProps<{
  lines: CartLine[]
  total: string
  selectedProductId: string | null
}>()

const emit = defineEmits<{
  select: [productId: string]
  clear: []
  increase: [productId: string]
  decrease: [productId: string]
  remove: [productId: string]
}>()

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const itemCount = computed(() =>
  props.lines.reduce((sum, line) => sum + line.quantity, 0)
)

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value))
}
</script>
