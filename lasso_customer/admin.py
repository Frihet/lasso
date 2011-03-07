# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from extendable_permissions import *
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


class ContactInline(ExtendablePermissionAdminMixin, admin.TabularInline):
    form = ContactAdminForm
    model = Contact
    fk_name = "organization"
    fields = ("first_name", "last_name", "title", "email", "phone", "fax", "address", "username", "password", "is_active")
    access_controlled_fields = {'username': ['change_access'],
                                'password': ['change_access'],
                                'is_active': ['change_access']}

class OrganizationAdminForm(forms.ModelForm):
    copy_from = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        label=_("Copy from"),
        widget = forms.ModelChoiceField.widget(attrs = {'class': 'autosubmit'}))

class OrganizationAdmin(IntermediateFormHandlingAdminMixin, admin.ModelAdmin):
    inlines = [ContactInline]
    search_fields = ('title',)
    fields = ('copy_from', 'title', 'address', 'phone', 'fax')

    def cross_verify_forms(self, adminform, inlines_forms):
        if adminform.form['copy_from'].data is not None:
            org = Organization.objects.get(id=adminform.form['copy_from'].data)
            for attr in ["title", "address", "phone", "fax"]:
                adminform.form.data[attr] = getattr(org, attr)
            adminform.form.data['copy_from'] = None


class CustomerAdminForm(OrganizationAdminForm):
    class Meta:
        model = Customer
class CustomerAdmin(OrganizationAdmin):
    form = CustomerAdminForm
    inlines = [UnitWorkPricesInline] + OrganizationAdmin.inlines
    fields = OrganizationAdmin.fields + ('customer_nr',
                                         
                                         'price_per_kilo_per_day',
                                         'price_per_kilo_per_entry',
                                         'price_per_kilo_per_withdrawal',
                                         
                                         'price_per_unit_per_day',
                                         'price_per_unit_per_entry',
                                         'price_per_unit_per_withdrawal',
                                         
                                         'price_min_per_day',
                                         'price_min_per_entry',
                                         'price_min_per_withdrawal')
admin.site.register(Customer, CustomerAdmin)

class OriginalSellerAdminForm(OrganizationAdminForm):
    class Meta:
        model = OriginalSeller
class OriginalSellerAdmin(OrganizationAdmin):
    form = OriginalSellerAdminForm
admin.site.register(OriginalSeller, OriginalSellerAdmin)

class DestinationAdminForm(OrganizationAdminForm):
    class Meta:
        model = Destination
class DestinationAdmin(OrganizationAdmin):
    form = DestinationAdminForm
admin.site.register(Destination, DestinationAdmin)

class TransporterAdminForm(OrganizationAdminForm):
    class Meta:
        model = Transporter
class TransporterAdmin(OrganizationAdmin):
    form = TransporterAdminForm

admin.site.register(Transporter, TransporterAdmin)
