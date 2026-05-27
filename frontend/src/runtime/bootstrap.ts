import { initializeRuntimeConfig } from '@/runtime/config'

const DESKTOP_HEALTH_ATTEMPTS = 40
const DESKTOP_HEALTH_INTERVAL_MS = 250

function wait(intervalMs: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, intervalMs)
  })
}

async function isApiHealthy(apiBaseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${apiBaseUrl}/health/ready`, {
      cache: 'no-store',
      headers: {
        Accept: 'application/json'
      }
    })

    return response.ok
  } catch {
    return false
  }
}

export async function bootstrapRuntime(): Promise<void> {
  const config = await initializeRuntimeConfig()

  if (config.mode !== 'desktop') {
    return
  }

  for (let attempt = 0; attempt < DESKTOP_HEALTH_ATTEMPTS; attempt += 1) {
    if (await isApiHealthy(config.apiBaseUrl)) {
      return
    }

    await wait(DESKTOP_HEALTH_INTERVAL_MS)
  }

  throw new Error('O backend local nao respondeu a tempo. Reinicie o aplicativo.')
}