# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms

admin.site.register(UnitWorkType)

class UnitWorkPricesInline(admin.TabularInline):
    model = UnitWorkPrices


class ContactAdminForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput)

    class Meta:
        model = Contact

    def __init__(self, *args, **kwargs):
        super(ContactAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['password'] = self.instance.password

    def save(self, commit=True):
        self.instance.password = self.cleaned_data['password']
        return super(ContactAdminForm, self).save(commit)

    save.alters_data = True

    def __init__(self, *arg, **kw):
        super(ContactAdminForm, self).__init__(*arg, **kw)
        self.fields['username'].required = False


class ContactInline(admin.TabularInline):
    form = ContactAdminForm
    model = Contact
    fk_name = "organization"
    fields = ("first_name", "last_name", "title", "email", "phone", "fax", "address", "username", "password", "is_active")

class CustomerAdmin(admin.ModelAdmin):
    inlines = [UnitWorkPricesInline, ContactInline]
    search_fields = ('title',)
    exclude = ("name",)
admin.site.register(Customer, CustomerAdmin)

class OriginalSellerAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('title',)
    exclude = ("name",)
admin.site.register(OriginalSeller, OriginalSellerAdmin)

class DestinationAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('title',)
    exclude = ("name",)
admin.site.register(Destination, DestinationAdmin)

class TransporterAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('title',)
    exclude = ("name",)

admin.site.register(Transporter, TransporterAdmin)
