import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // server: {
  //   host: '0.0.0.0',  //모든 IP주소 허용
  //   port: 5173,
  // },
  server : {
    proxy : {
      'api' : {
        target : 'http://127.0.0.1:8000',
        changeOrigin : true,
        secure : false
      }
    }
  }
})
