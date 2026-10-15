from django.contrib.auth import password_validation
from rest_framework import serializers
from .models import *
from .services import _sum

class UserSerializer(serializers.ModelSerializer):
    class Meta: model = User; fields = ["id","username","email","first_name","last_name","phone","profile_photo","role"]; read_only_fields = ["id","username","role"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta: model = User; fields = ["email","password","first_name","last_name","phone"]
    def validate_email(self, v):
        if User.objects.filter(email__iexact=v).exists(): raise serializers.ValidationError("An account with this email already exists.")
        return v.lower()
    def validate_password(self, v): password_validation.validate_password(v); return v
    def create(self, d):
        return User.objects.create_user(username=d["email"], **d)

def make_serializer(model, extra=None):
    meta = type("Meta", (), {"model": model, "exclude": ["house"]})
    return type(model.__name__ + "Serializer", (serializers.ModelSerializer,), {"Meta": meta, **(extra or {})})

class BudgetExtra:
    def _spent(o):
        from .models import Expense
        return _sum(Expense.objects.filter(house=o.house, category=o.category, date__month=o.month, date__year=o.year))
BUDGET_EXTRA = {
  "current_spending": serializers.SerializerMethodField(), "remaining": serializers.SerializerMethodField(),
  "get_current_spending": lambda self, o: BudgetExtra._spent(o),
  "get_remaining": lambda self, o: o.monthly_limit - BudgetExtra._spent(o),
}
class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model = Notification; exclude = ["user"]; read_only_fields = ["title","message","notification_type","created_at"]
