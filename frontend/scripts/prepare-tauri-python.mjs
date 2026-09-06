import { createHash } from 'node:crypto'
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync
} from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const frontendDir = resolve(scriptDir, '..')
const backendDir = resolve(frontendDir, '..', 'backend')
const backendPyprojectPath = resolve(backendDir, 'pyproject.toml')
const runtimeRoot = resolve(frontendDir, 'src-tauri', 'resources', 'python')
const runtimeStampPath = resolve(runtimeRoot, '.pdv-python-runtime.json')

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: 'pipe',
    encoding: 'utf-8',
    ...options
  })

  if (result.status !== 0) {
    const stderr = result.stderr?.trim()
    const stdout = result.stdout?.trim()
    const details =
      stderr ||
      stdout ||
      `command exited with code ${result.status ?? 'unknown'}`
    throw new Error(`${command} ${args.join(' ')} failed: ${details}`)
  }

  return result.stdout?.trim() ?? ''
}

function commandExists(command) {
  const result = spawnSync(command, ['--version'], {
    stdio: 'ignore'
  })

  return result.status === 0
}

function resolveBuildPython() {
  const candidates = []

  if (process.env.PDV_DESKTOP_BUILD_PYTHON) {
    candidates.push(process.env.PDV_DESKTOP_BUILD_PYTHON)
  }

  if (process.platform === 'win32') {
    candidates.push('python')
    candidates.push('py')
  } else {
    candidates.push('python3')
    candidates.push('python')
  }

  for (const candidate of candidates) {
    if (commandExists(candidate)) {
      return candidate
    }
  }

  throw new Error(
    'No suitable Python executable was found. Set PDV_DESKTOP_BUILD_PYTHON to a Python 3.13+ interpreter.'
  )
}

function resolveRuntimePythonPath() {
  if (process.platform === 'win32') {
    return resolve(runtimeRoot, 'Scripts', 'python.exe')
  }

  return resolve(runtimeRoot, 'bin', 'python3')
}

function readPythonMetadata(pythonCommand) {
  const metadata = run(pythonCommand, [
    '-c',
    [
      'import json, platform, sys',
      'print(json.dumps({',
      '  "version": list(sys.version_info[:3]),',
      '  "executable": sys.executable,',
      '  "platform": platform.platform(),',
      '}, sort_keys=True))'
    ].join('\n')
  ])

  const parsed = JSON.parse(metadata)
  const [major, minor] = parsed.version

  if (major < 3 || (major === 3 && minor < 13)) {
    throw new Error(
      `Desktop runtime build requires Python 3.13+, but ${pythonCommand} resolved to ${parsed.version.join('.')}.`
    )
  }

  return parsed
}

function computeDependencyFingerprint(pythonMetadata) {
  const hash = createHash('sha256')
  hash.update(readFileSync(backendPyprojectPath, 'utf-8'))
  hash.update(
    JSON.stringify({
      executable: pythonMetadata.executable,
      version: pythonMetadata.version,
      platform: pythonMetadata.platform
    })
  )
  return hash.digest('hex')
}

function readExistingStamp() {
  if (!existsSync(runtimeStampPath)) {
    return null
  }

  return JSON.parse(readFileSync(runtimeStampPath, 'utf-8'))
}

function shouldReuseRuntime(fingerprint) {
  if (!existsSync(resolveRuntimePythonPath())) {
    return false
  }

  const stamp = readExistingStamp()
  return stamp?.fingerprint === fingerprint
}

function ensureFreshRuntimeRoot() {
  rmSync(runtimeRoot, { recursive: true, force: true })
  mkdirSync(runtimeRoot, { recursive: true })
}

function createVirtualEnvironment(pythonExecutable) {
  const venvResult = spawnSync(pythonExecutable, ['-m', 'venv', runtimeRoot], {
    cwd: frontendDir,
    stdio: 'pipe',
    encoding: 'utf-8'
  })

  if (venvResult.status === 0) {
    return
  }

  if (!commandExists('uv')) {
    const failureDetails = (venvResult.stderr || venvResult.stdout || '').trim()
    throw new Error(
      [
        'python -m venv failed and uv is not available.',
        'Install python3-venv or uv, or set PDV_DESKTOP_BUILD_PYTHON to a Python with venv support.',
        failureDetails
      ]
        .filter(Boolean)
        .join(' ')
    )
  }

  const failureDetails = (venvResult.stderr || venvResult.stdout || '').trim()
  if (failureDetails) {
    console.warn('python -m venv failed; falling back to uv venv')
  }

  rmSync(runtimeRoot, { recursive: true, force: true })
  mkdirSync(runtimeRoot, { recursive: true })

  run('uv', ['venv', '--clear', '--python', pythonExecutable, runtimeRoot], {
    cwd: frontendDir,
    stdio: 'inherit'
  })
}

function installRuntime(pythonMetadata) {
  ensureFreshRuntimeRoot()
  createVirtualEnvironment(pythonMetadata.executable)

  const runtimePython = resolveRuntimePythonPath()

  if (commandExists('uv')) {
    run(
      'uv',
      ['pip', 'install', '--python', runtimePython, '--reinstall', backendDir],
      {
        cwd: frontendDir,
        stdio: 'inherit'
      }
    )
    return
  }

  run(runtimePython, ['-m', 'pip', 'install', '--upgrade', 'pip'], {
    cwd: frontendDir,
    stdio: 'inherit'
  })

  run(runtimePython, ['-m', 'pip', 'install', '--no-cache-dir', backendDir], {
    cwd: frontendDir,
    stdio: 'inherit'
  })
}

function writeRuntimeStamp(pythonMetadata, fingerprint) {
  writeFileSync(
    runtimeStampPath,
    JSON.stringify(
      {
        fingerprint,
        pythonExecutable: pythonMetadata.executable,
        pythonVersion: pythonMetadata.version,
        platform: pythonMetadata.platform
      },
      null,
      2
    ) + '\n',
    'utf-8'
  )
}

const buildPython = resolveBuildPython()
const pythonMetadata = readPythonMetadata(buildPython)
const fingerprint = computeDependencyFingerprint(pythonMetadata)

if (shouldReuseRuntime(fingerprint)) {
  console.log(`Reusing embedded desktop Python runtime from ${runtimeRoot}`)
  process.exit(0)
}

console.log(`Preparing embedded desktop Python runtime with ${buildPython}`)
installRuntime(pythonMetadata)
writeRuntimeStamp(pythonMetadata, fingerprint)
console.log(`Embedded desktop Python runtime ready at ${runtimeRoot}`)
