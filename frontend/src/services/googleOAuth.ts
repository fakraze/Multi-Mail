const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

export function startGoogleOAuth(): void {
  window.location.assign(`${backendBaseUrl.replace(/\/$/, '')}/auth/google/start`)
}
