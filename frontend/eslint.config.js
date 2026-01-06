import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { globalIgnores } from "eslint/config";
import stylistic from "@stylistic/eslint-plugin";

export default tseslint.config([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "@stylistic": stylistic,
    },
    extends: [js.configs.recommended, tseslint.configs.recommended],
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "react-refresh/only-export-components": "warn",
      "@stylistic/jsx-max-props-per-line": ["error", { maximum: 1 }],
      "@stylistic/jsx-first-prop-new-line": ["error", "multiline"],
      "@stylistic/function-call-argument-newline": ["error", "consistent"],
      "@stylistic/jsx-newline": [
        "error",
        { prevent: true, allowMultilines: true },
      ],
      "@stylistic/jsx-one-expression-per-line": ["error", { allow: "literal" }],
      "@stylistic/semi": ["error", "never"],
      "@stylistic/function-paren-newline": ["error", { minItems: 3 }],
      "@stylistic/multiline-ternary": ["error", "always-multiline"],
      "@stylistic/member-delimiter-style": [
        "warn",
        {
          multiline: {
            delimiter: "none",
            requireLast: false,
          },
          singleline: {
            delimiter: "comma",
            requireLast: false,
          },
        },
      ],
    },
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
]);
