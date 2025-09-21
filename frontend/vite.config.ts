import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
const usePolling = process.env.CHOKIDAR_USEPOLLING === '1' || process.env.USE_POLLING === '1'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    watch: {
      usePolling,
      interval: 300,
      ignored: ['**/node_modules/**', '**/.git/**']
    },
    fs: { strict: true },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
