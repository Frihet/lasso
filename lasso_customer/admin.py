# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms


admin.site.register(UnitWorkType)

class UnitWorkPricesInline(admin.TabularInline):
    model = UnitWorkPrices

class ContactInline(admin.TabularInline):
    model = Contact
    fk_name = "for_organization"
    fields = ("first_name", "last_name", "email", "phone", "fax", "address")

class CustomerAdmin(admin.ModelAdmin):
    inlines = [UnitWorkPricesInline, ContactInline]
    exclude = ('username', 'first_name', 'last_name', 'is_superuser','user_permissions', 'last_login', 'date_joined', 'is_staff')
    search_fields = ('name',)

admin.site.register(Customer, CustomerAdmin)

class TransporterAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    exclude = ('username', 'first_name', 'last_name', 'is_superuser','user_permissions', 'last_login', 'date_joined', 'is_staff')
    search_fields = ('name',)

admin.site.register(Transporter, TransporterAdmin)
