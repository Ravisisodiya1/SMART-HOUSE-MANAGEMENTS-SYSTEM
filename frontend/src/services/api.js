import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api" });
api.interceptors.request.use((c) => { const t = localStorage.getItem("access"); if (t) c.headers.Authorization = `Bearer ${t}`; return c; });
api.interceptors.response.use((r) => r, async (err) => {
  const o = err.config, rt = localStorage.getItem("refresh");
  if (err.response?.status === 401 && rt && !o._retry && !o.url.includes("auth/")) {
    o._retry = true;
    try { const { data } = await axios.post(api.defaults.baseURL + "/auth/refresh/", { refresh: rt }); localStorage.setItem("access", data.access); o.headers.Authorization = `Bearer ${data.access}`; return api(o); }
    catch { localStorage.clear(); window.location = "/login"; }
  }
  return Promise.reject(err);
});
export const errMsg = (e) => {
  if (!e.response) return "Network error. Please check your connection.";
  const d = e.response.data; if (e.response.status >= 500) return "Something went wrong on our side. Please try again.";
  if (e.response.status === 401) return d?.detail || "Invalid credentials or session expired.";
  if (typeof d === "string") return "Request failed.";
  return d?.detail || Object.entries(d || {}).map(([k, v]) => `${k}: ${[].concat(v).join(" ")}`).join(" | ") || "Request failed.";
};
export default api;
