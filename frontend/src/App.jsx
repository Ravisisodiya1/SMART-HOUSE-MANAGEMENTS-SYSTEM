import { useEffect, useState } from "react";
import { Navigate, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import api from "./services/api";
import { MODULES } from "./modules";
import { NAV_ORDER, PAGE_NAMES, UI } from "./ui";
import CrudPage from "./components/CrudPage";
import Dashboard from "./pages/Dashboard";
import { Assistant, House, Profile, Reports } from "./pages/Extra";
import { Auth, Landing } from "./pages/Public";

function Layout({ children }) {
  const { user, logout } = useAuth(), nav = useNavigate(), loc = useLocation(), [open, setOpen] = useState(false), [notes, setNotes] = useState([]), [show, setShow] = useState(false);
  const loadNotes = () => api.get("/notifications/").then((r) => setNotes(r.data.results)).catch(() => {});
  useEffect(() => { const t = setTimeout(loadNotes, 800); return () => clearTimeout(t); }, []);
  const read = async (n) => { await api.patch(`/notifications/${n.id}/`, { is_read: true }); loadNotes(); };
  const unread = notes.filter((n) => !n.is_read).length;
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email;
  const initials = (user.first_name ? user.first_name[0] + (user.last_name?.[0] || "") : (user.email || "?")[0]).toUpperCase();
  const keys = [...NAV_ORDER, ...Object.keys(MODULES).filter((k) => !NAV_ORDER.includes(k))].filter((k) => MODULES[k]);
  const crumb = PAGE_NAMES[loc.pathname] || UI[loc.pathname.split("/")[2]]?.label || MODULES[loc.pathname.split("/")[2]]?.title || "";
  const item = (to, icon, label) => <NavLink key={to} end={to === "/app"} to={to}><span className="ico">{icon}</span>{label}</NavLink>;
  return <div className="app"><aside className={"sidebar " + (open ? "open" : "")} onClick={() => setOpen(false)}>
    <div className="brand"><div className="brandmark">⌂</div><div><strong>Smart House<span>.</span></strong><small>MANAGEMENT SYSTEM</small></div></div>
    <div className="navlabel">WORKSPACE</div>
    <nav className="nav">{item("/app", "▦", "Dashboard")}{item("/app/house", "⌂", "House")}{keys.map((k) => item("/app/" + k, UI[k]?.icon || "•", UI[k]?.label || MODULES[k].title))}
      <div className="navlabel">INSIGHTS & SYSTEM</div>{item("/app/reports", "▥", "Reports & Insights")}{item("/app/assistant", "✦", "AI Assistant")}{item("/app/profile", "☺", "Profile")}</nav>
    <div className="sidebar-bottom"><div className="house-mini"><div className="house-avatar">🏡</div><div><strong>My Home</strong><small>Family workspace</small></div></div></div>
  </aside>
    <div className="main"><header className="topbar"><div style={{ display: "flex", alignItems: "center", gap: 12 }}><button className="icon-btn mobile-menu" onClick={() => setOpen(!open)}>☰</button><div className="crumb">Workspace&nbsp; / &nbsp;<b>{crumb}</b></div></div>
      <div className="top-actions"><div className="notif-wrap"><button className="icon-btn" title="Notifications" onClick={() => setShow(!show)}>🔔{unread > 0 && <span className="dot" />}</button>
        {show && <div className="card notif"><div className="card-head" style={{ marginBottom: 14 }}><div><h3>Notifications</h3><p>{unread} unread</p></div></div>{notes.length === 0 ? <p className="muted-text">No notifications</p> : <div className="activity">{notes.slice(0, 8).map((n) => <div className="activity-row" key={n.id} style={{ opacity: n.is_read ? 0.5 : 1 }} onClick={() => read(n)}><div className="activity-icon si-gold">▤</div><div><strong>{n.title}</strong><p>{n.message}</p></div></div>)}</div>}</div>}</div>
        <div className="profile"><div className="avatar">{initials}</div><div className="profile-text"><strong>{name}</strong><small>Home Owner</small></div></div>
        <button className="btn" onClick={async () => { await logout(); nav("/"); }}>Logout</button></div></header>
      <div className="content">{children}</div></div></div>;
}
export default function App() {
  const { user, loading } = useAuth(), [toastMsg, setToast] = useState("");
  const toast = (m) => { setToast(m); setTimeout(() => setToast(""), 2500); };
  if (loading) return <div className="empty">Loading…</div>;
  const guard = (el) => (user ? <Layout>{el}</Layout> : <Navigate to="/login" />);
  return <>
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={user ? <Navigate to="/app" /> : <Auth mode="login" />} />
      <Route path="/register" element={user ? <Navigate to="/app" /> : <Auth mode="register" />} />
      <Route path="/app" element={guard(<Dashboard />)} />
      <Route path="/app/house" element={guard(<House toast={toast} />)} />
      <Route path="/app/reports" element={guard(<Reports />)} />
      <Route path="/app/assistant" element={guard(<Assistant />)} />
      <Route path="/app/profile" element={guard(<Profile toast={toast} />)} />
      {Object.keys(MODULES).map((k) => <Route key={k} path={"/app/" + k} element={guard(<CrudPage key={k} name={k} toast={toast} />)} />)}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>{toastMsg && <div className="toast">{toastMsg}</div>}</>;
}
