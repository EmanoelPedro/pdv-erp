import { onBeforeUnmount, onMounted } from 'vue'

import { PRODUCT_SHORTCUT_KEYS } from '@/components/pos/visuals'

interface PosKeyboardHandlers {
  onOpenHelp: () => void
  onOpenMoreOptions: () => void
  onFocusSearch: () => void
  onClearCart: () => void
  onCancelItem: () => void
  onConfirmSale: () => void
  onCloseCashRegister: () => void
  onSelectProductShortcut: (shortcut: string) => void
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false
  }

  if (target.isContentEditable) {
    return true
  }

  return ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)
}

export function usePosKeyboardShortcuts(handlers: PosKeyboardHandlers): void {
  function handleKeydown(event: KeyboardEvent): void {
    const editableTarget = isEditableTarget(event.target)

    if (
      (event.key === 'k' && (event.ctrlKey || event.metaKey)) ||
      (!editableTarget && event.key === '/')
    ) {
      event.preventDefault()
      handlers.onFocusSearch()
      return
    }

    switch (event.key) {
      case 'F2':
        event.preventDefault()
        handlers.onOpenHelp()
        return
      case 'F3':
        event.preventDefault()
        handlers.onFocusSearch()
        return
      case 'F5':
        event.preventDefault()
        handlers.onClearCart()
        return
      case 'F6':
        event.preventDefault()
        handlers.onCancelItem()
        return
      case 'F10':
        event.preventDefault()
        handlers.onConfirmSale()
        return
      case 'F11':
        event.preventDefault()
        handlers.onOpenMoreOptions()
        return
      case 'F12':
        event.preventDefault()
        handlers.onCloseCashRegister()
        return
      default:
        break
    }

    if (editableTarget) {
      return
    }

    if (
      PRODUCT_SHORTCUT_KEYS.includes(
        event.key as (typeof PRODUCT_SHORTCUT_KEYS)[number]
      )
    ) {
      event.preventDefault()
      handlers.onSelectProductShortcut(event.key)
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}
