# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms


admin.site.register(UnitWorkType)

class UnitWorkPricesInline(admin.TabularInline):
    model = UnitWorkPrices

class CustomerAdmin(admin.ModelAdmin):
    inlines = [UnitWorkPricesInline,]
    exclude = ('username', 'first_name', 'last_name', 'is_superuser','user_permissions', 'last_login', 'date_joined', 'is_staff')

admin.site.register(Customer, CustomerAdmin)
