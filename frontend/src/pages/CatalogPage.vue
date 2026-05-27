<template>
  <section class="app-page flex flex-col gap-4">
    <div class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
      <Card class="border border-zinc-200">
        <template #content>
          <div class="flex flex-col gap-4">
            <div class="grid gap-3 sm:grid-cols-3">
              <div class="catalog-preview-tile">
                <div class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500">Categorias</div>
                <div class="mt-2 text-2xl font-semibold text-zinc-950">{{ categories.length }}</div>
              </div>
              <div class="catalog-preview-tile">
                <div class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500">Ativos</div>
                <div class="mt-2 text-2xl font-semibold text-zinc-950">{{ activeProducts.length }}</div>
              </div>
              <div class="catalog-preview-tile">
                <div class="text-xs font-medium uppercase tracking-[0.18em] text-zinc-500">Inativos</div>
                <div class="mt-2 text-2xl font-semibold text-zinc-950">{{ inactiveProducts.length }}</div>
              </div>
            </div>

            <div class="rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
              <div class="text-sm font-semibold text-zinc-950">Nova categoria</div>
              <form class="mt-4 flex flex-col gap-3" @submit.prevent="submitCategory">
                <div class="flex flex-col gap-2">
                  <label class="text-sm font-medium text-zinc-700" for="category-name">Nome</label>
                  <InputText id="category-name" v-model="categoryName" placeholder="Ex.: Pasteis" />
                </div>

                <Button type="submit" :label="isSubmittingCategory ? 'Salvando...' : 'Criar categoria'" :loading="isSubmittingCategory" />
              </form>
            </div>
          </div>
        </template>
      </Card>

      <Card class="border border-zinc-200">
        <template #content>
          <div class="grid gap-5 xl:grid-cols-[1fr_0.9fr]">
            <form class="flex flex-col gap-4" @submit.prevent="submitProduct">
              <div class="text-lg font-semibold text-zinc-950">Cadastrar produto</div>

              <div class="grid gap-4 md:grid-cols-2">
                <div class="flex flex-col gap-2">
                  <label class="text-sm font-medium text-zinc-700" for="product-category">Categoria</label>
                  <Select
                    id="product-category"
                    v-model="selectedCategoryId"
                    :options="categories"
                    option-label="name"
                    option-value="id"
                    placeholder="Selecione"
                  />
                </div>

                <div class="flex flex-col gap-2">
                  <label class="text-sm font-medium text-zinc-700" for="product-price">Preco</label>
                  <InputNumber
                    id="product-price"
                    v-model="productPriceValue"
                    mode="currency"
                    currency="BRL"
                    locale="pt-BR"
                    :min="0"
                    :min-fraction-digits="2"
                    :max-fraction-digits="2"
                    fluid
                    placeholder="R$ 0,00"
                  />
                </div>
              </div>

              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-zinc-700" for="product-name">Nome</label>
                <InputText id="product-name" v-model="productName" placeholder="Ex.: Pastel de Carne" />
              </div>

              <div class="grid gap-4 md:grid-cols-[0.45fr_0.55fr]">
                <div class="flex flex-col gap-2">
                  <label class="text-sm font-medium text-zinc-700" for="product-emoji">Emoji</label>
                  <Select
                    id="product-emoji"
                    v-model="productEmoji"
                    :options="emojiOptions"
                    option-label="label"
                    option-value="value"
                    filter
                    show-clear
                    placeholder="Escolha um emoji"
                  />
                </div>

                <div class="flex flex-col gap-2">
                  <label class="text-sm font-medium text-zinc-700" for="product-image">Foto</label>
                  <input
                    id="product-image"
                    class="rounded-xl border border-zinc-300 bg-white px-3 py-3 text-sm text-zinc-700"
                    type="file"
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    @change="handleImageSelection"
                  />
                  <div class="text-xs text-zinc-500">Ao escolher a foto, uma janela de corte sera aberta para ajustar qualidade e enquadramento.</div>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <Button type="submit" :label="isSubmittingProduct ? 'Salvando...' : 'Criar produto'" :loading="isSubmittingProduct" />
                <Button label="Limpar" severity="secondary" text @click.prevent="resetCreateForm" />
              </div>
            </form>

            <div class="catalog-preview-tile flex flex-col gap-4">
              <div class="text-sm font-semibold text-zinc-950">Preview do produto</div>

              <div class="rounded-[1.5rem] border border-zinc-200 bg-white p-4 shadow-sm">
                <div class="flex items-start justify-between gap-3">
                  <div class="catalog-product-thumb">
                    <img v-if="productImagePreview" :src="productImagePreview" :alt="previewName" class="h-full w-full object-cover" />
                    <span v-else class="text-5xl leading-none">{{ previewEmoji }}</span>
                  </div>
                  <Tag :value="previewCategory" severity="secondary" />
                </div>

                <div class="mt-5 text-xl font-semibold text-zinc-950">{{ previewName }}</div>
                <div class="mt-2 text-sm text-zinc-500">{{ previewCategory }}</div>
                <div class="mt-6 text-3xl font-semibold text-emerald-700">{{ formatCurrencyNumber(productPriceValue ?? 0) }}</div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Card class="border border-zinc-200">
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="text-lg font-semibold text-zinc-950">Produtos</span>
              <Select
                v-model="catalogFilter"
                :options="filterOptions"
                option-label="label"
                option-value="value"
                class="min-w-[12rem]"
              />
            </div>

            <Button label="Atualizar" severity="secondary" outlined @click="refreshCatalog" />
          </div>

          <Message v-if="message" severity="success" :closable="false">{{ message }}</Message>
          <Message v-if="errorMessage" severity="error" :closable="false">{{ errorMessage }}</Message>

          <div v-if="visibleProducts.length === 0" class="pos-empty-state">
            <div class="text-5xl">📦</div>
            <div class="mt-3 text-lg font-semibold text-zinc-700">Nenhum produto encontrado</div>
            <div class="mt-1 text-sm text-zinc-500">Altere o filtro ou cadastre um novo item.</div>
          </div>

          <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="product in visibleProducts" :key="product.id" class="catalog-preview-tile flex flex-col gap-4" :class="{ 'opacity-70': !product.is_active }">
              <div class="flex items-start justify-between gap-3">
                <div class="catalog-product-thumb">
                  <img
                    v-if="product.image_path"
                    :src="productImageUrl(product.image_path)"
                    :alt="product.name"
                    class="h-full w-full object-cover"
                  />
                  <span v-else class="text-4xl leading-none">{{ product.emoji || fallbackEmoji(product) }}</span>
                </div>
                <Tag :severity="product.is_active ? 'success' : 'secondary'" :value="product.is_active ? 'Ativo' : 'Inativo'" />
              </div>

              <div>
                <div class="text-lg font-semibold text-zinc-950">{{ product.name }}</div>
                <div class="mt-1 text-sm text-zinc-500">{{ categoryNameById(product.category_id) }}</div>
              </div>

              <div class="mt-auto flex flex-col gap-3">
                <div class="text-2xl font-semibold text-zinc-950">{{ formatCurrency(product.price) }}</div>

                <div class="grid gap-2 sm:grid-cols-2">
                  <Button label="Editar" severity="secondary" outlined @click="openEditDialog(product)" />
                  <Button
                    v-if="product.is_active"
                    label="Excluir"
                    severity="danger"
                    outlined
                    @click="softDeleteProduct(product)"
                  />
                  <Button
                    v-else
                    label="Restaurar"
                    severity="success"
                    outlined
                    @click="restoreProductItem(product)"
                  />
                </div>
              </div>
            </article>
          </div>
        </div>
      </template>
    </Card>

    <Dialog v-model:visible="showEditDialog" modal header="Editar produto" :style="{ width: '42rem', maxWidth: '95vw' }">
      <form class="flex flex-col gap-4" @submit.prevent="submitEditProduct">
        <div class="grid gap-4 md:grid-cols-2">
          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="edit-category">Categoria</label>
            <Select id="edit-category" v-model="editCategoryId" :options="categories" option-label="name" option-value="id" placeholder="Selecione" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="edit-price">Preco</label>
            <InputNumber
              id="edit-price"
              v-model="editPriceValue"
              mode="currency"
              currency="BRL"
              locale="pt-BR"
              :min="0"
              :min-fraction-digits="2"
              :max-fraction-digits="2"
              fluid
            />
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-zinc-700" for="edit-name">Nome</label>
          <InputText id="edit-name" v-model="editName" />
        </div>

        <div class="grid gap-4 md:grid-cols-[0.45fr_0.55fr]">
          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="edit-emoji">Emoji</label>
            <Select
              id="edit-emoji"
              v-model="editEmoji"
              :options="emojiOptions"
              option-label="label"
              option-value="value"
              filter
              show-clear
              placeholder="Escolha um emoji"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="edit-image">Nova foto</label>
            <input
              id="edit-image"
              class="rounded-xl border border-zinc-300 bg-white px-3 py-3 text-sm text-zinc-700"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              @change="handleEditImageSelection"
            />
          </div>
        </div>

        <div class="grid gap-3 md:grid-cols-[auto_1fr] md:items-start">
          <div class="catalog-product-thumb">
            <img v-if="editPreviewUrl" :src="editPreviewUrl" alt="Preview da imagem do produto" class="h-full w-full object-cover" />
            <span v-else class="text-4xl leading-none">{{ editEmoji || fallbackEmoji({ category_id: editCategoryId, name: editName }) }}</span>
          </div>

          <div class="flex flex-col gap-3">
            <div class="flex flex-wrap gap-2">
              <Button label="Ajustar foto atual" severity="secondary" outlined :disabled="!editImageCurrentPath" @click.prevent="openCropperForCurrentEditImage" />
              <Button label="Recortar nova foto" severity="secondary" text :disabled="!editPreviewUrl" @click.prevent="reopenEditCropper" />
            </div>

            <label class="flex items-center gap-3 text-sm text-zinc-700">
              <input v-model="editRemoveImage" type="checkbox" />
              Remover foto atual e voltar para emoji
            </label>
          </div>
        </div>
      </form>

      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="showEditDialog = false" />
        <Button label="Salvar alteracoes" :loading="isSubmittingEdit" @click="submitEditProduct" />
      </template>
    </Dialog>

    <ProductImageCropperDialog
      v-model:visible="showCropDialog"
      :source="cropImageSource"
      :title="cropDialogTitle"
      :file-name="cropFileName"
      @apply="applyCroppedImage"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import ProductImageCropperDialog from '@/components/catalog/ProductImageCropperDialog.vue'
