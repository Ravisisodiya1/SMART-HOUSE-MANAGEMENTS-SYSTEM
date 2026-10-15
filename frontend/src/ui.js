// UI-only metadata (icons, labels, descriptions) used by the sidebar and page headers.
export const UI = {
  income:      { label: "Income",           icon: "↗",  tone: "teal",   eyebrow: "HOUSEHOLD FINANCES",    desc: "Track salary, freelance earnings and contributions." },
  expenses:    { label: "Expenses",         icon: "↘",  tone: "blue",   eyebrow: "HOUSEHOLD FINANCES",    desc: "Review household purchases and everyday spending." },
  budgets:     { label: "Budgets",          icon: "◉",  tone: "purple", eyebrow: "PLAN & CONTROL",        desc: "Set limits and see how your spending compares with each plan." },
  bills:       { label: "Bills & Payments", icon: "▤",  tone: "gold",   eyebrow: "PAYMENTS & REMINDERS",  desc: "Keep due dates visible and stay ahead of household payments." },
  tasks:       { label: "Tasks & Chores",   icon: "☑",  tone: "teal",   eyebrow: "HOME OPERATIONS",       desc: "Coordinate household work and keep responsibilities clear." },
  shopping:    { label: "Shopping List",    icon: "🛒", tone: "blue",   eyebrow: "SHOPPING & INVENTORY",  desc: "Keep shopping organized, from essentials to weekly groceries." },
  assets:      { label: "Home Assets",      icon: "⌂",  tone: "purple", eyebrow: "ASSETS & INVENTORY",    desc: "A useful inventory of appliances and important household items." },
  maintenance: { label: "Maintenance",      icon: "⚙",  tone: "gold",   eyebrow: "HOME CARE",             desc: "Track preventive care, repairs and warranty dates." },
  documents:   { label: "Documents",        icon: "▧",  tone: "teal",   eyebrow: "FILES & RECORDS",       desc: "A central place for important household records." },
  family:      { label: "Family Members",   icon: "♧",  tone: "blue",   eyebrow: "YOUR HOME TEAM",        desc: "Share responsibilities and keep your household connected." },
};
export const NAV_ORDER = ["income", "expenses", "budgets", "bills", "tasks", "shopping", "assets", "maintenance", "documents", "family"];
export const PAGE_NAMES = { "/app": "Dashboard", "/app/house": "House", "/app/reports": "Reports & Insights", "/app/assistant": "AI Assistant", "/app/profile": "Profile" };

// maps a status / priority / condition value to a pill colour
export const pillClass = (v) => {
  const s = String(v ?? "").toLowerCase();
  if (["paid", "completed", "active", "purchased", "excellent", "good", "low"].includes(s)) return "paid";
  if (["overdue", "cancelled", "urgent", "high", "poor", "inactive"].includes(s)) return "overdue";
  if (s === "in progress") return "inprogress";
  return "pending";
};
