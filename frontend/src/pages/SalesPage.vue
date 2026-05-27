<template>
  <section class="grid gap-4 md:grid-cols-3">
    <Card v-for="item in cards" :key="item.title">
      <template #title>{{ item.title }}</template>
      <template #content>
        <div class="flex flex-col gap-3">
          <Tag :value="item.kicker" severity="secondary" />
          <p class="text-sm text-zinc-600">{{ item.text }}</p>
        </div>
      </template>
    </Card>
  </section>
</template>

<script setup lang="ts">
import Card from 'primevue/card'
import Tag from 'primevue/tag'

const cards = [
  {
    kicker: 'Vendas',
    title: 'Registro',
    text: 'As vendas sao criadas pela tela de caixa.'
  },
  {
    kicker: 'Pagamentos',
    title: 'Pagamentos',
    text: 'Dinheiro, Pix, debito, credito e misto.'
  },
  {
    kicker: 'Historico',
    title: 'Historico',
    text: 'Consulta detalhada ainda pendente.'
  }
]
</script>
