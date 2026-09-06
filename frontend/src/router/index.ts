import { createRouter, createWebHistory } from 'vue-router'

import AppShell from '@/layouts/AppShell.vue'
import { useAuthStore } from '@/stores/auth'
import { pinia } from '@/stores/index'

const CatalogPage = () => import('@/pages/CatalogPage.vue')
const CashRegisterPage = () => import('@/pages/CashRegisterPage.vue')
const DashboardPage = () => import('@/pages/DashboardPage.vue')
const ExpensesPage = () => import('@/pages/ExpensesPage.vue')
const LoginPage = () => import('@/pages/LoginPage.vue')
const ReportsPage = () => import('@/pages/ReportsPage.vue')
const UsersPage = () => import('@/pages/UsersPage.vue')

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
