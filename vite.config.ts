import { defineConfig } from "vite";

export default defineConfig({
  base: process.env.GITHUB_ACTIONS ? "/Kalp_01/astro-rashi/" : "/",
  root: "src/development-studio/astro-rashi/first-slice",
  build: {
    outDir: "../../../../dist/astro-rashi",
    emptyOutDir: true
  },
  server: {
    port: 4173
  }
});
