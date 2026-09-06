<template>
  <Dialog
    :visible="visible"
    modal
    :header="title"
    :style="{ width: '56rem', maxWidth: '96vw' }"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="flex flex-col gap-4">
      <div v-if="source" class="catalog-cropper-shell">
        <Cropper
          ref="cropperRef"
          class="catalog-cropper"
          :src="source"
          image-restriction="fit-area"
          :stencil-props="{ aspectRatio: 1 }"
        />
      </div>

      <Message v-else severity="warn" :closable="false"
        >Selecione uma imagem para continuar.</Message
      >
      <Message v-if="errorMessage" severity="error" :closable="false">{{
        errorMessage
      }}</Message>

      <div class="text-sm text-zinc-500">
        Ajuste o enquadramento para um recorte quadrado. A imagem será exportada
        em boa qualidade para manter o visual do produto consistente.
      </div>
    </div>

    <template #footer>
      <Button
        label="Cancelar"
        severity="secondary"
        text
        @click="emit('update:visible', false)"
      />
      <Button
        label="Aplicar corte"
        :disabled="!source"
        :loading="isApplying"
        @click="applyCrop"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

interface CropperResult {
  canvas?: HTMLCanvasElement | null
}

interface CropperInstance {
  getResult: () => CropperResult
}

const props = defineProps<{
  visible: boolean
  source: string | null
  title?: string
  fileName?: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  apply: [payload: { file: File; previewUrl: string }]
}>()

const cropperRef = ref<CropperInstance | null>(null)
const isApplying = ref(false)
const errorMessage = ref('')

async function canvasToFile(canvas: HTMLCanvasElement): Promise<File> {
  const blob = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, 'image/webp', 0.92)
  })

  if (!blob) {
    throw new Error('Não foi possível gerar a imagem cortada.')
  }

  return new File([blob], props.fileName ?? 'produto.webp', {
    type: 'image/webp'
  })
}

async function applyCrop(): Promise<void> {
  errorMessage.value = ''

  if (!props.source || !cropperRef.value) {
    errorMessage.value = 'Selecione uma imagem antes de continuar.'
    return
  }

  const result = cropperRef.value.getResult()
  const canvas = result.canvas

  if (!canvas) {
    errorMessage.value = 'Não foi possível ler o recorte atual.'
    return
  }

  isApplying.value = true

  try {
    const file = await canvasToFile(canvas)
    emit('apply', {
      file,
      previewUrl: URL.createObjectURL(file)
    })
    emit('update:visible', false)
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : 'Não foi possível aplicar o corte.'
  } finally {
    isApplying.value = false
  }
}
</script>
