# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.db.models.signals import *
from django import forms
import datetime

class Entry(models.Model):
    customer = models.ForeignKey(Customer)
    arrival_date = models.DateField()
    price_per_kilo_per_entry = models.FloatField(blank=True)

    class Meta:
        permissions = (("view_entry", "View"),
                       ("view_own_entry", "View own"))

    @property
    def nett_weight(self):
        return sum([row.nett_weight for row in self.rows.all()])

    @property
    def gross_weight(self):
        return sum([row.gross_weight for row in self.rows.all()])

    @property
    def nett_weight_left(self):
        return sum([row.nett_weight_left for row in self.rows.all()])

    @property
    def gross_weight_left(self):
        return sum([row.gross_weight_left for row in self.rows.all()])

    @property
    def product_value(self):
        return sum([row.product_value for row in self.rows.all() if row.product_value])

    @property
    def product_value_left(self):
        return sum([row.product_value_left for row in self.rows.all() if row.product_value_left])

    @property
    def product_description(self):
        return '; '.join(["%s %s %s" % (row.units, row.uom, row.product_description) for row in self.rows.all() if row.product_description])

    def __unicode__(self):
        return u"%s @ %s for %s" % (self.id, self.arrival_date, self.customer)

def entry_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_kilo_per_entry = instance.customer.price_per_kilo_per_entry
pre_save.connect(entry_pre_save, sender=Entry)

class EntryRow(models.Model):
    entry = models.ForeignKey(Entry, related_name="rows")
    custom_handling_date = models.DateField(null=True, blank=True)
    customs_receipt_nr = models.CharField(max_length=200, blank=True)
    customs_testimony_nr = models.CharField(max_length=200, blank=True)
    transporter = models.CharField(max_length=200, blank=True)
    product_nr = models.CharField(max_length=400, blank=True)
    uom = models.CharField(max_length=200, blank=True)
    units = models.IntegerField()
    units_left = models.IntegerField(blank=True)
    nett_weight = models.FloatField()
    gross_weight = models.FloatField()
    product_value = models.FloatField(null=True, blank=True)

    use_before = models.DateField(null=True, blank=True)
    product_description = models.CharField(max_length=400, blank=True)
    product_state = models.CharField(max_length=200, blank=True)
    comment = models.TextField(null=True, blank=True)
    arrival_temperature = models.FloatField(null=True, blank=True)

    origin = models.CharField(max_length=200, blank=True)

    @property
    def cost(self):
        return self.gross_weight * self.entry.price_per_kilo_per_entry

    @property
    def nett_weight_per_unit(self):
        return self.nett_weight / self.units

    @property
    def gross_weight_per_unit(self):
        return self.gross_weight / self.units

    @property
    def product_value_per_unit(self):
        if self.product_value is None: return None
        return self.product_value / self.units

    @property
    def nett_weight_left(self):
        return self.nett_weight_per_unit * self.units_left

    @property
    def gross_weight_left(self):
        return self.gross_weight_per_unit * self.units_left

    @property
    def product_value_left(self):
        if self.product_value_per_unit is None: return None
        return self.product_value_per_unit * self.units_left

    @property
    def id_str(self):
        return "%s.%s" % (self.entry.id, self.id)

    def log(self):
        if not list(StorageLog.objects.filter(entry_row = self, date = datetime.date.today())):
            return StorageLog(entry_row = self).save()
        return None

    def __unicode__(self):
        return u"%s: %s (%s %s à %skg @ %s for %s)" % (self.id_str, self.product_description, self.units, self.uom, self.nett_weight, self.entry.arrival_date, self.entry.customer)

def entry_row_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.units_left = instance.units
pre_save.connect(entry_row_pre_save, sender=EntryRow)

