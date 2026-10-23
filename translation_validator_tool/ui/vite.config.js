import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: '0.0.0.0',
      allowedHosts: (env.DEV_ALLOWED_HOSTS || '').split(',').map(host => host.trim()).filter(Boolean)
    },
    build: {
      outDir: 'dist',
      sourcemap: true
    }
  }
})
