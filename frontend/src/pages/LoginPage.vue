<template>
  <div
    class="flex min-h-screen items-center justify-center bg-zinc-100 px-4 py-8"
  >
    <Card class="w-full max-w-md">
      <template #title>PDV Local</template>
      <template #subtitle>
        {{ authStore.hasUsers ? 'Entrar' : 'Primeiro acesso' }}
      </template>
      <template #content>
        <div class="flex flex-col gap-4">
          <p class="text-sm text-zinc-600">
            {{
              authStore.hasUsers
                ? 'Informe usuário e PIN.'
                : 'Crie o usuário proprietário para liberar o terminal.'
            }}
          </p>

          <Message
            v-if="authStore.initializationError"
            severity="warn"
            :closable="false"
          >
            API indisponivel: {{ authStore.initializationError }}
          </Message>

          <Message v-if="errorMessage" severity="error" :closable="false">
            {{ errorMessage }}
          </Message>

          <form
            v-if="authStore.hasUsers"
            class="flex flex-col gap-4"
            @submit.prevent="submitLogin"
          >
            <div class="flex flex-col gap-2">
              <label
                class="text-sm font-medium text-zinc-700"
                for="login-username"
                >Usuário</label
              >
              <InputText
                id="login-username"
                v-model="loginUsername"
                autocomplete="username"
              />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-zinc-700" for="login-pin"
                >PIN</label
              >
              <Password
                id="login-pin"
                v-model="loginPin"
                toggle-mask
                :feedback="false"
                fluid
                inputmode="numeric"
                autocomplete="current-password"
              />
            </div>

            <Button
              type="submit"
              :label="isSubmitting ? 'Entrando...' : 'Entrar'"
              :loading="isSubmitting"
            />
          </form>

          <form
            v-else
            class="flex flex-col gap-4"
            @submit.prevent="submitBootstrapOwner"
          >
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-zinc-700" for="owner-name"
                >Nome</label
              >
              <InputText id="owner-name" v-model="ownerFullName" />
            </div>

            <div class="flex flex-col gap-2">
              <label
                class="text-sm font-medium text-zinc-700"
                for="owner-username"
                >Usuário</label
              >
              <InputText
                id="owner-username"
                v-model="ownerUsername"
                autocomplete="username"
              />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-zinc-700" for="owner-pin"
                >PIN</label
              >
              <Password
                id="owner-pin"
                v-model="ownerPin"
                toggle-mask
                :feedback="false"
                fluid
                inputmode="numeric"
              />
            </div>

            <Button
              type="submit"
              :label="isSubmitting ? 'Criando...' : 'Criar usuário'"
              :loading="isSubmitting"
            />
          </form>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { useRouter } from 'vue-router'

import { ApiError } from '@/services/http'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const errorMessage = ref('')

const loginUsername = ref('')
const loginPin = ref('')

const ownerFullName = ref('')
const ownerUsername = ref('')
const ownerPin = ref('')

function readError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Não foi possível concluir a autenticação.'
}

async function submitLogin(): Promise<void> {
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await authStore.login({
      username: loginUsername.value,
      pin: loginPin.value
    })
    await router.replace('/caixa')
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmitting.value = false
  }
}

async function submitBootstrapOwner(): Promise<void> {
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await authStore.bootstrapOwner({
      full_name: ownerFullName.value,
      username: ownerUsername.value,
      pin: ownerPin.value,
      role: 'OWNER'
    })
    await router.replace('/caixa')
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
