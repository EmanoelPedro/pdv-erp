import { inject, type InjectionKey } from 'vue'

export type AppTopbarSeverity =
  | 'secondary'
  | 'contrast'
  | 'success'
  | 'info'
  | 'warn'
  | 'danger'

export interface AppTopbarBadge {
  value: string
  severity?: AppTopbarSeverity
}

export interface AppTopbarAction {
  key: string
  label: string
  icon?: string
  severity?: AppTopbarSeverity
  outlined?: boolean
  text?: boolean
  size?: 'small' | 'large'
  onClick: () => void | Promise<void>
}

export interface AppTopbarConfig {
  title?: string
  badge?: AppTopbarBadge | null
  actions?: AppTopbarAction[]
}

export interface AppTopbarController {
  setTopbar: (config: AppTopbarConfig | null) => void
  clearTopbar: () => void
}

export const appTopbarKey: InjectionKey<AppTopbarController> =
  Symbol('appTopbar')

export function useAppTopbar(): AppTopbarController {
  const controller = inject(appTopbarKey, null)

  if (!controller) {
    throw new Error('App topbar controller is not available in this route.')
  }

  return controller
}
