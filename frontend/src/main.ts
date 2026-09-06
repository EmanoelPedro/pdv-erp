import { createApp } from 'vue'
import Aura from '@primeuix/themes/aura'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

import App from './App.vue'
import { router } from './router'
import { bootstrapRuntime } from './runtime/bootstrap'
import { isDesktopRuntime } from './runtime/platform'
import { pinia } from './stores'
import './styles.css'

let hasMountedApplication = false
let hasResolvedBootError = false

function readBootstrapError(error: unknown): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message
  }

  if (typeof error === 'string' && error.trim()) {
    return error
  }

  if (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof error.message === 'string' &&
    error.message.trim()
  ) {
    return error.message
  }

  return 'Não foi possível iniciar o aplicativo.'
}

async function resetDesktopWebviewState(): Promise<void> {
  if (!isDesktopRuntime()) {
    return
  }

  try {
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations()
      await Promise.all(
        registrations.map((registration) => registration.unregister())
      )
    }

    if ('caches' in window) {
      const cacheKeys = await window.caches.keys()
      await Promise.all(
        cacheKeys.map((cacheKey) => window.caches.delete(cacheKey))
      )
    }
  } catch (error) {
    console.error('failed to reset desktop webview cache', error)
  }
}

function registerBootErrorHandlers(): void {
  window.addEventListener('error', (event) => {
    if (hasMountedApplication || hasResolvedBootError) {
      return
    }

    const description = readBootstrapError(event.error ?? event.message)
    hasResolvedBootError = true
    console.error(event.error ?? event.message)
    renderBootState('Não foi possível iniciar o PDV', description, true)
  })

  window.addEventListener('unhandledrejection', (event) => {
    if (hasMountedApplication || hasResolvedBootError) {
      return
    }

    const description = readBootstrapError(event.reason)
    hasResolvedBootError = true
    console.error(event.reason)
    renderBootState('Não foi possível iniciar o PDV', description, true)
  })
}

function resolveBootFailure(error: unknown): void {
  if (hasResolvedBootError) {
    return
  }

  hasResolvedBootError = true
  const description = readBootstrapError(error)
  console.error(error)
  renderBootState('Não foi possível iniciar o PDV', description, true)
}

function renderBootState(
  title: string,
  description: string,
  isError = false
): void {
  const container = document.querySelector<HTMLDivElement>('#app')

  if (!container) {
    return
  }

  const shell = document.createElement('div')
  shell.className = 'boot-shell'

  const card = document.createElement('div')
  card.className = 'boot-card'

  const eyebrow = document.createElement('p')
  eyebrow.className = 'boot-eyebrow'
  eyebrow.textContent = isError ? 'Falha de inicializacao' : 'PDV Local'

  const heading = document.createElement('h1')
  heading.className = 'boot-title'
  heading.textContent = title

  const body = document.createElement('p')
  body.className = 'boot-copy'
  body.textContent = description

  card.append(eyebrow, heading, body)
  shell.append(card)
  container.replaceChildren(shell)
}

async function bootstrapApplication(): Promise<void> {
  await resetDesktopWebviewState()
  renderBootState(
    'Preparando o aplicativo',
    'Verificando a API e carregando o ambiente local...'
  )
  await bootstrapRuntime()

  const app = createApp(App)

  app.use(PrimeVue, {
    ripple: true,
    inputVariant: 'filled',
    theme: {
      preset: Aura,
      options: {
        darkModeSelector: false
      }
    }
  })

  app.use(ToastService)
  app.use(pinia)
  app.use(router)
  app.config.errorHandler = (error) => {
    if (!hasMountedApplication) {
      resolveBootFailure(error)
      return
    }

    console.error(error)
  }
  router.onError((error) => {
    if (!hasMountedApplication) {
      resolveBootFailure(error)
      return
    }

    console.error(error)
  })
  app.mount('#app')
  hasMountedApplication = true
}

registerBootErrorHandlers()

void bootstrapApplication().catch((error) => {
  resolveBootFailure(error)
})
