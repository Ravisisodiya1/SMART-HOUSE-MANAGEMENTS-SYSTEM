from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views as v
from .models import *
from .serializers import BUDGET_EXTRA

r = DefaultRouter()
for name, model, search, uf, extra in [
  ("expenses", Expense, ("title","category","description"), "user", None), ("income", Income, ("source","description"), "user", None),
  ("budgets", Budget, ("category",), None, BUDGET_EXTRA), ("bills", Bill, ("bill_type","provider"), None, None),
  ("tasks", Task, ("title","category"), None, None), ("shopping", ShoppingItem, ("item_name","category"), "added_by", None),
  ("maintenance", Maintenance, ("title","category","service_provider"), None, None), ("assets", Asset, ("name","category","serial_number"), None, None),
  ("documents", Document, ("title","category"), "uploaded_by", None), ("family", FamilyMember, ("name","relationship"), None, None)]:
    r.register(name, v.make_viewset(model, search, uf, extra), basename=name)
r.register("notifications", v.Notifications, basename="notifications")

urlpatterns = [
  path("auth/register/", v.Register.as_view()), path("auth/login/", TokenObtainPairView.as_view()),
  path("auth/refresh/", TokenRefreshView.as_view()), path("auth/logout/", v.Logout.as_view()),
  path("auth/profile/", v.Profile.as_view()), path("auth/change-password/", v.ChangePassword.as_view()),
  path("house/", v.HouseView.as_view()), path("dashboard/", v.DashboardView.as_view()),
  path("ai/insights/", v.Insights.as_view()), path("ai/chat/", v.Chat.as_view()), path("reports/", v.Report.as_view()),
  path("", include(r.urls)),
]
