import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { clearToken, fetchApi, getToken, setToken } from './client';
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  MessageResponse,
  RegisterRequest,
  RegisterResponse,
} from '../types';

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  /** True while the initial /me validation is in flight. */
  loading: boolean;
  isAuthenticated: boolean;
  login: (body: LoginRequest) => Promise<LoginResponse>;
  register: (body: RegisterRequest) => Promise<RegisterResponse>;
  verifyEmail: (token: string) => Promise<AuthUser>;
  requestPasswordReset: (email: string) => Promise<MessageResponse>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<MessageResponse>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<MessageResponse>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Validate the persisted token against /me on mount and whenever it changes.
  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      try {
        const me = await fetchApi<AuthUser>('/auth/me');
        if (!cancelled) setUser(me);
      } catch {
        if (!cancelled) {
          clearToken();
          setTokenState(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  // React to 401s raised by the API client (expired/revoked token).
  useEffect(() => {
    function onUnauthorized() {
      setTokenState(null);
      setUser(null);
    }
    window.addEventListener('pantrypulse:unauthorized', onUnauthorized);
    return () => window.removeEventListener('pantrypulse:unauthorized', onUnauthorized);
  }, []);

  const login = useCallback(async (body: LoginRequest) => {
    const res = await fetchApi<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    setToken(res.access_token);
    setTokenState(res.access_token);
    setUser(res.user);
    return res;
  }, []);

  const register = useCallback(async (body: RegisterRequest) => {
    return await fetchApi<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }, []);

  const verifyEmail = useCallback(async (token: string) => {
    return await fetchApi<AuthUser>('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }, []);

  const requestPasswordReset = useCallback(async (email: string) => {
    return await fetchApi<MessageResponse>('/auth/password-reset/request', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }, []);

  const confirmPasswordReset = useCallback(async (token: string, newPassword: string) => {
    return await fetchApi<MessageResponse>('/auth/password-reset/confirm', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  }, []);

  const changePassword = useCallback(
    async (currentPassword: string, newPassword: string) => {
      return await fetchApi<MessageResponse>('/auth/password-change', {
        method: 'POST',
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
    },
    [],
  );

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: !!token && !!user,
      login,
      register,
      verifyEmail,
      requestPasswordReset,
      confirmPasswordReset,
      changePassword,
      logout,
    }),
    [
      user,
      token,
      loading,
      login,
      register,
      verifyEmail,
      requestPasswordReset,
      confirmPasswordReset,
      changePassword,
      logout,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
