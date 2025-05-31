// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    strictPort: true, // Exit if port 5173 is unavailable
    host: '127.0.0.1', // Ensure consistent hostname
  },
});
