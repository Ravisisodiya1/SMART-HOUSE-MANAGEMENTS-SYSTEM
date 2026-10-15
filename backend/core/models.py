from decimal import Decimal
import os
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

def validate_upload(f):
    if os.path.splitext(f.name)[1].lower() not in (".pdf",".png",".jpg",".jpeg",".doc",".docx"):
        raise ValidationError("Unsupported file type. Allowed: pdf, png, jpg, doc, docx.")
    if f.size > 5 * 1024 * 1024:
        raise ValidationError("File too large (max 5 MB).")

class User(AbstractUser):
    ROLES = [("owner","House Owner"),("member","Family Member"),("admin","Admin")]
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLES, default="owner")
    updated_at = models.DateTimeField(auto_now=True)

class House(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="houses")
    house_name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    house_type = models.CharField(max_length=20, default="Apartment")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.house_name

class Scoped(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: abstract = True

def amt(): return models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])

class FamilyMember(Scoped):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, default="Other")
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, default="member")
    status = models.CharField(max_length=20, default="active")

class Expense(Scoped):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=30, default="Other")
    amount = amt()
    date = models.DateField()
    payment_method = models.CharField(max_length=20, default="Cash")
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True, validators=[validate_upload])
    class Meta: indexes = [models.Index(fields=["house","date"])]

class Income(Scoped):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    source = models.CharField(max_length=60, default="Salary")
    amount = amt()
    date = models.DateField()
    description = models.TextField(blank=True)

class Budget(Scoped):
    category = models.CharField(max_length=30)
    monthly_limit = amt()
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    class Meta: unique_together = ("house","category","month","year")

class Bill(Scoped):
    bill_type = models.CharField(max_length=30, default="Electricity")
    provider = models.CharField(max_length=100, blank=True)
    amount = amt()
    due_date = models.DateField()
    status = models.CharField(max_length=10, default="unpaid")
    recurring = models.BooleanField(default=False)
    reminder_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

class Task(Scoped):
    assigned_to = models.ForeignKey(FamilyMember, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, default="Medium")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, default="Pending")
    category = models.CharField(max_length=40, blank=True)

class ShoppingItem(Scoped):
    added_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    item_name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=1)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=30, default="Grocery")
    priority = models.CharField(max_length=10, default="Medium")
    status = models.CharField(max_length=12, default="pending")

class Maintenance(Scoped):
    category = models.CharField(max_length=30, default="Other")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    service_provider = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scheduled_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, default="Scheduled")
    warranty_date = models.DateField(null=True, blank=True)

class Asset(Scoped):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, default="Electronics")
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_expiry = models.DateField(null=True, blank=True)
    serial_number = models.CharField(max_length=80, blank=True)
    condition = models.CharField(max_length=20, default="Good")
    notes = models.TextField(blank=True)

class Document(Scoped):
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=40, default="Other")
    file = models.FileField(upload_to="documents/", validators=[validate_upload])
    expiry_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, default="info")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
