import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5176, // Changed to match your actual server port
    host: '0.0.0.0', // Add this line to bind to all network interfaces
    cors: true, // Enable CORS for all origins
    proxy: {
      // Proxy API requests to Django backend
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (path) => path
      }
    },
    allowedHosts: [
      'localhost',
      '*.ngrok-free.app' // This will allow all ngrok domains
    ]
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Customize build if needed
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui-vendor': [
            '@mui/material',
            '@mui/icons-material',
            '@emotion/react',
            '@emotion/styled'
          ]
        }
      }
    }
  }
});