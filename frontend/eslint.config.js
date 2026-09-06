import js from '@eslint/js'
import globals from 'globals'
import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import eslintConfigPrettier from 'eslint-config-prettier'

export default tseslint.config(
  {
    ignores: [
      'dev-dist',
      'dist',
      'node_modules',
      'src-tauri/resources',
      'src-tauri/target'
    ]
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      globals: {
        ...globals.browser
      },
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    rules: {
      'vue/multi-word-component-names': 'off'
    }
  },
  {
    files: ['scripts/**/*.mjs'],
    languageOptions: {
      globals: {
        ...globals.node
      }
    }
  },
  eslintConfigPrettier
)
