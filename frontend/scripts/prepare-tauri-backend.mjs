import { cpSync, mkdirSync, rmSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const frontendDir = resolve(scriptDir, '..')
const backendDir = resolve(frontendDir, '..', 'backend')
const bundledBackendDir = resolve(
  frontendDir,
  'src-tauri',
  'resources',
  'backend'
)

rmSync(bundledBackendDir, { recursive: true, force: true })
mkdirSync(bundledBackendDir, { recursive: true })

for (const entry of ['app', 'migrations', 'alembic.ini']) {
  cpSync(resolve(backendDir, entry), resolve(bundledBackendDir, entry), {
    recursive: true,
    filter(sourcePath) {
      return !sourcePath.includes('__pycache__') && !sourcePath.endsWith('.pyc')
    }
  })
}
