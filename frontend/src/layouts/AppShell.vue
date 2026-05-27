<template>
  <div class="min-h-screen bg-zinc-100 py-3 text-zinc-950">
    <div
      v-if="!uiStore.isOnline"
      class="fixed inset-x-0 top-0 z-50 flex items-center justify-center gap-2 bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow"
    >
      <i class="pi pi-wifi" style="font-size: 0.9rem" />
      Sem conexao &mdash; vendas serao sincronizadas ao reconectar
    </div>
    <div class="page-shell-wide" :class="{ 'mt-9': !uiStore.isOnline }">
      <header
        v-if="!isCashRegister"
        class="mb-4 flex flex-wrap items-start justify-between gap-3 rounded-[1.75rem] border border-zinc-200 bg-white px-5 py-4 shadow-[0_18px_40px_-28px_rgba(15,23,42,0.35)]"
      >
        <div class="min-w-0">
          <h1 class="text-2xl font-semibold tracking-[-0.03em] text-zinc-950">{{ currentTopbar.title }}</h1>
        </div>

        <div class="flex shrink-0 flex-wrap items-center justify-end gap-2 self-start">
          <Tag
            v-if="currentTopbar.badge"
            :value="currentTopbar.badge.value"
            :severity="currentTopbar.badge.severity ?? 'secondary'"
            rounded
          />
          <Button
            v-for="action in currentTopbar.actions ?? []"
            :key="action.key"
            :label="action.label"
            :icon="action.icon"
            :severity="action.severity ?? 'secondary'"
            :outlined="action.outlined"
            :text="action.text"
            :size="action.size"
            @click="action.onClick"
          />
          <Button class="!text-sm" label="Menu" severity="secondary" outlined @click="uiStore.openSidebar" />
        </div>
      </header>

      <RouterView />
    </div>

    <Drawer v-model:visible="uiStore.sidebarOpen" position="right" header="Mais opcoes" :style="{ width: '22rem', maxWidth: '92vw' }">
      <div class="flex h-full flex-col gap-4">
        <div class="rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
          <div class="text-sm font-semibold text-zinc-950">{{ authStore.user?.full_name ?? 'Sem sessao' }}</div>
          <div class="mt-1 text-sm text-zinc-500">@{{ authStore.user?.username ?? 'visitante' }}</div>
          <Tag class="mt-3" :severity="authStore.isOwner ? 'warn' : 'secondary'" :value="authStore.isOwner ? 'Proprietario' : 'Funcionario'" />
        </div>

        <nav class="flex flex-col gap-2">
          <Button
            v-for="item in navigation"
            :key="item.route"
            :label="item.label"
            class="justify-start"
            :severity="item.route === route.path ? 'contrast' : 'secondary'"
            :outlined="item.route !== route.path"
            @click="navigateTo(item.route)"
          />
        </nav>

        <div class="mt-auto">
          <Button label="Sair" severity="secondary" outlined fluid @click="handleLogout" />
        </div>
      </div>
    </Drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, provide, shallowRef, watch } from 'vue'
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import Tag from 'primevue/tag'
import { RouterView, useRoute, useRouter } from 'vue-router'

import { appTopbarKey, type AppTopbarConfig } from '@/composables/useAppTopbar'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const topbarOverride = shallowRef<AppTopbarConfig | null>(null)

const topbarByRouteName: Record<string, { title: string }> = {
  dashboard: {
    title: 'Visao geral do negocio'
  },
  catalog: {
    title: 'Produtos e categorias'
  },
  users: {
    title: 'Usuarios e acessos'
  },
  sales: {
    title: 'Operacao comercial'
  },
  expenses: {
    title: 'Despesas do caixa'
  },
  reports: {
    title: 'Relatorios operacionais'
  }
}

const isCashRegister = computed(() => route.path === '/caixa')

const currentTopbar = computed(() => {
  const routeName = typeof route.name === 'string' ? route.name : ''
  const baseTopbar =
    topbarByRouteName[routeName] ?? {
      title: 'Painel operacional'
    }

  return {
    ...baseTopbar,
    ...topbarOverride.value,
    badge: topbarOverride.value?.badge ?? null,
    actions: topbarOverride.value?.actions ?? []
  }
})

provide(appTopbarKey, {
  setTopbar(config) {
    topbarOverride.value = config
  },
  clearTopbar() {
    topbarOverride.value = null
  }
})

watch(
  () => route.fullPath,
  () => {
    topbarOverride.value = null
  }
)

const navigation = computed(() =>
  authStore.isOwner
    ? [
        { label: 'Dashboard', route: '/' },
        { label: 'Caixa', route: '/caixa' },
        { label: 'Catalogo', route: '/catalogo' },
        { label: 'Usuarios', route: '/usuarios' },
        { label: 'Vendas', route: '/vendas' },
        { label: 'Despesas', route: '/despesas' },
        { label: 'Relatorios', route: '/relatorios' }
      ]
    : [
        { label: 'Caixa', route: '/caixa' },
        { label: 'Vendas', route: '/vendas' }
      ]
)

  function handleGlobalKeydown(event: KeyboardEvent): void {
    if (event.key !== 'F11') {
      return
    }

    event.preventDefault()
    uiStore.openSidebar()
  }

async function navigateTo(path: string): Promise<void> {
  uiStore.closeSidebar()
  await router.push(path)
}

async function handleLogout(): Promise<void> {
  uiStore.closeSidebar()
  await authStore.logout()
  await router.replace('/login')
}

function handleOnline() {
  uiStore.setOnline(true)
}

function handleOffline() {
  uiStore.setOnline(false)
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>
