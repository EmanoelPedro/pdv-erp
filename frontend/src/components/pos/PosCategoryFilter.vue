<template>
  <div class="grid gap-2 sm:grid-cols-3 xl:grid-cols-6">
    <Button
      v-for="item in categoryButtons"
      :key="item.id"
      fluid
      class="pos-category-button"
      :severity="item.id === modelValue ? 'success' : 'secondary'"
      :outlined="item.id !== modelValue"
      @click="emit('update:modelValue', item.id)"
    >
      <template #default>
        <div class="flex w-full items-center gap-2 text-left">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg text-xl"
            :class="item.visual.surfaceClass"
          >
            <span class="leading-none">{{ item.visual.icon }}</span>
          </div>
          <div class="flex flex-col">
            <span class="text-xs font-semibold">{{ item.label }}</span>
            <span class="text-[11px] text-zinc-500">{{ item.caption }}</span>
          </div>
        </div>
      </template>
    </Button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'

import {
  resolveCategoryVisual,
  sortCategoriesForPos
} from '@/components/pos/visuals'
import type { Category } from '@/types/catalog'

const props = defineProps<{
  categories: Category[]
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const categoryButtons = computed(() => {
  const orderedCategories = sortCategoriesForPos(props.categories)
  return [
    {
      id: 'all',
      label: 'Todos',
      caption: 'Sem filtro',
      visual: resolveCategoryVisual('todos')
    },
    ...orderedCategories.map((category) => ({
      id: category.id,
      label: category.name,
      caption: 'Categoria',
      visual: resolveCategoryVisual(category.name)
    }))
  ]
})
</script>
