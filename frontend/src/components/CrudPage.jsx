import { useCallback, useEffect, useState } from "react";
import api, { errMsg } from "../services/api";
import { MODULES } from "../modules";
import { UI, pillClass } from "../ui";
const label = (s) => s.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

export default function CrudPage({ name, toast }) {
  const m = MODULES[name], u = UI[name] || {}, [rows, setRows] = useState([]), [count, setCount] = useState(0), [page, setPage] = useState(1);
  const [q, setQ] = useState(""), [edit, setEdit] = useState(null), [form, setForm] = useState({}), [err, setErr] = useState(""), [loading, setLoading] = useState(true);
  const load = useCallback(() => {
    setLoading(true);
    api.get(`/${name}/`, { params: { search: q || undefined, page } }).then((r) => { setRows(r.data.results); setCount(r.data.count); setErr(""); }).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  }, [name, q, page]);
  useEffect(() => { setPage(1); }, [name, q]);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);

  const open = (row) => { setEdit(row || {}); setForm(row ? { ...row } : {}); setErr(""); };
  const save = async () => {
    const fd = new FormData();
    m.fields.forEach(([f, type]) => { const v = form[f]; if (type === "file") { if (v instanceof File) fd.append(f, v); } else if (v !== undefined && v !== null && v !== "") fd.append(f, v); else if (type === "checkbox") fd.append(f, false); });
    try { edit.id ? await api.patch(`/${name}/${edit.id}/`, fd) : await api.post(`/${name}/`, fd); toast(edit.id ? "Updated" : "Added"); setEdit(null); load(); }
    catch (e) { setErr(errMsg(e)); }
  };
  const del = async (r) => { if (!confirm("Delete this record? This cannot be undone.")) return; try { await api.delete(`/${name}/${r.id}/`); toast("Deleted"); load(); } catch (e) { toast(errMsg(e)); } };
  const csv = async () => { const r = await api.get("/reports/", { params: { type: m.csv, format: "csv" }, responseType: "blob" }); const a = document.createElement("a"); a.href = URL.createObjectURL(r.data); a.download = `${m.csv}.csv`; a.click(); };
  const cell = (r, c) => c === "file" ? (r.file ? <a href={r.file} target="_blank" rel="noreferrer">Download</a> : "-")
    : ["status", "priority", "condition"].includes(c) && r[c] ? <span className={"pill " + pillClass(r[c])}>{String(r[c])}</span> : String(r[c] ?? "-");

  return (<div>
    <div className="pagehead"><div><div className="eyebrow">{u.eyebrow || "HOUSEHOLD MANAGEMENT"}</div><h1>{m.title}</h1><p>{u.desc || "Track and organize your household records."}</p></div>
      <div className="actions">{m.csv && <button className="btn" onClick={csv}>↧ Export CSV</button>}<button className="btn primary" onClick={() => open()}>＋ Add new</button></div></div>
    <div className="toolbar"><input placeholder="Search records..." value={q} onChange={(e) => setQ(e.target.value)} /></div>
    {err && !edit && <div className="err">{err}</div>}
    <div className="card table-card">{loading ? <div className="empty">Loading…</div> : rows.length === 0 ? <div className="empty">No records yet. Click “Add new” to create one.</div> :
      <table><thead><tr>{m.cols.map((c) => <th key={c}>{label(c)}</th>)}<th>Action</th></tr></thead>
        <tbody>{rows.map((r) => <tr key={r.id}>{m.cols.map((c) => <td key={c}>{cell(r, c)}</td>)}
          <td><button className="link" onClick={() => open(r)}>Edit</button> <button className="link del" onClick={() => del(r)}>Delete</button></td></tr>)}</tbody></table>}</div>
    <div className="pager"><button className="btn" disabled={page < 2} onClick={() => setPage(page - 1)}>Prev</button><span>Page {page} · {count} records</span><button className="btn" disabled={page * 20 >= count} onClick={() => setPage(page + 1)}>Next</button></div>
    {edit && <div className="modal-backdrop"><div className="modal"><div className="modal-head"><h2>{edit.id ? "Edit" : "Add"} {m.title}</h2><button className="close" onClick={() => setEdit(null)}>×</button></div>
      <div className="form-grid">{m.fields.map(([f, type = "text", opts]) => <div key={f} className={"field" + (type === "textarea" || type === "file" || f === "title" ? " full" : "")}><label>{label(f)}</label>
        {type === "select" ? <select value={form[f] ?? ""} onChange={(e) => setForm({ ...form, [f]: e.target.value })}><option value="">Select…</option>{opts.map((o) => <option key={o}>{o}</option>)}</select>
        : type === "textarea" ? <textarea rows={2} value={form[f] ?? ""} onChange={(e) => setForm({ ...form, [f]: e.target.value })} />
        : type === "file" ? <input type="file" onChange={(e) => setForm({ ...form, [f]: e.target.files[0] })} />
        : type === "checkbox" ? <input type="checkbox" style={{ width: "auto" }} checked={!!form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.checked })} />
        : <input type={type} step="any" value={form[f] ?? ""} onChange={(e) => setForm({ ...form, [f]: e.target.value })} />}</div>)}</div>
      {err && <div className="err">{err}</div>}<div className="modal-actions"><button className="btn" onClick={() => setEdit(null)}>Cancel</button><button className="btn primary" onClick={save}>Save record</button></div></div></div>}
  </div>);
}
