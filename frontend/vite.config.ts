import { execSync } from "node:child_process";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

function windowsHostFromWsl() {
  try {
    const route = execSync("ip route show default", { encoding: "utf8" });
    const match = route.match(/default via (\S+)/);
    return match?.[1] ?? null;
  } catch {
    return null;
  }
}

function apiTarget() {
  if (process.env.SGA_API_URL) return process.env.SGA_API_URL;
  if (process.env.WSL_DISTRO_NAME) {
    const host = windowsHostFromWsl();
    if (host) return `http://${host}:8000`;
    return "http://host.docker.internal:8000";
  }
  return "http://127.0.0.1:8000";
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: apiTarget(),
        changeOrigin: true,
      },
    },
  },
});