class Withdrawal(models.Model):
    customer = models.ForeignKey(Customer)
    price_per_kilo_per_withdrawal = models.FloatField(blank=True)

    reference_nr = models.CharField(max_length=200, blank=True)
    responsible = models.CharField(max_length=200, blank=True)
    place_of_departure = models.CharField(max_length=200, blank=True)
    
    insurance = models.CharField(max_length=200, blank=True)
    transport_condition = models.CharField(max_length=200, blank=True)
    transport_nr = models.CharField(max_length=200, blank=True)
    order_nr = models.CharField(max_length=200, blank=True)

    destination_address = models.TextField(null=True, blank=True)
    withdrawal_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=200, blank=True)
    opening_hours = models.CharField(max_length=200, blank=True)
    transporter = models.CharField(max_length=200, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        permissions = (("view_withdrawal", "View"),
                       ("view_own_withdrawal", "View own"))

    @property
    def nett_weight(self):
        return sum([row.nett_weight for row in self.rows.all()])

    @property
    def gross_weight(self):
        return sum([row.gross_weight for row in self.rows.all()])

    @property
    def product_description(self):
        return '; '.join(["%s %s %s" % (row.units, row.entry_row.uom, row.entry_row.product_description) for row in self.rows.all() if row.entry_row.product_description])

    def __unicode__(self):
        return u"%s @ %s" % (self.id, self.withdrawal_date)

def withdrawal_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_kilo_per_withdrawal = instance.customer.price_per_kilo_per_withdrawal
pre_save.connect(withdrawal_pre_save, sender=Withdrawal)

class WithdrawalRow(models.Model):
    withdrawal = models.ForeignKey(Withdrawal, related_name="rows")
    entry_row = models.ForeignKey(EntryRow, related_name="withdrawal_rows")
    old_units = models.IntegerField(blank=True)
    units = models.IntegerField()

    @property
    def cost(self):
        return self.gross_weight * self.withdrawal.price_per_kilo_per_withdrawal

    @property
    def nett_weight(self):
        return self.entry_row.nett_weight_per_unit * self.units

    @property
    def gross_weight(self):
        return self.entry_row.gross_weight_per_unit * self.units

    @property
    def id_str(self):
        return "%s.%s" % (self.withdrawal.id, self.id)

    def __unicode__(self):
        return u"%s (%s @ %s from %s)" % (self.id_str, self.units, self.withdrawal.withdrawal_date, self.entry_row)

def withdrawal_row_post_init(sender, instance, **kwargs):
    if instance.id is None:
        instance.old_units = 0
pre_save.connect(withdrawal_row_post_init, sender=WithdrawalRow)

def withdrawal_row_pre_save(sender, instance, **kwargs):
    instance.entry_row.units_left -= instance.units - instance.old_units
    instance.entry_row.save()
    instance.old_units = instance.units
pre_save.connect(withdrawal_row_pre_save, sender=WithdrawalRow)

def withdrawal_row_pre_delete(sender, instance, **kwargs):
    instance.entry_row.units_left += instance.old_units
    instance.entry_row.save()
pre_delete.connect(withdrawal_row_pre_delete, sender=WithdrawalRow)


class UnitWork(models.Model):
    work_type = models.ForeignKey(UnitWorkPrices)
    price_per_unit = models.FloatField(blank=True)
    date = models.DateField()
    units = models.IntegerField()

    def __unicode__(self):
        return u"%s of %s @ %s for %s" % (self.work_type.work_type, self.units, self.date, self.work_type.customer)

def unitwork_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_unit = instance.work_type.price_per_unit
pre_save.connect(unitwork_pre_save, sender=UnitWork)



class StorageLog(models.Model):
    entry_row = models.ForeignKey(EntryRow)
    date = models.DateField()
    price_per_kilo_per_day = models.FloatField()
    units_left = models.IntegerField()


    class Meta:
        permissions = (("view_storagelog", "View"),
                       ("view_own_storagelog", "View own"))

    @property
    def cost(self):
        return self.gross_weight_left * self.price_per_kilo_per_day

    @property
    def nett_weight_left(self):
        return self.entry_row.nett_weight_per_unit * self.units_left

    @property
    def gross_weight_left(self):
        return self.entry_row.gross_weight_per_unit * self.units_left

    def __unicode__(self):
        return u"%s for %s: %s à %s" % (self.date, self.entry_row, self.units_left, self.price_per_kilo_per_day)

def storagelog_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.date = datetime.date.today()
        instance.price_per_kilo_per_day = instance.entry_row.entry.customer.price_per_kilo_per_day
        instance.units_left = instance.entry_row.units_left
pre_save.connect(storagelog_pre_save, sender=StorageLog)
