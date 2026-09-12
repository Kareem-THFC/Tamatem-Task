/// <reference types="vite/client" />

// Declaring the variables this project reads turns a typo in an env name into
// a compile error rather than a silent `undefined` at runtime. All three are
// optional: local builds set only the API URL, and the demo credentials exist
// only in the deployed build.
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_DEMO_USERNAME?: string
  readonly VITE_DEMO_PASSWORD?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
