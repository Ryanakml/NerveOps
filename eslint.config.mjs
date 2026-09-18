// M0-01 root lint wiring (stable interface; #4 owns full harness).
// Flat config for eslint v9. Minimal: TS files only, no domain rules yet.
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";

export default [
  {
    ignores: ["**/node_modules/**", "**/dist/**", "**/.next/**", "**/coverage/**"]
  },
  {
    files: ["apps/**/*.ts", "apps/**/*.tsx", "apps/**/*.mts", "apps/**/*.cts"],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module"
      }
    },
    plugins: {
      "@typescript-eslint": tseslint
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "no-unused-vars": "off"
    }
  }
];