import { resolveProductVisual } from '@/components/pos/visuals'
import {
  createCategory,
  createProduct,
  deactivateProduct,
  listCategories,
  listProducts,
  restoreProduct,
  updateProduct,
  uploadProductImage
} from '@/services/catalog'
import { getApiBaseUrl, ApiError } from '@/services/http'
import type { Category, Product } from '@/types/catalog'

type CatalogFilter = 'ALL' | 'ACTIVE' | 'INACTIVE'
type CropTarget = 'create' | 'edit' | null

const emojiOptions = [
  { label: '🥟 Pastel', value: '🥟' },
  { label: '🍔 Burger', value: '🍔' },
  { label: '🍕 Pizza', value: '🍕' },
  { label: '🥤 Refrigerante', value: '🥤' },
  { label: '🧃 Suco', value: '🧃' },
  { label: '🍟 Batata', value: '🍟' },
  { label: '🌭 Lanche', value: '🌭' },
  { label: '🥪 Sanduiche', value: '🥪' },
  { label: '🍰 Doce', value: '🍰' },
  { label: '🧁 Cupcake', value: '🧁' },
  { label: '🍩 Rosquinha', value: '🍩' },
  { label: '☕ Cafe', value: '☕' },
  { label: '🧋 Bebida', value: '🧋' },
  { label: '🧀 Salgado', value: '🧀' }
]

