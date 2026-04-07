import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/MyPortfolio/',
  
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-three': ['three'],
          'vendor-gsap': ['gsap'],
          'vendor-codemirror': ['codemirror', 'vue-codemirror6', '@codemirror/lang-css', '@codemirror/lang-html', '@codemirror/lang-javascript', '@codemirror/theme-one-dark'],
          'vendor-charts': ['echarts', 'apexcharts', 'vue3-apexcharts'],
          'vendor-markdown': ['markdown-it', 'highlight.js'],
        },
      },
    },
    chunkSizeWarningLimit: 1500,
  }
})