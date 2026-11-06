import { fileURLToPath } from 'node:url';
import { loadEnv } from 'vite';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, fileURLToPath(new URL('.', import.meta.url)), 'VITE_');
  return {
    plugins: [react()],
    server: { proxy: { '/api/admin': { target: env.VITE_ADMIN_API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true } } },
    test: { environment: 'jsdom', setupFiles: './src/test/setup.ts', exclude: ['node_modules/**', 'e2e/**'] },
  };
});
