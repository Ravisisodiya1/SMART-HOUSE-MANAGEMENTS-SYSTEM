import csv
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum
from .models import *

def get_house(u):
    h = House.objects.filter(owner=u).first()
    if h: return h
    m = FamilyMember.objects.filter(user=u).select_related("house").first()
    return m.house if m else None

def _sum(qs, f="amount"): return qs.aggregate(t=Sum(f))["t"] or Decimal(0)

def budget_status(h, today=None):
    today = today or date.today(); out = []
    for b in Budget.objects.filter(house=h, month=today.month, year=today.year):
        spent = _sum(Expense.objects.filter(house=h, category=b.category, date__month=b.month, date__year=b.year))
        out.append(dict(category=b.category, limit=b.monthly_limit, spent=spent, remaining=b.monthly_limit-spent, percent=round(float(spent/b.monthly_limit*100), 1)))
    return out

def dashboard(h):
    today = date.today(); ex = Expense.objects.filter(house=h); inc = Income.objects.filter(house=h)
    month_ex = ex.filter(date__month=today.month, date__year=today.year)
    monthly = []
    for i in range(5, -1, -1):
        y, m = today.year, today.month - i
        while m < 1: m += 12; y -= 1
        monthly.append(dict(month=f"{y}-{m:02d}", expense=float(_sum(ex.filter(date__year=y, date__month=m))), income=float(_sum(inc.filter(date__year=y, date__month=m)))))
    cats = [dict(category=c["category"], total=float(c["t"])) for c in month_ex.values("category").annotate(t=Sum("amount")).order_by("-t")]
    bills = Bill.objects.filter(house=h, status="unpaid")
    return dict(
        total_income=_sum(inc), total_expense=_sum(ex), month_expense=_sum(month_ex),
        month_income=_sum(inc.filter(date__month=today.month, date__year=today.year)),
        pending_bills=bills.count(), overdue_bills=bills.filter(due_date__lt=today).count(),
        upcoming_bills=list(bills.filter(due_date__gte=today, due_date__lte=today+timedelta(days=7)).values("id","bill_type","provider","amount","due_date")),
        pending_tasks=Task.objects.filter(house=h, status__in=["Pending","In Progress"]).count(),
        shopping_items=ShoppingItem.objects.filter(house=h, status="pending").count(),
        maintenance_due=Maintenance.objects.filter(house=h, status="Scheduled", scheduled_date__lte=today+timedelta(days=14)).count(),
        warranty_expiring=Asset.objects.filter(house=h, warranty_expiry__gte=today, warranty_expiry__lte=today+timedelta(days=60)).count(),
        budgets=budget_status(h), recent=list(ex.order_by("-date","-id").values("id","title","category","amount","date")[:6]),
        monthly=monthly, categories=cats, insights=AIService().insights(h))

class RuleBasedAI:
    """Safe local fallback. Only analyses and suggests; never mutates data."""
    def insights(self, h):
        today = date.today(); tips = []
        ex = Expense.objects.filter(house=h)
        cur = ex.filter(date__month=today.month, date__year=today.year)
        prev_m = today.month - 1 or 12; prev_y = today.year if today.month > 1 else today.year - 1
        for c in cur.values("category").annotate(t=Sum("amount")):
            p = _sum(ex.filter(category=c["category"], date__month=prev_m, date__year=prev_y))
            if p and c["t"] > p * Decimal("1.2"):
                tips.append(f"Your {c['category']} spending is over 20% higher than last month. Consider reviewing it.")
        for b in budget_status(h, today):
            if b["percent"] >= 100: tips.append(f"You have exceeded your {b['category']} budget.")
            elif b["percent"] >= 80: tips.append(f"You have used {b['percent']}% of your {b['category']} budget.")
        n = Bill.objects.filter(house=h, status="unpaid", due_date__lte=today+timedelta(days=7)).count()
        if n: tips.append(f"You have {n} bill(s) due within 7 days or overdue.")
        if Asset.objects.filter(house=h, warranty_expiry__gte=today, warranty_expiry__lte=today+timedelta(days=60)).exists():
            tips.append("Some asset warranties expire within 60 days. Check the Assets page.")
        inc = _sum(Income.objects.filter(house=h, date__month=today.month, date__year=today.year)); e = _sum(cur)
        if inc and e > inc * Decimal("0.8"): tips.append("You are spending over 80% of this month's income. Look for savings opportunities.")
        return tips or ["Everything looks healthy. Keep tracking your expenses!"]
    def chat(self, h, q):
        q = q.lower(); d = dashboard_light(h)
        if "spend" in q or "expense" in q and "reduce" not in q: return f"You spent ₹{d['month_expense']} this month."
        if "highest" in q or "category" in q: return f"Highest expense category this month: {d['top']}." if d["top"] else "No expenses recorded this month."
        if "save" in q or "saving" in q: return f"Savings this month: ₹{d['month_income'] - d['month_expense']}."
        if "bill" in q: return f"You have {d['bills']} unpaid bill(s) due within 7 days or overdue."
        if "task" in q: return f"You have {d['tasks']} pending task(s)."
        if "warranty" in q or "asset" in q: return f"{d['warranty']} asset warranty(ies) expire within 60 days."
        if "reduce" in q or "tip" in q: return " ".join(self.insights(h))
        if "summary" in q: return f"Income ₹{d['month_income']}, expenses ₹{d['month_expense']}, savings ₹{d['month_income']-d['month_expense']}, top category: {d['top'] or 'n/a'}, unpaid bills: {d['bills']}, pending tasks: {d['tasks']}."
        return "I can answer questions about spending, savings, bills, tasks, warranties, or give a monthly summary."

def dashboard_light(h):
    t = date.today(); cur = Expense.objects.filter(house=h, date__month=t.month, date__year=t.year)
    top = cur.values("category").annotate(t=Sum("amount")).order_by("-t").first()
    return dict(month_expense=_sum(cur), month_income=_sum(Income.objects.filter(house=h, date__month=t.month, date__year=t.year)),
        top=top["category"] if top else None, bills=Bill.objects.filter(house=h, status="unpaid", due_date__lte=t+timedelta(days=7)).count(),
        tasks=Task.objects.filter(house=h, status__in=["Pending","In Progress"]).count(),
        warranty=Asset.objects.filter(house=h, warranty_expiry__gte=t, warranty_expiry__lte=t+timedelta(days=60)).count())

def AIService():
    """Provider factory. Replace/extend here to plug in an external LLM using settings.AI_API_KEY."""
    return RuleBasedAI()

def sync_notifications(user, h):
    today = date.today()
    for b in Bill.objects.filter(house=h, status="unpaid", due_date__lte=today+timedelta(days=3)):
        Notification.objects.get_or_create(user=user, title=f"Bill due: {b.bill_type}", message=f"{b.bill_type} bill of ₹{b.amount} is due on {b.due_date}.", notification_type="bill", is_read=False)
