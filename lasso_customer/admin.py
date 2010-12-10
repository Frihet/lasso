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
    fk_name = "organization"
    fields = ("first_name", "last_name", "email", "phone", "fax", "address")

class CustomerAdmin(admin.ModelAdmin):
    inlines = [UnitWorkPricesInline, ContactInline]
    search_fields = ('name',)
admin.site.register(Customer, CustomerAdmin)

class OriginalSellerAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('name',)
admin.site.register(OriginalSeller, OriginalSellerAdmin)

class DestinationAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('name',)
admin.site.register(Destination, DestinationAdmin)

class TransporterAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('name',)

admin.site.register(Transporter, TransporterAdmin)
