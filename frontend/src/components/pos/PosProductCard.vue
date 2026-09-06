<template>
  <Card
    class="pos-product-card h-full border border-zinc-200"
    :class="{ 'pos-product-card-active': active }"
    :pt="{
      root: {
        tabindex: 0,
        role: 'button',
        'aria-label': `Adicionar ${product.name}`
      }
    }"
    @click="emit('add', product)"
    @keydown.enter.prevent="emit('add', product)"
    @keydown.space.prevent="emit('add', product)"
  >
    <template #content>
      <div class="flex h-full flex-col gap-3">
        <div class="flex items-start justify-between gap-3">
          <div
            class="pos-product-media overflow-hidden"
            :class="imageUrl ? 'bg-zinc-100' : visual.surfaceClass"
          >
            <img
              v-if="imageUrl"
              :src="imageUrl"
              :alt="product.name"
              class="h-full w-full object-cover"
            />
            <span v-else class="text-3xl leading-none">{{
              product.emoji || visual.icon
            }}</span>
          </div>
          <Tag v-if="shortcut" severity="secondary" :value="shortcut" />
        </div>

        <div class="flex min-h-[3.5rem] flex-1 flex-col">
          <div class="text-sm font-semibold leading-tight text-zinc-950">
            {{ product.name }}
          </div>
          <div class="mt-1 text-xs text-zinc-500">{{ categoryLabel }}</div>
        </div>

        <div class="flex items-end justify-between gap-3">
          <span class="text-lg font-semibold text-zinc-950">{{
            priceLabel
          }}</span>
          <Button
            label="Adicionar"
            size="small"
            @click.stop="emit('add', product)"
          />
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

import { resolveProductVisual } from '@/components/pos/visuals'
import { getApiBaseUrl } from '@/services/http'
import type { Product } from '@/types/catalog'

const props = defineProps<{
  product: Product
  categoryLabel: string
  shortcut?: string
  active?: boolean
}>()

const emit = defineEmits<{
  add: [product: Product]
}>()

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const visual = computed(() =>
  resolveProductVisual(props.categoryLabel, props.product.name)
)
const imageUrl = computed(() =>
  props.product.image_path
    ? `${getApiBaseUrl()}${props.product.image_path}`
    : null
)
const priceLabel = computed(() =>
  currencyFormatter.format(Number(props.product.price))
)
</script>
