# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from lasso.lasso_warehandling.models import *
from lasso.lasso_warehouse.models import *
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms
from extendable_permissions import *
import utils
import django.forms.util

class EntryRowAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=PalletSpace.objects.all(),
        required=False,
        label=_("Locations"))
    withdrawal_links = utils.ModelLinkField(queryset=Withdrawal.objects.all(), required=False, label=_("Withdrawal links"))

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
    fieldsets = [(_('Product'), {'fields': ('use_before',
                                            'product_nr',
                                            'product_description',
                                            'origin')
                                 }),
                 (_('Amount'), {'fields': ('auto_weight',
                                           'uom',
                                           'units',
                                           'nett_weight',
                                           'gross_weight',
                                           'product_value')
                                }),
                 (_('Current status'), {'fields': ('withdrawal_links',
                                                   )}),
                 (_('Arrival'), {'fields': ('arrival_temperatures',
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
    group_owner_field = "customer"

admin.site.register(Entry, EntryAdmin)

class WithdrawalRowAdminForm(forms.ModelForm):
    nett_weight = forms.FloatField(label="Nett weight", required=False)
    gross_weight = forms.FloatField(label="Gross weight", required=False)

    class Meta:
        model = WithdrawalRow

    def __init__(self, *args, **kwargs):
        super(WithdrawalRowAdminForm, self).__init__(*args,**kwargs)
        if self.instance.pk is not None:
            self.initial['nett_weight'] = self.instance.nett_weight
            self.initial['gross_weight'] = self.instance.gross_weight

    def save(self, commit=True):
        self.instance.nett_weight = self.cleaned_data['nett_weight']
        self.instance.gross_weight = self.cleaned_data['gross_weight']
        return super(WithdrawalRowAdminForm, self).save(commit)

    save.alters_data = True

class WithdrawalUnitWorkInline(admin.TabularInline):
    model = UnitWork
    exclude = ('price_per_unit', 'date', 'entry')

class WithdrawalRowInline(admin.TabularInline):
    form = WithdrawalRowAdminForm
    model = WithdrawalRow
    fields = ('entry_row', 'units', 'nett_weight', 'gross_weight')

class WithdrawalAdminForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
    reference_nr = utils.ReadonlyCharField()
    def __init__(self, *args, **kwargs):
        super(WithdrawalAdminForm, self).__init__(*args,**kwargs)
        if self.instance is not None:
            self.initial['reference_nr'] = self.instance.reference_nr
        if self.instance and not self.instance.id:
            vts = VehicleType.objects.filter(is_default=True)
            if len(vts) > 0:
                self.initial['vehicle_type'] = vts[0]
        self.fields['customer'].widget.attrs['class'] = 'autosubmit'

class WithdrawalAdmin(IntermediateFormHandlingAdminMixin, ExtendablePermissionAdminMixin, admin.ModelAdmin):
    form = WithdrawalAdminForm
    inlines = [WithdrawalUnitWorkInline, WithdrawalRowInline,]
    date_hierarchy = 'withdrawal_date'

    fieldsets = [(_('Arrival'), {'fields': ('destination',
                                             'opening_hours',
                                             'arrival_date',
                                             'comment')
                                  }),
                 (_('General'), {'fields': ('customer',
                                            'transport_nr',
                                            'order_nr',
                                            'reference_nr')
                                 }),
                 (_('Departure'), {'fields': ('responsible',
                                              'place_of_departure',
                                              'withdrawal_date')
                                   }),
                 (_('Transport'), {'fields': ('transport_condition',
                                              'vehicle_type',
                                              'transporter')
                                   })]

    list_display_links = list_display = ('id', 'customer', 'withdrawal_date', 'product_description', 'nett_weight', 'gross_weight')
    search_fields = ('customer__name', 'withdrawal_date', 'rows__entry_row__product_description')
    group_owner_field = "customer"

    def cross_verify_forms(self, adminform, inlines_forms):
        if adminform.form['customer'].data is not None:
            customer = Customer.objects.get(id=adminform.form['customer'].data)

            for unit_work_row in inlines_forms[self.inlines.index(WithdrawalUnitWorkInline)].formset.forms:
                unit_work_row['work_type'].field.queryset = unit_work_row['work_type'].field.queryset.filter(customer = customer)

            for withdrawal_row in inlines_forms[self.inlines.index(WithdrawalRowInline)].formset.forms:
                withdrawal_row['entry_row'].field.queryset = withdrawal_row['entry_row'].field.queryset.filter(entry__customer = customer)



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
    exclude = ('price_per_unit', 'entry', 'withdrawal')
    group_owner_field = "work_type__customer"

admin.site.register(UnitWork, UnitWorkAdmin)
