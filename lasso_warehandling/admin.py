# -*- coding: utf-8 -*-
from lasso.lasso_warehandling.models import *
from lasso.lasso_warehouse.models import *
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms
from extendable_permissions import *

class EntryRowInline(admin.StackedInline):
    model = EntryRow

class EntryAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=PalletSpace.objects.all(),
        required=False)
    class Meta:
        model = Entry

    def __init__(self, *args, **kwargs):
        super(EntryAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['locations'] = [values[0] for values in self.instance.locations.values_list('pk')]

    def save(self, commit=True):
        instance = super(EntryAdminForm, self).save(commit)

        def save_m2m():
            instance.locations = self.cleaned_data['locations']

        if commit:
            save_m2m()
        elif hasattr(self, 'save_m2m'):
            save_old_m2m = self.save_m2m

            def save_both():
                save_old_m2m()
                save_m2m()

            self.save_m2m = save_both
        else:
            self.save_m2m = save_m2m

        return instance

    save.alters_data = True

class EntryAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    inlines = [EntryRowInline,]
    date_hierarchy = 'arrival_date'
    exclude = ('price_per_kilo_per_entry',)
    form = EntryAdminForm
    list_display_links = list_display = ('id', 'customer', 'arrival_date', 'product_description', 'nett_weight', 'gross_weight', 'product_value', 'nett_weight_left', 'gross_weight_left', 'product_value_left')
    owner_field = "customer"

admin.site.register(Entry, EntryAdmin)


class WithdrawalRowInline(admin.TabularInline):
    model = WithdrawalRow
    exclude = ('old_units',)

class WithdrawalAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    inlines = [WithdrawalRowInline,]
    date_hierarchy = 'withdrawal_date'
    exclude = ('price_per_kilo_per_withdrawal',)
    list_display_links = list_display = ('id', 'customer', 'withdrawal_date', 'product_description', 'nett_weight', 'gross_weight')

admin.site.register(Withdrawal, WithdrawalAdmin)


class UnitWorkAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    exclude = ('price_per_unit',)

admin.site.register(UnitWork, UnitWorkAdmin)
