import csv
from django.http import HttpResponse
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from django.contrib.auth import password_validation
from .services import *

def make_viewset(model, search=(), user_field=None, extra_ser=None):
    ser = make_serializer(model, extra_ser)
    class VS(viewsets.ModelViewSet):
        serializer_class = ser
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        search_fields = list(search); ordering_fields = "__all__"; ordering = ["-id"]
        def get_queryset(self):
            h = get_house(self.request.user); qs = model.objects.filter(house=h) if h else model.objects.none()
            for k, v in self.request.query_params.items():   # simple exact-match filters, e.g. ?category=Food&status=paid
                if k in [f.name for f in model._meta.fields] and k not in ("house", "receipt", "file"): qs = qs.filter(**{k: v})
            for k in ("date_from", "date_to"):
                if k in self.request.query_params and any(f.name == "date" for f in model._meta.fields):
                    qs = qs.filter(**{"date__gte" if k == "date_from" else "date__lte": self.request.query_params[k]})
            return qs
        def perform_create(self, s):
            h = get_house(self.request.user)
            if not h: raise ValidationError({"detail": "Create your house profile first."})
            kw = {"house": h}
            if user_field: kw[user_field] = self.request.user
            s.save(**kw)
    VS.__name__ = model.__name__ + "ViewSet"
    return VS

class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, r):
        s = RegisterSerializer(data=r.data); s.is_valid(raise_exception=True); u = s.save()
        t = RefreshToken.for_user(u)
        return Response({"user": UserSerializer(u).data, "access": str(t.access_token), "refresh": str(t)}, status=201)

class Logout(APIView):
    def post(self, r):
        try: RefreshToken(r.data.get("refresh")).blacklist()
        except Exception: pass
        return Response(status=204)

class Profile(APIView):
    def get(self, r): return Response(UserSerializer(r.user).data)
    def patch(self, r):
        s = UserSerializer(r.user, data=r.data, partial=True); s.is_valid(raise_exception=True); s.save(); return Response(s.data)

class ChangePassword(APIView):
    def post(self, r):
        if not r.user.check_password(r.data.get("old_password", "")): raise ValidationError({"detail": "Current password is incorrect."})
        try: password_validation.validate_password(r.data.get("new_password", ""), r.user)
        except Exception as e: raise ValidationError({"detail": list(e.messages)})
        r.user.set_password(r.data["new_password"]); r.user.save(); return Response({"detail": "Password changed."})

class HouseView(APIView):
    def get(self, r):
        h = get_house(r.user)
        return Response(make_house(h) if h else None)
    def post(self, r):
        if get_house(r.user): raise ValidationError({"detail": "House already exists."})
        h = House.objects.create(owner=r.user, **{k: r.data.get(k, "") for k in ("house_name","address","city","state","pincode")}, house_type=r.data.get("house_type", "Apartment"))
        return Response(make_house(h), status=201)
    def put(self, r):
        h = get_house(r.user)
        if not h or h.owner != r.user: raise ValidationError({"detail": "Only the house owner can edit."})
        for k in ("house_name","address","city","state","pincode","house_type"):
            if k in r.data: setattr(h, k, r.data[k])
        h.save(); return Response(make_house(h))
def make_house(h): return {k: getattr(h, k) for k in ("id","house_name","address","city","state","pincode","house_type")}

class DashboardView(APIView):
    def get(self, r):
        h = get_house(r.user)
        if not h: return Response({"no_house": True})
        sync_notifications(r.user, h); return Response(dashboard(h))

class Insights(APIView):
    def get(self, r):
        h = get_house(r.user); return Response({"insights": AIService().insights(h) if h else []})

class Chat(APIView):
    def post(self, r):
        h = get_house(r.user); q = str(r.data.get("message", ""))[:500]
        if not h: return Response({"reply": "Please create your house profile first."})
        return Response({"reply": AIService().chat(h, q)})

class Report(APIView):
    """GET /api/reports/?type=expenses|income|bills&format=csv|json&date_from=&date_to="""
    def get(self, r):
        h = get_house(r.user); t = r.query_params.get("type", "expenses")
        model = {"expenses": Expense, "income": Income, "bills": Bill}.get(t)
        if not h or not model: raise ValidationError({"detail": "Invalid report type."})
        qs = model.objects.filter(house=h); df = "date" if t != "bills" else "due_date"
        if r.query_params.get("date_from"): qs = qs.filter(**{df + "__gte": r.query_params["date_from"]})
        if r.query_params.get("date_to"): qs = qs.filter(**{df + "__lte": r.query_params["date_to"]})
        fields = [f.name for f in model._meta.fields if f.name not in ("house", "receipt", "user")]
        if r.query_params.get("format") == "csv":
            resp = HttpResponse(content_type="text/csv"); resp["Content-Disposition"] = f'attachment; filename="{t}.csv"'
            w = csv.writer(resp); w.writerow(fields)
            for o in qs: w.writerow([getattr(o, f) for f in fields])
            return resp
        return Response(list(qs.values(*fields)))

class Notifications(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer; http_method_names = ["get", "patch", "delete"]
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)