const categories = ref<Category[]>([])
const products = ref<Product[]>([])

const categoryName = ref('')
const selectedCategoryId = ref('')
const productName = ref('')
const productPriceValue = ref<number | null>(0)
const productEmoji = ref<string | null>(null)
const productImageFile = ref<File | null>(null)
const productImagePreview = ref<string | null>(null)
const catalogFilter = ref<CatalogFilter>('ALL')

const showEditDialog = ref(false)
const editingProductId = ref<string | null>(null)
const editCategoryId = ref('')
const editName = ref('')
const editPriceValue = ref<number | null>(0)
const editEmoji = ref<string | null>(null)
const editImageFile = ref<File | null>(null)
const editImagePreview = ref<string | null>(null)
const editImageCurrentPath = ref<string | null>(null)
const editRemoveImage = ref(false)

const showCropDialog = ref(false)
const cropImageSource = ref<string | null>(null)
const cropTarget = ref<CropTarget>(null)
const cropFileName = ref('produto.webp')

const isSubmittingCategory = ref(false)
const isSubmittingProduct = ref(false)
const isSubmittingEdit = ref(false)
const message = ref('')
const errorMessage = ref('')

const filterOptions = [
  { label: 'Todos', value: 'ALL' },
  { label: 'Ativos', value: 'ACTIVE' },
  { label: 'Inativos', value: 'INACTIVE' }
]

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const activeProducts = computed(() => products.value.filter((product) => product.is_active))
const inactiveProducts = computed(() => products.value.filter((product) => !product.is_active))
const visibleProducts = computed(() => {
  if (catalogFilter.value === 'ACTIVE') {
    return activeProducts.value
  }
  if (catalogFilter.value === 'INACTIVE') {
    return inactiveProducts.value
  }
  return products.value
})
const previewName = computed(() => productName.value.trim() || 'Produto sem nome')
const previewCategory = computed(() => categoryNameById(selectedCategoryId.value))
const previewEmoji = computed(() => {
  const fallbackProduct = {
    category_id: selectedCategoryId.value,
    name: productName.value
  } as Pick<Product, 'category_id' | 'name'>

  return productEmoji.value?.trim() || fallbackEmoji(fallbackProduct)
})
const cropDialogTitle = computed(() =>
  cropTarget.value === 'edit' ? 'Ajustar foto do produto' : 'Preparar foto do novo produto'
)
const editPreviewUrl = computed(() => {
  if (editRemoveImage.value && !editImageFile.value) {
    return null
  }

  if (editImagePreview.value) {
    return editImagePreview.value
  }

  if (editImageCurrentPath.value) {
    return productImageUrl(editImageCurrentPath.value)
  }

  return null
})

