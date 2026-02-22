import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 3000,
    // historyApiFallback: true, // 简化 historyApiFallback 配置，让所有非 API 路径都返回 index.html
    middlewareMode: false,
    proxy: {
      // 使用更精确的路径匹配，只匹配以 /api/ 开头的路径（注意后面有斜杠）
      '^/api/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        // additionalData: `@import "@/styles/variables.scss";`
      }
    }
  }
})