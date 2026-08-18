import api from "../api/axios";

// FastAPI: GET /api/routes
async function getRoutes() {
  const { data } = await api.get("/api/routes");
  return data;
}

// FastAPI: GET /api/routes/{id}
async function getRouteDetail(id) {
  const { data } = await api.get(`/api/routes/${id}`);
  return data;
}

// FastAPI: GET /api/routes?type=personal — 개인 자전거 루트만 (따릉이 제외)
async function getPersonalRoutes() {
  const { data } = await api.get("/api/routes", { params: { type: "personal" } });
  return data;
}

const routeService = { getRoutes, getRouteDetail, getPersonalRoutes };
export default routeService;