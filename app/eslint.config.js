import eslintConfigPrettier from 'eslint-config-prettier/flat'
import vue from 'eslint-plugin-vue'

export default [
  {
    ignores: ['dist/**', 'coverage/**'],
  },
  ...vue.configs['flat/recommended'],
  eslintConfigPrettier,
]
