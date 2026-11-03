import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// O preview do Base44 chega por um proxy com o Host do sandbox e o Origin do
// domínio público. Os valores são environment-specific, por isso vêm sempre
// do ambiente e só são usados quando BASE44_PREVIEW_MODE === '1'.
const dominioSandbox = process.env.BASE44_SANDBOX_HOST_DOMAIN
const sufixoPreview = process.env.BASE44_PUBLIC_HOST_SUFFIX
const emPreview = process.env.BASE44_PREVIEW_MODE === '1'

const hostsPermitidos = [
  dominioSandbox ? `.${dominioSandbox}` : null,
  sufixoPreview ? `3000-${sufixoPreview}` : null,
].filter((host): host is string => host !== null)

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // Bind mounts não propagam eventos de ficheiros em todos os hosts.
    watch: { usePolling: true },
    allowedHosts: emPreview && hostsPermitidos.length > 0 ? hostsPermitidos : undefined,
    proxy: {
      // Deixa a página falar com o servidor WebSocket na mesma origem quando
      // se define VITE_WS_URL=/ws (usado no sandbox). Por omissão a página
      // liga-se diretamente a ws://localhost:8000/ws.
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true },
    },
  },
})
