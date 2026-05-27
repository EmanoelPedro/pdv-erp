import { createRouter, createWebHistory } from 'vue-router'

import AppShell from '@/layouts/AppShell.vue'
import CatalogPage from '@/pages/CatalogPage.vue'
import CashRegisterPage from '@/pages/CashRegisterPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import ExpensesPage from '@/pages/ExpensesPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import ReportsPage from '@/pages/ReportsPage.vue'
import SalesPage from '@/pages/SalesPage.vue'
import UsersPage from '@/pages/UsersPage.vue'
import { useAuthStore } from '@/stores/auth'
import { pinia } from '@/stores/index'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { public: true }
    },
    {
      path: '/',
      component: AppShell,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardPage,
          meta: { ownerOnly: true }
        },
        {
          path: 'caixa',
          name: 'cash-register',
          component: CashRegisterPage,
          meta: { fullBleed: true }
        },
        {
          path: 'catalogo',
          name: 'catalog',
          component: CatalogPage,
          meta: { ownerOnly: true }
        },
        {
          path: 'usuarios',
          name: 'users',
          component: UsersPage,
          meta: { ownerOnly: true }
        },
        {
          path: 'vendas',
          name: 'sales',
          component: SalesPage
        },
        {
          path: 'despesas',
          name: 'expenses',
          component: ExpensesPage,
          meta: { ownerOnly: true }
        },
        {
          path: 'relatorios',
          name: 'reports',
          component: ReportsPage,
          meta: { ownerOnly: true }
        }
      ]
    }
  ]
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore(pinia)
  await authStore.initialize()

  if (to.meta.public && authStore.isAuthenticated) {
    return { name: 'cash-register' }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.ownerOnly && !authStore.isOwner) {
    return { name: 'cash-register' }
  }

  return true
})
