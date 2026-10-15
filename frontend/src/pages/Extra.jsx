import { useEffect, useRef, useState } from "react";
import api, { errMsg } from "../services/api";
const lab = (s) => s.replace("_", " ").replace(/^./, (c) => c.toUpperCase());
export function Assistant() {
  const [msgs, setMsgs] = useState([{ r: "a", t: "Hi! Ask me about your spending, bills, tasks, savings or warranties." }]), [txt, setTxt] = useState(""), end = useRef();
  useEffect(() => end.current?.scrollIntoView(), [msgs]);
  const send = async (m = txt) => {
    if (!m.trim()) return; setMsgs((x) => [...x, { r: "u", t: m }]); setTxt("");
    try { const { data } = await api.post("/ai/chat/", { message: m }); setMsgs((x) => [...x, { r: "a", t: data.reply }]); } catch (e) { setMsgs((x) => [...x, { r: "a", t: errMsg(e) }]); }
  };
  return <div style={{ maxWidth: 720 }}><div className="pagehead"><div><div className="eyebrow">SMART SUGGESTIONS</div><h1>AI Household Assistant</h1><p>Suggestions only — the assistant never changes your data.</p></div></div>
    <div className="card"><div className="chips">{["How much did I spend this month?", "Which category has the highest expense?", "Which bills are due this week?", "Show my pending tasks", "Give me my monthly summary"].map((s) => <button key={s} className="btn" onClick={() => send(s)}>{s}</button>)}</div>
      <div className="chat">{msgs.map((m, i) => <p key={i} className={"msg " + m.r}>{m.t}</p>)}<div ref={end} /></div>
      <div className="send-row"><input value={txt} onChange={(e) => setTxt(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Ask something…" /><button className="btn primary" onClick={() => send()}>Send</button></div></div></div>;
}
export function House({ toast }) {
  const [h, setH] = useState({ house_name: "", address: "", city: "", state: "", pincode: "", house_type: "Apartment" }), [has, setHas] = useState(false), [err, setErr] = useState("");
  useEffect(() => { api.get("/house/").then((r) => { if (r.data) { setH(r.data); setHas(true); } }); }, []);
  const save = async () => { try { const { data } = await (has ? api.put("/house/", h) : api.post("/house/", h)); setH(data); setHas(true); setErr(""); toast("House saved"); } catch (e) { setErr(errMsg(e)); } };
  return <div style={{ maxWidth: 560 }}><div className="pagehead"><div><div className="eyebrow">YOUR HOME</div><h1>House profile</h1><p>Workspace details for your household.</p></div></div>
    <div className="card"><div className="form-grid">{["house_name", "address", "city", "state", "pincode"].map((f) => <div key={f} className={"field" + (f === "house_name" || f === "address" ? " full" : "")}><label>{lab(f)}</label><input placeholder={f.replace("_", " ")} value={h[f] || ""} onChange={(e) => setH({ ...h, [f]: e.target.value })} /></div>)}
      <div className="field"><label>House type</label><select value={h.house_type} onChange={(e) => setH({ ...h, house_type: e.target.value })}>{["Apartment", "Villa", "Independent House", "Hostel/PG", "Other"].map((t) => <option key={t}>{t}</option>)}</select></div></div>
      {err && <div className="err">{err}</div>}<div className="modal-actions"><button className="btn primary" onClick={save}>{has ? "Update" : "Create"} house</button></div></div></div>;
}
export function Reports() {
  const [type, setType] = useState("expenses"), [from, setFrom] = useState(""), [to, setTo] = useState(""), [rows, setRows] = useState([]);
  const p = { type, date_from: from || undefined, date_to: to || undefined };
  useEffect(() => { api.get("/reports/", { params: p }).then((r) => setRows(r.data)); }, [type, from, to]);
  const dl = async () => { const r = await api.get("/reports/", { params: { ...p, format: "csv" }, responseType: "blob" }); const a = document.createElement("a"); a.href = URL.createObjectURL(r.data); a.download = type + ".csv"; a.click(); };
  const total = rows.reduce((s, r) => s + Number(r.amount || 0), 0);
  return <div><div className="pagehead"><div><div className="eyebrow">MAKE INFORMED DECISIONS</div><h1>Reports & insights</h1><p>Understand your household trends and plan with confidence.</p></div>
    <div className="actions"><button className="btn primary" onClick={dl}>↧ Export CSV</button><button className="btn" onClick={() => window.print()}>Print / PDF</button></div></div>
    <div className="toolbar"><select style={{ width: 160 }} value={type} onChange={(e) => setType(e.target.value)}><option>expenses</option><option>income</option><option>bills</option></select>
      <input type="date" style={{ width: 170 }} value={from} onChange={(e) => setFrom(e.target.value)} /><input type="date" style={{ width: 170 }} value={to} onChange={(e) => setTo(e.target.value)} /></div>
    <div className="grid stats two"><div className="card"><div className="stat-top">Records <span className="stat-icon si-blue">▤</span></div><div className="stat-value">{rows.length}</div></div>
      <div className="card"><div className="stat-top">Total <span className="stat-icon si-teal">↗</span></div><div className="stat-value">₹{total.toLocaleString("en-IN")}</div></div></div></div>;
}
export function Profile({ toast }) {
  const [p, setP] = useState({}), [pw, setPw] = useState({ old_password: "", new_password: "" }), [err, setErr] = useState("");
  useEffect(() => { api.get("/auth/profile/").then((r) => setP(r.data)); }, []);
  const save = async () => { try { await api.patch("/auth/profile/", { first_name: p.first_name, last_name: p.last_name, phone: p.phone }); toast("Profile updated"); } catch (e) { setErr(errMsg(e)); } };
  const chg = async () => { try { await api.post("/auth/change-password/", pw); toast("Password changed"); setPw({ old_password: "", new_password: "" }); setErr(""); } catch (e) { setErr(errMsg(e)); } };
  return <div><div className="pagehead"><div><div className="eyebrow">MAKE IT YOURS</div><h1>Profile</h1><p>Manage your personal details and password.</p></div></div>
    <div className="grid two-col"><div className="card"><div className="card-head"><div><h3>Personal details</h3><p>Your account information</p></div></div><div className="stack">{["first_name", "last_name", "phone"].map((f) => <div className="field" key={f}><label>{lab(f)}</label><input placeholder={f.replace("_", " ")} value={p[f] || ""} onChange={(e) => setP({ ...p, [f]: e.target.value })} /></div>)}</div><div className="modal-actions"><button className="btn primary" onClick={save}>Save</button></div></div>
      <div className="card"><div className="card-head"><div><h3>Change password</h3><p>Keep your account secure</p></div></div><div className="stack"><div className="field"><label>Current password</label><input type="password" placeholder="Current password" value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} /></div><div className="field"><label>New password</label><input type="password" placeholder="New password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></div></div>{err && <div className="err">{err}</div>}<div className="modal-actions"><button className="btn primary" onClick={chg}>Change</button></div></div></div></div>;
}
