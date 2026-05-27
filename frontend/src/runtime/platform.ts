export type RuntimeMode = 'web' | 'desktop'

export function isDesktopRuntime(): boolean {
  return typeof window !== 'undefined' && typeof window.__TAURI_INTERNALS__ !== 'undefined'
}

export function getRuntimeMode(): RuntimeMode {
  return isDesktopRuntime() ? 'desktop' : 'web'
}