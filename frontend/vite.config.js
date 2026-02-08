import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: process.env.VITE_GAME_SLUG ? `/${process.env.VITE_GAME_SLUG}/` : '/agame/',
  test: {
    environment: 'happy-dom',
    setupFiles: './src/setup-tests.js',
    css: false,
    pool: 'vmThreads',
  },
  server: {
    proxy: process.env.VITE_GAME_SLUG
      ? {
          [`/${process.env.VITE_GAME_SLUG}/api`]: {
            target: 'http://127.0.0.1:8001',
            changeOrigin: true,
            rewrite: (path) => path.replace(new RegExp(`^/${process.env.VITE_GAME_SLUG}`), ''),
          },
        }
      : {
          '/agame/api': {
            target: 'http://127.0.0.1:8001',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/agame/, ''),
          },
        },
  },
})
