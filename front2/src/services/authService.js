import api from "../api/axios";

// const MOCK_USER = {
//   id: "mock-user-1",
//   nickname: "김민준",
//   handle: "@minzun_rides",
//   email: "minjun@example.com",
// };

// // 향후 FastAPI: POST /api/auth/login
// async function login({ email, password }) {
//   try {
//     const { data } = await api.post("/api/auth/login", { email, password });
//     return data;
//   } catch {
//     return { accessToken: "mock-access-token", user: MOCK_USER };
//   }
// }

async function login({email, password}) {
  const {data} = await api.post(
    "/api/member/login",
    {
      email,
      password
    }
  );

  if (data.isLogin && data.accessToken) {
    localStorage.setItem(
      "pedalup_access_token",
      data.accessToken
    );
  }
  
  return data;
}

// // 향후 FastAPI: POST /api/auth/signup
// async function signup(payload) {
//   try {
//     const { data } = await api.post("/api/auth/signup", payload);
//     return data;
//   } catch {
//     return { accessToken: "mock-access-token", user: { ...MOCK_USER, nickname: payload.nickname || MOCK_USER.nickname } };
//   }
// }

async function signup(payload) {
  const {data} = await api.post("/api/member/signup", payload);
  return data;
}

// 향후 FastAPI OAuth 연동 지점 — 현재는 UI 전용
async function loginWithGoogle() {
  return login({ email: "google-user@example.com", password: "oauth" });
}

async function loginWithKakao() {
  return login({ email: "kakao-user@example.com", password: "oauth" });
}

// 향후 FastAPI: GET /api/member/me — accessToken으로 로그인 상태 복원 (새로고침 시 사용)
async function getMe() {
  const { data } = await api.get("/api/member/me");
  return data; // { nickname, role }
}

function logout() {
  localStorage.removeItem("pedalup_access_token");
}

const authService = { login, signup, loginWithGoogle, loginWithKakao, logout, getMe };
export default authService;