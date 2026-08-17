import { createContext, useContext, useState, useCallback, useEffect } from "react";
import authService from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // 앱이 처음 로드되어 localStorage의 토큰으로 세션을 복원하는 동안 true.
  // "잠깐 로그아웃 화면이 보였다가 로그인 화면으로 바뀌는" 깜빡임을 막는 용도.
  const [isLoading, setIsLoading] = useState(true);

  const applySession = useCallback(({ accessToken, user: nextUser }) => {
    localStorage.setItem("pedalup_access_token", accessToken);
    setUser(nextUser);
    setIsAuthenticated(true);
  }, []);

  // 새로고침/재접속 시 accessToken이 남아있으면 /api/member/me 로 사용자 정보를 복원한다.
  useEffect(() => {
    const restoreSession = async () => {
      const token = localStorage.getItem("pedalup_access_token");

      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const nextUser = await authService.getMe();
        setUser(nextUser);
        setIsAuthenticated(true);
      } catch (error) {
        // 토큰이 만료/위조되어 /me가 실패한 경우 로그아웃 상태로 정리한다.
        localStorage.removeItem("pedalup_access_token");
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = useCallback(
    async (credentials) => {
      const session = await authService.login(credentials);
      applySession(session);
      return session;
    },
    [applySession]
  );

  const signup = useCallback(
    async (payload) => {
      const session = await authService.signup(payload);
      applySession(session);
      return session;
    },
    [applySession]
  );

  const loginWithGoogle = useCallback(async () => {
    const session = await authService.loginWithGoogle();
    applySession(session);
    return session;
  }, [applySession]);

  const loginWithKakao = useCallback(async () => {
    const session = await authService.loginWithKakao();
    applySession(session);
    return session;
  }, [applySession]);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, isLoading, login, signup, loginWithGoogle, loginWithKakao, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
