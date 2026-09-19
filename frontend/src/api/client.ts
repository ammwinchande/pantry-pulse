const API_BASE = '/api';
const TOKEN_KEY = 'pantrypulse_token';

/** Read the persisted JWT (if any). */
export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

/** Persist the JWT after a successful login. */
export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* storage unavailable — token will not survive reload */
  }
}

/** Clear the persisted JWT (logout or on 401). */
export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

/**
 * Fetch wrapper for the PantryPulse API.
 * - Prepends /api
 * - Attaches the Bearer token when present
 * - On a 401, clears the stored token and notifies listeners so the UI can
 *   drop back to the auth screen.
 */
export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event('pantrypulse:unauthorized'));
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `API request failed with status ${response.status}`);
  }

  return response.json();
}
