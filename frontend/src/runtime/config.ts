import { getRuntimeMode, type RuntimeMode } from '@/runtime/platform'

export interface RuntimeConfig {
  mode: RuntimeMode
  apiBaseUrl: string
}

const webDefaultBaseUrl = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
const desktopDefaultBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

let runtimeConfig: RuntimeConfig | null = null

async function resolveDesktopApiBaseUrl(): Promise<string> {
  const { invoke } = await import('@tauri-apps/api/core')
  const config = await invoke<Partial<RuntimeConfig>>('get_runtime_config')

  return config.apiBaseUrl?.trim() || desktopDefaultBaseUrl
}

export async function initializeRuntimeConfig(): Promise<RuntimeConfig> {
  if (runtimeConfig) {
    return runtimeConfig
  }

  const mode = getRuntimeMode()

  runtimeConfig = {
    mode,
    apiBaseUrl: mode === 'desktop' ? await resolveDesktopApiBaseUrl() : webDefaultBaseUrl
  }

  return runtimeConfig
}

export function getRuntimeConfig(): RuntimeConfig {
  if (runtimeConfig) {
    return runtimeConfig
  }

  const mode = getRuntimeMode()

  return {
    mode,
    apiBaseUrl: mode === 'desktop' ? desktopDefaultBaseUrl : webDefaultBaseUrl
  }
}