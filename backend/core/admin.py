from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models as m
admin.site.register(m.User, UserAdmin)
for cls in (m.House,m.FamilyMember,m.Expense,m.Income,m.Budget,m.Bill,m.Task,m.ShoppingItem,m.Maintenance,m.Asset,m.Document,m.Notification):
    admin.site.register(cls)
