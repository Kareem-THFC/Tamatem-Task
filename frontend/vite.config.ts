import path from 'node:path'

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    // Lets modules import each other as "@/api/client" instead of walking up
    // with "../../api/client". The matching path mapping in tsconfig.app.json
    // is what teaches TypeScript and the editor about the same alias.
    alias: { '@': path.resolve(import.meta.dirname, 'src') },
  },
  server: {
    // The Flask API allows http://localhost:3000 by default (see
    // backend/app/config.py), so the dev server matches that rather than
    // Vite's usual 5173, which would be blocked by CORS.
    port: 3000,
    strictPort: true,
  },
})
