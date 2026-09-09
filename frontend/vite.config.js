import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/ask": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/orchestrate": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/compare": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/benchmark": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/kb": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
      },
    },
  },
});

