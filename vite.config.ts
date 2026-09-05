import { defineConfig } from "vite";

export default defineConfig({
  root: "src/development-studio/astro-rashi/first-slice",
  build: {
    outDir: "../../../../dist/astro-rashi",
    emptyOutDir: true
  },
  server: {
    port: 4173
  }
});
