<template>
  <section class="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
    <Card>
      <template #title>Novo usuário</template>
      <template #content>
        <form class="flex flex-col gap-4" @submit.prevent="submitUser">
          <Message v-if="message" severity="success" :closable="false">{{
            message
          }}</Message>
          <Message v-if="errorMessage" severity="error" :closable="false">{{
            errorMessage
          }}</Message>

          <div class="flex flex-col gap-2">
            <label
              class="text-sm font-medium text-zinc-700"
              for="user-full-name"
              >Nome</label
            >
            <InputText id="user-full-name" v-model="fullName" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-zinc-700" for="user-username"
              >Usuário</label
            >
            <InputText id="user-username" v-model="username" />
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-zinc-700" for="user-pin"
                >PIN</label
              >
              <Password
                id="user-pin"
                v-model="pin"
                toggle-mask
                :feedback="false"
                fluid
                inputmode="numeric"
              />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-zinc-700" for="user-role"
                >Nivel</label
              >
              <Select
                id="user-role"
                v-model="role"
                :options="roleOptions"
                option-label="label"
                option-value="value"
              />
            </div>
          </div>

          <Button
            type="submit"
            :label="isSubmitting ? 'Salvando...' : 'Cadastrar usuário'"
            :loading="isSubmitting"
          />
        </form>
      </template>
    </Card>

    <Card>
      <template #title>Usuários cadastrados</template>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex justify-end">
            <Button
              label="Atualizar"
              severity="secondary"
              outlined
              @click="loadUsers"
            />
          </div>

          <DataTable :value="users" size="small" striped-rows>
            <Column field="full_name" header="Nome" />
            <Column field="username" header="Usuário" />
            <Column header="Nivel">
              <template #body="slotProps">
                <Tag
                  :severity="
                    slotProps.data.role === 'OWNER' ? 'warn' : 'secondary'
                  "
                  :value="
                    slotProps.data.role === 'OWNER'
                      ? 'Proprietário'
                      : 'Funcionário'
                  "
                />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import { listUsers } from '@/services/auth'
import { ApiError } from '@/services/http'
import { useAuthStore } from '@/stores/auth'
import type { AuthUser, UserRole } from '@/types/auth'

const authStore = useAuthStore()

const fullName = ref('')
const username = ref('')
const pin = ref('')
const role = ref<UserRole>('EMPLOYEE')
const users = ref<AuthUser[]>([])
const isSubmitting = ref(false)
const message = ref('')
const errorMessage = ref('')

const roleOptions = [
  { label: 'Funcionário', value: 'EMPLOYEE' },
  { label: 'Proprietário', value: 'OWNER' }
]

function readError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Não foi possível salvar o usuário.'
}

async function loadUsers(): Promise<void> {
  users.value = await listUsers()
}

async function submitUser(): Promise<void> {
  isSubmitting.value = true
  message.value = ''
  errorMessage.value = ''

  try {
    await authStore.createUser({
      full_name: fullName.value,
      username: username.value,
      pin: pin.value,
      role: role.value
    })
    fullName.value = ''
    username.value = ''
    pin.value = ''
    role.value = 'EMPLOYEE'
    message.value = 'Usuário cadastrado com sucesso.'
    await loadUsers()
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  await loadUsers()
})
</script>
