import { spawnSync } from 'node:child_process'

if (process.platform !== 'linux') {
  process.exit(0)
}

const packages = [
  'glib-2.0',
  'gobject-2.0',
  'gio-2.0',
  'gdk-pixbuf-2.0',
  'pango',
  'gtk+-3.0',
  'webkit2gtk-4.1'
]

const missingPackages = packages.filter((pkg) => {
  const result = spawnSync('pkg-config', ['--exists', pkg], {
    stdio: 'ignore'
  })

  return result.status !== 0
})

if (missingPackages.length === 0) {
  process.exit(0)
}

console.error('Desktop native dependency preflight failed on Linux.')
console.error(`Missing pkg-config entries: ${missingPackages.join(', ')}`)
console.error(
  'Install the GTK/WebKit development packages before running Tauri desktop commands.'
)
console.error('Suggested Debian/Ubuntu command:')
console.error(
  'sudo apt update && sudo apt install libglib2.0-dev libgtk-3-dev libgdk-pixbuf-2.0-dev libpango1.0-dev libwebkit2gtk-4.1-dev pkg-config libdbus-1-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev libxdo-dev build-essential'
)
process.exit(1)
