import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue' // 引入插件

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()], // 告诉 Vite 使用 Vue 插件
})