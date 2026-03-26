import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    allowedHosts: ['dylan-drill-organised-missed.trycloudflare.com']
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})