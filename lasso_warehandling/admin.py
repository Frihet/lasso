# -*- coding: utf-8 -*-
from lasso.lasso_warehandling.models import *
from lasso.lasso_warehouse.models import *
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms
from extendable_permissions import *

class EntryRowAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=PalletSpace.objects.all(),
        required=False)
    class Meta:
        model = EntryRow

    def __init__(self, *args, **kwargs):
        super(EntryRowAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['locations'] = [values[0] for values in self.instance.locations.values_list('pk')]

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
                                         'product_description',
                                         'origin')
                              }),
                 ('Arrival', {'fields': ('arrival_temperature',
                                         'product_state',
                                         'comment',
                                         'locations')
                              }),
                 ('Customs', {'fields': ('custom_handling_date',
                                         'customs_receipt_nr',
                                         'customs_testimony_nr')
                              }),
                 ('Amount', {'fields': ('uom',
                                        'units',
                                        'nett_weight',
                                        'gross_weight',
                                        'product_value')
                             })]

class EntryAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    inlines = [EntryRowInline,]
    date_hierarchy = 'arrival_date'
    exclude = ('price_per_kilo_per_entry','price_per_unit_per_entry',)
    list_display_links = list_display = ('id', 'customer', 'arrival_date', 'product_description', 'nett_weight', 'gross_weight', 'product_value', 'nett_weight_left', 'gross_weight_left', 'product_value_left')
    search_fields = ('customer__name', 'arrival_date', 'rows__product_description')
    owner_field = "customer"

admin.site.register(Entry, EntryAdmin)


class WithdrawalRowInline(admin.TabularInline):
    model = WithdrawalRow
    exclude = ('old_units',)

class WithdrawalAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    inlines = [WithdrawalRowInline,]
    date_hierarchy = 'withdrawal_date'

    fieldsets = [('Destination', {'fields': ('destination_address',
                                             'opening_hours',
                                             'arrival_date',
                                             'comment')
                                  }),
                 ('General', {'fields': ('customer',
                                         'reference_nr',
                                         'transport_nr',
                                         'order_nr')
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

admin.site.register(Withdrawal, WithdrawalAdmin)


class UnitWorkAdmin(ExtendablePermissionAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    exclude = ('price_per_unit',)
    owner_field = "work_type__customer"

admin.site.register(UnitWork, UnitWorkAdmin)
