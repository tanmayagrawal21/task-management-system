import pluginVue from 'eslint-plugin-vue'

export default [
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'vue/no-v-model-argument': 'off',
      'vue/multi-word-component-names': 'off',
    },
  },
]
