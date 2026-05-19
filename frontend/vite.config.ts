import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load environment variables based on mode
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    optimizeDeps: {
      include: [
        '@mui/material',
        '@mui/icons-material',
        '@mui/x-date-pickers',
        '@mui/x-date-pickers/AdapterDayjs',
        '@mui/x-date-pickers/LocalizationProvider',
        '@mui/x-date-pickers/DateTimePicker',
        'dayjs',
      ],
    },
    server: {
      host: '0.0.0.0',
      allowedHosts: true,
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
