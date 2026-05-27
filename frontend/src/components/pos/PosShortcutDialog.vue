<template>
  <Dialog
    :visible="modelValue"
    modal
    header="Atalhos do caixa"
    :style="{ width: 'min(42rem, calc(100vw - 2rem))' }"
    @update:visible="emit('update:modelValue', $event)"
  >
    <div class="grid gap-3">
      <div
        v-for="shortcut in shortcuts"
        :key="shortcut.key"
        class="flex items-center justify-between gap-4 rounded-xl border border-zinc-200 px-4 py-3"
      >
        <span class="text-sm font-medium text-zinc-600">{{ shortcut.label }}</span>
        <Tag severity="secondary" :value="shortcut.key" />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'

import { POS_SHORTCUTS } from '@/components/pos/visuals'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const shortcuts = POS_SHORTCUTS
</script>
