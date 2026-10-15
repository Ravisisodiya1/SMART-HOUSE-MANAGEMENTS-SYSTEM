from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import *

class Command(BaseCommand):
    help = "Create demo user demo@smarthouse.com / Demo@12345 with sample data"
    def handle(self, *a, **k):
        u, new = User.objects.get_or_create(username="demo@smarthouse.com", defaults=dict(email="demo@smarthouse.com", first_name="Demo", last_name="User"))
        if not new: return self.stdout.write("Demo data already exists.")
        u.set_password("Demo@12345"); u.save(); t = date.today()
        h = House.objects.create(owner=u, house_name="Sharma Residence", address="12 MG Road", city="Indore", state="MP", pincode="452001")
        me = FamilyMember.objects.create(house=h, user=u, name="Demo User", relationship="Father", role="owner")
        FamilyMember.objects.create(house=h, name="Asha", relationship="Mother"); FamilyMember.objects.create(house=h, name="Ravi", relationship="Son")
        for i, (c, a) in enumerate([("Food",6500),("Electricity",2100),("Transport",1800),("Education",4000),("Entertainment",900)]):
            Expense.objects.create(house=h, user=u, title=f"{c} spend", category=c, amount=a, date=t - timedelta(days=i*3))
            Expense.objects.create(house=h, user=u, title=f"Earlier {c}", category=c, amount=a*0.7, date=t - timedelta(days=32+i))
        Income.objects.create(house=h, user=u, source="Salary", amount=60000, date=t.replace(day=1))
        Budget.objects.create(house=h, category="Food", monthly_limit=8000, month=t.month, year=t.year)
        Bill.objects.create(house=h, bill_type="Electricity", provider="MPEB", amount=2100, due_date=t + timedelta(days=2))
        Bill.objects.create(house=h, bill_type="Internet", provider="Airtel", amount=999, due_date=t - timedelta(days=1))
        Task.objects.create(house=h, title="Clean water tank", assigned_to=me, priority="High", due_date=t + timedelta(days=3))
        ShoppingItem.objects.create(house=h, item_name="Rice 5kg", estimated_price=350, added_by=u)
        Maintenance.objects.create(house=h, category="AC", title="AC service", scheduled_date=t + timedelta(days=7))
        Asset.objects.create(house=h, name="Samsung TV", purchase_price=45000, warranty_expiry=t + timedelta(days=30))
        self.stdout.write(self.style.SUCCESS("Demo created: demo@smarthouse.com / Demo@12345"))
