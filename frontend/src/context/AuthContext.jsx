import { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";
const Ctx = createContext(null); export const useAuth = () => useContext(Ctx);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null), [loading, setLoading] = useState(true);
  useEffect(() => { if (localStorage.getItem("access")) api.get("/auth/profile/").then((r) => setUser(r.data)).catch(() => localStorage.clear()).finally(() => setLoading(false)); else setLoading(false); }, []);
  const store = (d) => { localStorage.setItem("access", d.access); localStorage.setItem("refresh", d.refresh); };
  const login = async (email, password) => { const { data } = await api.post("/auth/login/", { username: email.toLowerCase(), password }); store(data); setUser((await api.get("/auth/profile/")).data); };
  const register = async (form) => { const { data } = await api.post("/auth/register/", form); store(data); setUser(data.user); };
  const logout = async () => { try { await api.post("/auth/logout/", { refresh: localStorage.getItem("refresh") }); } catch {} localStorage.clear(); setUser(null); };
  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>;
}
