# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin

class Entry(models.Model):
    customer = models.ForeignKey(Customer)
    arrival_date = models.DateField()
    def __unicode__(self):
        return u"%s @ %s for %s" % (self.id, self.arrival_date, self.customer)

class EntryRow(models.Model):
    entry = models.ForeignKey(Entry)
    product_description = models.CharField(max_length=400)
    price_per_kilo_entry = models.FloatField()
    arrival_temperature = models.FloatField()
    use_before = models.DateField()
    nett_weight = models.FloatField()
    gross_weight = models.FloatField()
    uom = models.CharField(max_length=200)
    units = models.IntegerField()
    units_left = models.IntegerField()

    @property
    def id_str(self):
        return "%s.%s" % (self.entry.id, self.id)

    def __unicode__(self):
        return u"%s: %s (%s %s à %skg @ %s for %s)" % (self.id_str, self.product_description, self.units, self.uom, self.nett_weight, self.entry.arrival_date, self.entry.customer)

class EntryRowInline(admin.TabularInline):
    model = EntryRow

class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryRowInline,]
    date_hierarchy = 'arrival_date'

admin.site.register(Entry, EntryAdmin)



class Withdrawal(models.Model):
    price_per_kilo_out = models.FloatField()
    withdrawal_date = models.DateField()
    arrival_date = models.DateField()

    def __unicode__(self):
        return u"%s @ %s" % (self.id, self.withdrawal_date)

class WithdrawalRow(models.Model):
    withdrawal = models.ForeignKey(Withdrawal)
    entry_row = models.ForeignKey(EntryRow)
    units = models.IntegerField()

    @property
    def id_str(self):
        return "%s.%s" % (self.withdrawal.id, self.id)

    def __unicode__(self):
        return u"%s (%s @ %s from %s)" % (self.id_str, self.units, self.withdrawal.withdrawal_date, self.entry_row)

class WithdrawalRowInline(admin.TabularInline):
    model = WithdrawalRow

class WithdrawalAdmin(admin.ModelAdmin):
    inlines = [WithdrawalRowInline,]
    date_hierarchy = 'withdrawal_date'

admin.site.register(Withdrawal, WithdrawalAdmin)


class UnitWork(models.Model):
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    date = models.DateField()
    units = models.IntegerField()

    def __unicode__(self):
        return u"%s of %s @ %s for %s" % (self.work_type, self.units, self.date, self.customer)

class UnitWorkAdmin(admin.ModelAdmin):
        date_hierarchy = 'date'

admin.site.register(UnitWork, UnitWorkAdmin)
