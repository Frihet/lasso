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
from django.db.models import Q
import utils
import django.forms.util
import decimal

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

class EntryUnitWorkInline(admin.TabularInline):
    model = UnitWork
    exclude = ('price_per_unit', 'date', 'withdrawal')

class EntryAdminForm(forms.ModelForm):
    class Meta:
        model = Entry

    def __init__(self, *args, **kwargs):
        super(EntryAdminForm, self).__init__(*args,**kwargs)
        self.fields['customer'].widget.attrs['class'] = 'autosubmit'
        self.fields['original_seller'].widget.attrs['class'] = 'autosubmit'

class EntryAdmin(IntermediateFormHandlingAdminMixin, ExtendablePermissionAdminMixin, admin.ModelAdmin):
    form = EntryAdminForm
    inlines = [EntryUnitWorkInline,EntryRowInline]
    date_hierarchy = 'arrival_date'
    exclude = ('insurance_percentage', 'price_per_kilo_per_entry','price_per_unit_per_entry','price_min_per_entry',)
    list_display_links = list_display = ('id', 'customer', 'arrival_date', 'product_description', 'nett_weight', 'gross_weight', 'product_value', 'nett_weight_left', 'gross_weight_left', 'product_value_left')
    search_fields = ('customer__name', 'arrival_date', 'rows__product_description')
    group_owner_field = "customer"

    def cross_verify_forms(self, adminform, inlines_forms):
        if adminform.form['customer'].data or adminform.form.initial.get('customer', None) is not None:
            customer = Customer.objects.get(id=adminform.form['customer'].data or adminform.form.initial['customer'])

            for unit_work_row in inlines_forms[self.inlines.index(EntryUnitWorkInline)].formset.forms:
                unit_work_row['work_type'].field.queryset = unit_work_row['work_type'].field.queryset.filter(customer = customer)

            if not hasattr(adminform.form['price'].field, 'orig_queryset'):
                adminform.form['price'].field.orig_queryset = adminform.form['price'].field.queryset
            adminform.form['price'].field.queryset = adminform.form['price'].field.orig_queryset.filter(customer = customer) 
            if adminform.form.data.get('price', '') == '' or adminform.form['price'].field.queryset.filter(id=adminform.form.data['price']).count() == 0:
                defaults = adminform.form['price'].field.queryset.filter(is_default=True)
                if len(defaults) > 0:
                    adminform.form.data['price'] = defaults[0].id

        # if adminform.form['original_seller'].data:
        #     original_seller = OriginalSeller.objects.get(id=adminform.form['original_seller'].data)

        #     for entry_row in inlines_forms[self.inlines.index(EntryRowInline)].formset.forms:
        #         if not entry_row.data[entry_row['origin'].html_name]:
        #             entry_row.data[entry_row['origin'].html_name] = original_seller.origin.id

admin.site.register(Entry, EntryAdmin)

class WithdrawalRowAdminForm(forms.ModelForm):
    nett_weight = forms.DecimalField(label="Nett weight", required=False)
    gross_weight = forms.DecimalField(label="Gross weight", required=False)

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

    def clean_units(self):
        old = getattr(self.instance, "old_units", 0) or 0
        if self.cleaned_data.get("entry_row", None) is not None and self.cleaned_data['units'] is not None and self.cleaned_data["entry_row"].units_left + old - self.cleaned_data['units'] < 0:
            raise ValidationError(_("Not enough units left"))
        return self.cleaned_data["units"]

    def clean_nett_weight(self):
        old = decimal.Decimal(str(getattr(self.instance, "old_nett_weight", 0) or 0))
        if self.cleaned_data.get("entry_row", None) is not None and self.cleaned_data['nett_weight'] is not None and not self.cleaned_data["entry_row"].auto_weight and self.cleaned_data["entry_row"].nett_weight_left + old - decimal.Decimal(str(self.cleaned_data['nett_weight'])) < 0:
            raise ValidationError(_("Not enough nett weight left"))
        return self.cleaned_data["nett_weight"]

    def clean_gross_weight(self):
        old = decimal.Decimal(str(getattr(self.instance, "old_gross_weight", 0) or 0))
        if self.cleaned_data.get("entry_row", None) is not None and self.cleaned_data['gross_weight'] is not None and not self.cleaned_data["entry_row"].auto_weight and self.cleaned_data["entry_row"].gross_weight_left + old - decimal.Decimal(str(self.cleaned_data['gross_weight'])) < 0:
            raise ValidationError(_("Not enough gross weight left"))
        return self.cleaned_data["gross_weight"]


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
        if adminform.form['customer'].data or adminform.form.initial.get('customer', None) is not None:
            customer = Customer.objects.get(id=adminform.form['customer'].data or adminform.form.initial['customer'])

            for unit_work_row in inlines_forms[self.inlines.index(WithdrawalUnitWorkInline)].formset.forms:
                unit_work_row['work_type'].field.queryset = unit_work_row['work_type'].field.queryset.filter(customer = customer)

            for withdrawal_row in inlines_forms[self.inlines.index(WithdrawalRowInline)].formset.forms:
                field = withdrawal_row['entry_row'].field
                if not hasattr(field, 'orig_queryset'):
                    field.orig_queryset = field.queryset
                
                field.queryset = field.orig_queryset.filter(entry__customer = customer)
                if withdrawal_row.instance.id is None:
                    field.queryset = field.queryset.filter(units_left__gt = 0)
                else:
                    field.queryset = field.queryset.filter(Q(units_left__gt = 0) | Q(id = withdrawal_row.instance.entry_row.id))

                field.queryset = field.queryset.order_by("-entry__id", "-id")

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