function formatCurrency(value: string): string {
  return currencyFormatter.format(Number(value))
}

function formatCurrencyNumber(value: number): string {
  return currencyFormatter.format(value)
}

function formatDecimalPrice(value: number | null): string {
  return Number(value ?? 0).toFixed(2)
}

function categoryNameById(categoryId: string): string {
  return categories.value.find((category) => category.id === categoryId)?.name ?? 'Sem categoria'
}

function fallbackEmoji(product: Pick<Product, 'category_id' | 'name'>): string {
  return resolveProductVisual(categoryNameById(product.category_id), product.name).icon
}

function productImageUrl(imagePath: string): string {
  return `${getApiBaseUrl()}${imagePath}`
}

function resetMessages(): void {
  message.value = ''
  errorMessage.value = ''
}

function resetCreateForm(): void {
  productName.value = ''
  productPriceValue.value = 0
  productEmoji.value = null
  productImageFile.value = null
  productImagePreview.value = null
  cropImageSource.value = null
  cropTarget.value = null
}

function readError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Nao foi possivel salvar o catalogo.'
}

async function fileToDataUrl(file: File): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error('Nao foi possivel ler a imagem.'))
    reader.readAsDataURL(file)
  })
}

async function openCropperForFile(file: File, target: Exclude<CropTarget, null>): Promise<void> {
  cropImageSource.value = await fileToDataUrl(file)
  cropTarget.value = target
  cropFileName.value = `${file.name.replace(/\.[^.]+$/, '') || 'produto'}.webp`
  showCropDialog.value = true
}

