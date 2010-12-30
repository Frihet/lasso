# -*- coding: utf-8 -*-
from lasso.lasso_warehandling.models import *
from lasso.lasso_warehouse.models import *
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms
from extendable_permissions import *
import utils

class EntryRowAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=PalletSpace.objects.all(),
        required=False)
    withdrawal_links = utils.ModelLinkField(queryset=Withdrawal.objects.all(), required=False)

    class Meta:
        model = EntryRow

    def __init__(self, *args, **kwargs):
        super(EntryRowAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['locations'] = [values[0] for values in self.instance.locations.values_list('pk')]
            self.initial['withdrawal_links'] = [row.withdrawal for row in self.instance.withdrawal_rows.all()]

    def save(self, commit=True):
        instance = super(EntryRowAdminForm, self).save(commit)

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


class EntryRowInline(admin.StackedInline):
    form = EntryRowAdminForm
    model = EntryRow
    fieldsets = [('Product', {'fields': ('use_before',
                                         'product_nr',
                                         'product_description')
                              }),
                 ('Amount', {'fields': ('auto_weight',
                                        'uom',
                                        'units',
                                        'nett_weight',
                                        'gross_weight',
                                        'product_value')
                             }),
                 ('Current status', {'fields': ('withdrawal_links',
                                                )}),
                 ('Arrival', {'fields': ('arrival_temperatures',
                                         'product_state',
                                         'comment',
                                         'locations',
                                         'customs_certificate_nr')
                              }),
                 ]

class EntryAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    inlines = [EntryRowInline,]
    date_hierarchy = 'arrival_date'
    exclude = ('insurance_percentage', 'price_per_kilo_per_entry','price_per_unit_per_entry',)
    list_display_links = list_display = ('id', 'customer', 'arrival_date', 'product_description', 'nett_weight', 'gross_weight', 'product_value', 'nett_weight_left', 'gross_weight_left', 'product_value_left')
    search_fields = ('customer__name', 'arrival_date', 'rows__product_description')
    owner_field = "customer"

admin.site.register(Entry, EntryAdmin)

admin.site.register(TransportCondition)

class WithdrawalRowAdminForm(forms.ModelForm):
    nett_weight = forms.FloatField(label="Nett weight")
    gross_weight = forms.FloatField(label="Gross weight")

    class Meta:
        model = WithdrawalRow

    def __init__(self, *args, **kwargs):
        super(WithdrawalRowAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['nett_weight'] = self.instance.nett_weight
            self.initial['gross_weight'] = self.instance.gross_weight

    def save(self, commit=True):
        if not self.instance.entry_row.auto_weight:
            self.instance.nett_weight = self.cleaned_data['nett_weight']
            self.instance.gross_weight = self.cleaned_data['gross_weight']
        return super(WithdrawalRowAdminForm, self).save(commit)

    save.alters_data = True

class WithdrawalRowInline(admin.TabularInline):
    form = WithdrawalRowAdminForm
    model = WithdrawalRow
    fields = ('entry_row', 'units', 'nett_weight', 'gross_weight')

class WithdrawalAdminForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
    reference_nr = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(WithdrawalAdminForm, self).__init__(*args,**kwargs)
        if self.instance is not None:
            self.initial['reference_nr'] = self.instance.reference_nr

class WithdrawalAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    form = WithdrawalAdminForm
    inlines = [WithdrawalRowInline,]
    date_hierarchy = 'withdrawal_date'

    fieldsets = [('Arrival', {'fields': ('destination',
                                             'opening_hours',
                                             'arrival_date',
                                             'comment')
                                  }),
                 ('General', {'fields': ('customer',
                                         'transport_nr',
                                         'order_nr',
                                         'reference_nr')
                              }),
                 ('Departure', {'fields': ('responsible',
                                           'place_of_departure',
                                           'withdrawal_date')
                                }),
                 ('Transport', {'fields': ('transport_condition',
                                           'vehicle_type',
                                           'transporter')
                                })]

    list_display_links = list_display = ('id', 'customer', 'withdrawal_date', 'product_description', 'nett_weight', 'gross_weight')
    search_fields = ('customer__name', 'withdrawal_date', 'rows__entry_row__product_description')
    owner_field = "customer"

    def set_defaults(self, request, initial):
        if 'responsible' not in initial:
            initial['responsible'] = request.user.pk

    def get_form(self, request, *arg, **kw):
        Form = super(WithdrawalAdmin, self).get_form(request, *arg, **kw)
        def model_form(*arg, **kw):
            form = Form(*arg, **kw)
            self.set_defaults(request, form.initial)
            return form
        return model_form

admin.site.register(Withdrawal, WithdrawalAdmin)


class UnitWorkAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    exclude = ('price_per_unit',)
    owner_field = "work_type__customer"

admin.site.register(UnitWork, UnitWorkAdmin)
