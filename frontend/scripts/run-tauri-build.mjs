import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync, readdirSync, renameSync, rmSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const frontendDir = resolve(scriptDir, '..')
const tauriDir = resolve(frontendDir, 'src-tauri')
const tauriConfigPath = resolve(tauriDir, 'tauri.conf.json')
const bundleAppImageDir = resolve(tauriDir, 'target', 'release', 'bundle', 'appimage')
const linuxdeployPath = resolve(process.env.HOME ?? '', '.cache', 'tauri', 'linuxdeploy-x86_64.AppImage')

function withLinuxAppImageEnv() {
  const env = { ...process.env }

  if (process.platform === 'linux' && !env.APPIMAGE_EXTRACT_AND_RUN) {
    env.APPIMAGE_EXTRACT_AND_RUN = '1'
    console.log('Linux desktop build will run AppImage tooling with APPIMAGE_EXTRACT_AND_RUN=1.')
  }

  return env
}

function run(command, commandArgs, env = process.env, cwd = frontendDir) {
  const result = spawnSync(command, commandArgs, {
    stdio: 'inherit',
    env,
    cwd
  })

  if (result.error) {
    throw result.error
  }

  return result.status ?? 1
}

function parseBundles(rawArgs) {
  const forwardedArgs = []
  let bundles = null

  for (let index = 0; index < rawArgs.length; index += 1) {
    const current = rawArgs[index]

    if (current === '--bundles') {
      bundles = rawArgs[index + 1]?.split(',').map((item) => item.trim()).filter(Boolean) ?? []
      index += 1
      continue
    }

    if (current.startsWith('--bundles=')) {
      bundles = current.slice('--bundles='.length).split(',').map((item) => item.trim()).filter(Boolean)
      continue
    }

    forwardedArgs.push(current)
  }

  return {
    bundles,
    forwardedArgs
  }
}

function readTauriConfig() {
  return JSON.parse(readFileSync(tauriConfigPath, 'utf-8'))
}

function findAppDir() {
  if (!existsSync(bundleAppImageDir)) {
    throw new Error(`AppImage bundle directory not found at ${bundleAppImageDir}`)
  }

  const entry = readdirSync(bundleAppImageDir, { withFileTypes: true }).find((item) => item.isDirectory() && item.name.endsWith('.AppDir'))

  if (!entry) {
    throw new Error(`No AppDir was generated under ${bundleAppImageDir}`)
  }

  return resolve(bundleAppImageDir, entry.name)
}

function normalizeAppImageName() {
  const config = readTauriConfig()
  return `${config.productName}_${config.version}_amd64.AppImage`
}

function removeExistingAppImages() {
  if (!existsSync(bundleAppImageDir)) {
    return
  }

  for (const entry of readdirSync(bundleAppImageDir, { withFileTypes: true })) {
    if (entry.isFile() && entry.name.endsWith('.AppImage')) {
      rmSync(resolve(bundleAppImageDir, entry.name), { force: true })
    }
  }
}

function finalizeManualAppImage() {
  const outputName = normalizeAppImageName()
  const outputPath = resolve(bundleAppImageDir, outputName)
  const candidateDirectories = [bundleAppImageDir, frontendDir]

  if (existsSync(outputPath)) {
    console.log(`Finished 1 bundle at:\n    ${outputPath}`)
    return
  }

  const source = candidateDirectories
    .filter((directory) => existsSync(directory))
    .flatMap((directory) =>
      readdirSync(directory, { withFileTypes: true })
        .filter((entry) => entry.isFile() && entry.name.endsWith('.AppImage'))
        .map((entry) => resolve(directory, entry.name))
    )
    .find((candidate) => candidate !== outputPath)

  if (!source) {
    throw new Error('linuxdeploy completed without producing an AppImage artifact.')
  }

  if (source !== outputPath) {
    rmSync(outputPath, { force: true })
    renameSync(source, outputPath)
  }

  console.log(`Finished 1 bundle at:\n    ${outputPath}`)
}

function runManualLinuxDeploy(env) {
  if (!existsSync(linuxdeployPath)) {
    throw new Error(`linuxdeploy AppImage not found at ${linuxdeployPath}`)
  }

  removeExistingAppImages()
  const appDir = findAppDir()
  const status = run(linuxdeployPath, ['--appdir', appDir, '--output', 'appimage'], {
    ...env,
    ARCH: 'x86_64'
  }, bundleAppImageDir)

  if (status !== 0) {
    process.exit(status)
  }

  finalizeManualAppImage()
}

const args = process.argv.slice(2)
const env = withLinuxAppImageEnv()
const { bundles, forwardedArgs } = parseBundles(args)

if (process.platform !== 'linux') {
  process.exit(run('pnpm', ['exec', 'tauri', 'build', ...args], env))
}

const effectiveBundles = bundles ?? ['appimage', 'deb']
const includesAppImage = effectiveBundles.includes('appimage')
const otherBundles = effectiveBundles.filter((bundle) => bundle !== 'appimage')

if (otherBundles.length > 0) {
  const otherStatus = run('pnpm', ['exec', 'tauri', 'build', ...forwardedArgs, '--bundles', otherBundles.join(',')], env)
  if (otherStatus !== 0) {
    process.exit(otherStatus)
  }
}

if (!includesAppImage) {
  process.exit(0)
}

const appImageStatus = run('pnpm', ['exec', 'tauri', 'build', ...forwardedArgs, '--bundles', 'appimage'], env)

if (appImageStatus === 0) {
  process.exit(0)
}

console.warn('Tauri AppImage step failed; retrying linuxdeploy manually against the generated AppDir.')
runManualLinuxDeploy(env)