async function handleImageSelection(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] ?? null
  target.value = ''

  if (!file) {
    return
  }

  try {
    await openCropperForFile(file, 'create')
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

async function handleEditImageSelection(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] ?? null
  target.value = ''

  if (!file) {
    return
  }

  try {
    await openCropperForFile(file, 'edit')
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

function applyCroppedImage(payload: { file: File; previewUrl: string }): void {
  if (cropTarget.value === 'edit') {
    editImageFile.value = payload.file
    editImagePreview.value = payload.previewUrl
    editRemoveImage.value = false
  } else {
    productImageFile.value = payload.file
    productImagePreview.value = payload.previewUrl
  }

  cropImageSource.value = null
  cropTarget.value = null
}

function reopenEditCropper(): void {
  if (!editPreviewUrl.value) {
    return
  }

  cropImageSource.value = editPreviewUrl.value
  cropTarget.value = 'edit'
  cropFileName.value = 'produto-editado.webp'
  showCropDialog.value = true
}

function openCropperForCurrentEditImage(): void {
  if (!editImageCurrentPath.value) {
    return
  }

  cropImageSource.value = productImageUrl(editImageCurrentPath.value)
  cropTarget.value = 'edit'
  cropFileName.value = 'produto-atual.webp'
  showCropDialog.value = true
}

function openEditDialog(product: Product): void {
  editingProductId.value = product.id
  editCategoryId.value = product.category_id
  editName.value = product.name
  editPriceValue.value = Number(product.price)
  editEmoji.value = product.emoji
  editImageFile.value = null
  editImagePreview.value = null
  editImageCurrentPath.value = product.image_path
  editRemoveImage.value = false
  showEditDialog.value = true
}

async function loadCatalog(): Promise<void> {
  const [nextCategories, nextProducts] = await Promise.all([
    listCategories(),
    listProducts(undefined, true)
  ])
  categories.value = nextCategories
  products.value = nextProducts
}

async function refreshCatalog(): Promise<void> {
  try {
    await loadCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

async function submitCategory(): Promise<void> {
  isSubmittingCategory.value = true
  resetMessages()

  try {
    await createCategory({ name: categoryName.value })
    categoryName.value = ''
    message.value = 'Categoria criada com sucesso.'
    await refreshCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmittingCategory.value = false
  }
}

async function submitProduct(): Promise<void> {
  isSubmittingProduct.value = true
  resetMessages()

  try {
    const createdProduct = await createProduct({
      category_id: selectedCategoryId.value,
      name: productName.value,
      price: formatDecimalPrice(productPriceValue.value),
      emoji: productEmoji.value?.trim() || undefined
    })

    if (productImageFile.value) {
      await uploadProductImage(createdProduct.id, productImageFile.value)
    }

    resetCreateForm()
    message.value = 'Produto criado com sucesso.'
    await refreshCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmittingProduct.value = false
  }
}

async function submitEditProduct(): Promise<void> {
  if (!editingProductId.value) {
    return
  }

  isSubmittingEdit.value = true
  resetMessages()

  try {
    await updateProduct(editingProductId.value, {
      category_id: editCategoryId.value,
      name: editName.value,
      price: formatDecimalPrice(editPriceValue.value),
      emoji: editEmoji.value?.trim() || null,
      remove_image: editRemoveImage.value
    })

    if (editImageFile.value) {
      await uploadProductImage(editingProductId.value, editImageFile.value)
    }

    showEditDialog.value = false
    message.value = 'Produto atualizado com sucesso.'
    await refreshCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmittingEdit.value = false
  }
}

async function softDeleteProduct(product: Product): Promise<void> {
  resetMessages()

  try {
    await deactivateProduct(product.id)
    message.value = `${product.name} foi inativado.`
    await refreshCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

async function restoreProductItem(product: Product): Promise<void> {
  resetMessages()

  try {
    await restoreProduct(product.id)
    message.value = `${product.name} foi restaurado.`
    await refreshCatalog()
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

onMounted(async () => {
  await refreshCatalog()
})
</script>