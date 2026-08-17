import api from "../api/axios";
import { DASHBOARD_STATS, ROUTES_MOCK, QUICK_MENU, COMMUNITY_FEED } from "../constants/mockData";

// 향후 FastAPI: GET /api/dashboard
async function getDashboard() {
  const { data } = await api.get("/api/dashboard");
  return data;
}

const dashboardService = { getDashboard };
export default dashboardService;
