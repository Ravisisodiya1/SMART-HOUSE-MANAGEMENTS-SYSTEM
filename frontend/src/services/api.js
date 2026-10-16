import axios from "axios";

const api = axios.create({
  baseURL: (
    import.meta.env.VITE_API_URL ||
    "https://smart-house-managements-system.onrender.com/api"
  ).replace(/\/+$/, ""),
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem("refresh");

    if (
      error.response?.status === 401 &&
      refreshToken &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("auth/")
    ) {
      originalRequest._retry = true;

      try {
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/refresh/`,
          { refresh: refreshToken }
        );

        localStorage.setItem("access", data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;

        return api(originalRequest);
      } catch {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export const errMsg = (error) => {
  if (!error.response) {
    return "Network error. Please check your connection.";
  }

  const data = error.response.data;

  if (error.response.status >= 500) {
    return "Something went wrong on our side. Please try again.";
  }

  if (error.response.status === 401) {
    return data?.detail || "Invalid credentials or session expired.";
  }

  if (typeof data === "string") {
    return "Request failed.";
  }

  return (
    data?.detail ||
    Object.entries(data || {})
      .map(([key, value]) => `${key}: ${[].concat(value).join(" ")}`)
      .join(" | ") ||
    "Request failed."
  );
};

export default api;