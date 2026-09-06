import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import VueDevTools from 'vite-plugin-vue-devtools'

const isTauriBuild = Boolean(process.env.TAURI_ENV_PLATFORM)

const plugins = [vue(), VueDevTools(), tailwindcss()]

if (!isTauriBuild) {
  plugins.push(
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icon.svg'],
      devOptions: {
        enabled: true,
        type: 'module'
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff,woff2}'],
        runtimeCaching: [
          {
            // GET para rotas da API: tenta rede, cai no cache quando offline
            urlPattern: /\/api\/v1\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 horas
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            // POST /sales: fila offline — sincroniza automaticamente quando a rede voltar
            urlPattern: /\/api\/v1\/sales/,
            method: 'POST',
            handler: 'NetworkOnly',
            options: {
              backgroundSync: {
                name: 'salesQueue',
                options: {
                  maxRetentionTime: 24 * 60 // manter na fila por 24 horas (em minutos)
                }
              }
            }
          }
        ]
      },
      manifest: {
        name: 'PDV Local',
        short_name: 'PDV',
        description:
          'PDV local-first para operação de caixa e controle do negócio.',
        theme_color: '#9a3412',
        background_color: '#fff7ed',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/icon.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ]
      }
    })
  )
}

export default defineConfig({
  plugins,
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true
  }
})
