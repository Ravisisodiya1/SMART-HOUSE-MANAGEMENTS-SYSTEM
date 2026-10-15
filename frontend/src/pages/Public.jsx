import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { errMsg } from "../services/api";
const Brand = () => <div className="brand"><div className="brandmark">⌂</div><div><strong>Smart House<span>.</span></strong><small>MANAGEMENT SYSTEM</small></div></div>;
export function Landing() {
  const F = [["Expenses & income", "↗", "teal"], ["Budgets with alerts", "◉", "purple"], ["Bills & reminders", "▤", "gold"], ["Tasks & family", "☑", "blue"], ["Shopping & groceries", "🛒", "teal"], ["Assets, warranties & documents", "▧", "purple"], ["AI insights & chat", "✦", "blue"], ["Reports & CSV export", "▥", "gold"]];
  return <div><div className="pubtop"><Brand /><div className="pub-actions"><Link to="/login">Login</Link><Link className="btn primary" to="/register">Get Started</Link></div></div>
    <div className="hero"><div className="eyebrow">YOUR HOME, IN ONE PLACE</div><h1>Run your whole household from one place</h1><p>Track money, bills, tasks, maintenance and documents — with AI suggestions.</p><Link className="btn primary" to="/register" style={{ padding: "13px 22px", fontSize: 13 }}>Get Started</Link></div>
    <div className="content"><div className="grid feature-grid">{F.map(([f, icon, tone]) => <div className="card" key={f}><div className={"stat-icon si-" + tone}>{icon}</div><b>{f}</b></div>)}</div>
      <div className="notice" style={{ marginTop: 20 }}><div className="notice-icon">🔒</div><div><strong>Security</strong><p>JWT authentication, hashed passwords, per-household data isolation and validated file uploads.</p></div></div></div></div>;
}
export function Auth({ mode }) {
  const { login, register } = useAuth(), nav = useNavigate(), reg = mode === "register";
  const [f, setF] = useState({ email: "", password: "", first_name: "", last_name: "" }), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const submit = async (e) => { e.preventDefault(); if (!f.email || !f.password) return setErr("Email and password are required."); setBusy(true);
    try { reg ? await register(f) : await login(f.email, f.password); nav("/app"); } catch (x) { setErr(errMsg(x)); } setBusy(false); };
  return <div className="authwrap"><form className="card authcard" onSubmit={submit}><Brand /><h2>{reg ? "Create account" : "Welcome back"}</h2><p className="sub">{reg ? "Set up your household workspace." : "Sign in to manage your home."}</p>
    <div className="stack">{reg && <div className="form-grid"><div className="field"><label>First name</label><input placeholder="First name" value={f.first_name} onChange={(e) => setF({ ...f, first_name: e.target.value })} /></div><div className="field"><label>Last name</label><input placeholder="Last name" value={f.last_name} onChange={(e) => setF({ ...f, last_name: e.target.value })} /></div></div>}
      <div className="field"><label>Email</label><input type="email" placeholder="Email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></div><div className="field"><label>Password</label><input type="password" placeholder="Password" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></div></div>
    {err && <div className="err">{err}</div>}<button className="btn primary" disabled={busy} style={{ marginTop: 6 }}>{busy ? "Please wait…" : reg ? "Register" : "Login"}</button>
    <p className="alt">{reg ? <Link to="/login">Already have an account?</Link> : <Link to="/register">Create an account</Link>}</p></form></div>;
}
