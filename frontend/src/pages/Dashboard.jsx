import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api, { errMsg } from "../services/api";
import { useAuth } from "../context/AuthContext";
const COLORS = ["#1da896", "#4778ee", "#d69b32", "#8a65d7", "#df5e68", "#06b6d4", "#ec4899", "#84cc16"];
const Stat = ({ t, v, icon, tone, sub, warn }) => <div className="card"><div className="stat-top">{t}<span className={"stat-icon si-" + tone}>{icon}</span></div><div className="stat-value">{v}</div>{sub && <div className={"trend" + (warn ? " warn" : "")}>{sub}</div>}</div>;
export default function Dashboard() {
  const { user } = useAuth(), [d, setD] = useState(null), [err, setErr] = useState("");
  useEffect(() => { api.get("/dashboard/").then((r) => setD(r.data)).catch((e) => setErr(errMsg(e))); }, []);
  if (err) return <div className="err">{err}</div>; if (!d) return <div className="empty">Loading…</div>;
  if (d.no_house) return <div className="notice"><div className="notice-icon">🏡</div><div><strong>Welcome!</strong><p><Link to="/app/house">Create your house profile</Link> to start.</p></div></div>;
  const inr = (n) => "₹" + Number(n).toLocaleString("en-IN");
  const hr = new Date().getHours(), greet = hr < 12 ? "Good morning" : hr < 17 ? "Good afternoon" : "Good evening";
  const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }).toUpperCase();
  const saving = d.month_income - d.month_expense;
  return (<div>
    <div className="pagehead"><div><div className="eyebrow">{today}</div><h1>{greet}{user?.first_name ? ", " + user.first_name : ""} <span style={{ fontSize: 24 }}>✦</span></h1><p>Here's what's happening around your home today.</p></div></div>
    <div className="grid stats">
      <Stat t="Total income" v={inr(d.total_income)} icon="↗" tone="teal" sub="All time" />
      <Stat t="Total expenses" v={inr(d.total_expense)} icon="↘" tone="blue" sub="All time" />
      <Stat t="This month's expenses" v={inr(d.month_expense)} icon="◉" tone="purple" sub="Current month" />
      <Stat t="Savings (this month)" v={inr(saving)} icon="◈" tone="gold" sub={saving >= 0 ? "↗ Healthy cash flow" : "Spending exceeds income"} warn={saving < 0} /></div>
    <div className="grid stats five">
      <Stat t="Pending bills" v={d.pending_bills} icon="▤" tone="gold" sub={`${d.overdue_bills} overdue`} warn={d.overdue_bills > 0} />
      <Stat t="Pending tasks" v={d.pending_tasks} icon="☑" tone="teal" />
      <Stat t="Shopping items" v={d.shopping_items} icon="🛒" tone="blue" />
      <Stat t="Maintenance due" v={d.maintenance_due} icon="⚙" tone="purple" />
      <Stat t="Warranties expiring" v={d.warranty_expiring} icon="⌛" tone="gold" /></div>
    <div className="grid main-grid">
      <div className="card"><div className="card-head"><div><h3>Cash flow overview</h3><p>Income vs expenses · Last 6 months</p></div></div><ResponsiveContainer width="100%" height={240}><BarChart data={d.monthly}><CartesianGrid strokeDasharray="3 3" stroke="#edf0f5" vertical={false} /><XAxis dataKey="month" tick={{ fontSize: 10, fill: "#9aa4b5" }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 10, fill: "#9aa4b5" }} axisLine={false} tickLine={false} /><Tooltip /><Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} /><Bar dataKey="income" fill="#1da896" radius={[6, 6, 0, 0]} /><Bar dataKey="expense" fill="#4778ee" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer></div>
      <div className="card"><div className="card-head"><div><h3>Monthly budget</h3><p>Budget progress</p></div></div>{d.budgets.length === 0 ? <p className="muted-text">No budgets this month.</p> : <div className="budget-list">{d.budgets.map((b, i) => { const color = b.percent >= 100 ? "#df5e68" : b.percent >= 80 ? "#d69b32" : "#1da896"; return <div key={b.category}><div className="budget-item-top"><strong>{b.category}</strong><span>{inr(b.spent)} / {inr(b.limit)}</span></div><div className="progress"><span style={{ width: Math.min(b.percent, 100) + "%", background: color }} /></div><div className="budget-foot"><span>{inr(Math.max(b.limit - b.spent, 0))} remaining</span><b>{Math.round(b.percent)}%</b></div></div>; })}</div>}</div>
    </div>
    <div className="grid main-grid">
      <div className="card"><div className="card-head"><div><h3>Expenses by category</h3><p>This month</p></div></div><ResponsiveContainer width="100%" height={240}><PieChart><Pie data={d.categories} dataKey="total" nameKey="category" outerRadius={85} innerRadius={45} paddingAngle={2} label>{d.categories.map((_, i) => <Cell key={i} fill={COLORS[i % 8]} />)}</Pie><Tooltip /><Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} /></PieChart></ResponsiveContainer></div>
      <div className="card"><div className="card-head"><div><h3>AI suggestions</h3><p>Helpful prompts based on your household data</p></div><Link className="link" to="/app/assistant">Ask the assistant →</Link></div><div className="activity">{d.insights.map((t, i) => <div className="activity-row" key={i}><div className={"activity-icon " + ["si-teal", "si-blue", "si-purple"][i % 3]}>✦</div><div><p style={{ fontSize: 11, color: "#172033", lineHeight: 1.6 }}>{t}</p></div></div>)}</div></div>
    </div>
    <div className="grid bottom-grid">
      <div className="card"><div className="card-head"><div><h3>Recent transactions</h3><p>Your latest household activity</p></div><Link className="link" to="/app/expenses">View all →</Link></div>{d.recent.length ? <div style={{ overflow: "auto" }}><table><thead><tr><th>Transaction</th><th>Date</th><th>Amount</th></tr></thead><tbody>{d.recent.map((r) => <tr key={r.id}><td><div className="transaction"><div className="tx-icon">🧾</div><div><strong>{r.title}</strong></div></div></td><td>{r.date}</td><td><b>{inr(r.amount)}</b></td></tr>)}</tbody></table></div> : <p className="muted-text">None</p>}</div>
      <div className="card"><div className="card-head"><div><h3>Upcoming bills</h3><p>Next 7 days</p></div><Link className="link" to="/app/bills">See all →</Link></div>{d.upcoming_bills.length ? <div className="activity">{d.upcoming_bills.map((b) => <div className="activity-row" key={b.id}><div className="activity-icon si-gold">▤</div><div><strong>{b.bill_type}</strong><p>{inr(b.amount)}</p><time>Due {b.due_date}</time></div></div>)}</div> : <p className="muted-text">None</p>}</div>
    </div></div>);
}
