from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from .models import *

class Base(APITestCase):
    def make(self, email):
        r = self.client.post("/api/auth/register/", {"email": email, "password": "Str0ng!Pass99", "first_name": "T"}, format="json")
        self.assertEqual(r.status_code, 201); self.client.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        self.assertEqual(self.client.post("/api/house/", {"house_name": "H"}, format="json").status_code, 201)

class Tests(Base):
    def test_auth(self):
        self.make("a@x.com"); self.client.credentials()
        self.assertEqual(self.client.get("/api/expenses/").status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login/", {"username": "a@x.com", "password": "bad"}).status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login/", {"username": "a@x.com", "password": "Str0ng!Pass99"}).status_code, 200)
        self.assertEqual(self.client.post("/api/auth/register/", {"email": "a@x.com", "password": "Str0ng!Pass99"}).status_code, 400)
    def test_crud_and_isolation(self):
        self.make("a@x.com"); d = {"title": "Milk", "category": "Food", "amount": "50.00", "date": "2026-09-01"}
        r = self.client.post("/api/expenses/", d, format="json"); self.assertEqual(r.status_code, 201)
        pk = r.data["id"]; self.assertEqual(self.client.patch(f"/api/expenses/{pk}/", {"amount": "60"}, format="json").status_code, 200)
        self.assertEqual(self.client.post("/api/expenses/", {**d, "amount": "-5"}, format="json").status_code, 400)
        self.make("b@x.com")
        self.assertEqual(self.client.get(f"/api/expenses/{pk}/").status_code, 404)
        self.assertEqual(self.client.get("/api/expenses/").data["count"], 0)
    def test_budget_and_dashboard(self):
        self.make("a@x.com"); t = date.today()
        self.client.post("/api/expenses/", {"title": "x", "category": "Food", "amount": "6500", "date": str(t)}, format="json")
        r = self.client.post("/api/budgets/", {"category": "Food", "monthly_limit": "8000", "month": t.month, "year": t.year}, format="json")
        self.assertEqual(float(r.data["remaining"]), 1500.0)
        d = self.client.get("/api/dashboard/").data; self.assertEqual(float(d["month_expense"]), 6500.0)
        self.assertIn("reply", self.client.post("/api/ai/chat/", {"message": "How much did I spend?"}, format="json").data)
    def test_bill_task_family(self):
        self.make("a@x.com")
        for url, d in [("bills", {"bill_type": "Water", "amount": "100", "due_date": "2026-10-05"}), ("tasks", {"title": "T"}), ("family", {"name": "Asha"})]:
            r = self.client.post(f"/api/{url}/", d, format="json"); self.assertEqual(r.status_code, 201, r.data)
            self.assertEqual(self.client.delete(f"/api/{url}/{r.data['id']}/").status_code, 204)
    def test_file_validation(self):
        self.make("a@x.com")
        bad = SimpleUploadedFile("x.exe", b"abc"); r = self.client.post("/api/documents/", {"title": "d", "file": bad}, format="multipart")
        self.assertEqual(r.status_code, 400)
        ok = SimpleUploadedFile("x.pdf", b"%PDF-1.4"); r = self.client.post("/api/documents/", {"title": "d", "file": ok}, format="multipart")
        self.assertEqual(r.status_code, 201)
