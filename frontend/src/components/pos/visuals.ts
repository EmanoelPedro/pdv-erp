export const PRODUCT_SHORTCUT_KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='] as const

export const POS_SHORTCUTS = [
  { key: 'F2', label: 'Atalhos' },
  { key: 'F3', label: 'Buscar produto' },
  { key: 'F5', label: 'Limpar carrinho' },
  { key: 'F6', label: 'Cancelar item' },
  { key: 'F7', label: 'Desconto' },
  { key: 'F8', label: 'Observacao' },
  { key: 'F9', label: 'Cliente' },
  { key: 'F10', label: 'Confirmar venda' },
  { key: 'F11', label: 'Mais opcoes' },
  { key: 'F12', label: 'Fechar caixa' },
  { key: '1-0 - =', label: 'Adicionar produto visivel' }
] as const

type VisualKey = 'pasteis' | 'bebidas' | 'salgados' | 'lanches' | 'pizzas' | 'outros' | 'todos'

interface VisualConfig {
  icon: string
  chipClass: string
  surfaceClass: string
}

const VISUALS: Record<VisualKey, VisualConfig> = {
  pasteis: {
    icon: '🥟',
    chipClass: 'bg-amber-50 text-amber-700',
    surfaceClass: 'bg-amber-50 text-amber-700'
  },
  bebidas: {
    icon: '🥤',
    chipClass: 'bg-sky-50 text-sky-700',
    surfaceClass: 'bg-sky-50 text-sky-700'
  },
  salgados: {
    icon: '🧆',
    chipClass: 'bg-orange-50 text-orange-700',
    surfaceClass: 'bg-orange-50 text-orange-700'
  },
  lanches: {
    icon: '🍔',
    chipClass: 'bg-emerald-50 text-emerald-700',
    surfaceClass: 'bg-emerald-50 text-emerald-700'
  },
  pizzas: {
    icon: '🍕',
    chipClass: 'bg-rose-50 text-rose-700',
    surfaceClass: 'bg-rose-50 text-rose-700'
  },
  outros: {
    icon: '🍽️',
    chipClass: 'bg-zinc-100 text-zinc-700',
    surfaceClass: 'bg-zinc-100 text-zinc-700'
  },
  todos: {
    icon: '▦',
    chipClass: 'bg-zinc-900 text-white',
    surfaceClass: 'bg-zinc-100 text-zinc-700'
  }
}

const CATEGORY_ORDER: VisualKey[] = ['pasteis', 'bebidas', 'salgados', 'lanches', 'pizzas', 'outros']

function normalize(value: string | undefined | null): string {
  return (value ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

function includesAny(value: string, words: string[]): boolean {
  return words.some((word) => value.includes(word))
}

export function resolveVisualKey(categoryName?: string, productName?: string): VisualKey {
  const text = `${normalize(categoryName)} ${normalize(productName)}`

  if (includesAny(text, ['todo', 'todos'])) {
    return 'todos'
  }

  if (includesAny(text, ['pastel', 'pasteis'])) {
    return 'pasteis'
  }
  if (includesAny(text, ['bebida', 'refrigerante', 'suco', 'agua', 'cafe', 'caldo', 'cana'])) {
    return 'bebidas'
  }
  if (includesAny(text, ['salgado', 'coxinha', 'bolinha', 'kibe', 'croquete', 'enrolado'])) {
    return 'salgados'
  }
  if (includesAny(text, ['lanche', 'burger', 'burguer', 'x-b', 'x-', 'sanduiche', 'sanduich'])) {
    return 'lanches'
  }
  if (includesAny(text, ['pizza', 'broto'])) {
    return 'pizzas'
  }

  return 'outros'
}

export function resolveProductVisual(categoryName?: string, productName?: string): VisualConfig {
  return VISUALS[resolveVisualKey(categoryName, productName)]
}

export function resolveCategoryVisual(categoryName: string): VisualConfig {
  return VISUALS[resolveVisualKey(categoryName)]
}

export function sortCategoriesForPos<T extends { name: string }>(categories: T[]): T[] {
  return [...categories].sort((left, right) => {
    const leftKey = resolveVisualKey(left.name)
    const rightKey = resolveVisualKey(right.name)
    const leftRank = CATEGORY_ORDER.indexOf(leftKey)
    const rightRank = CATEGORY_ORDER.indexOf(rightKey)

    if (leftRank !== rightRank) {
      return leftRank - rightRank
    }

    return left.name.localeCompare(right.name, 'pt-BR')
  })
}
