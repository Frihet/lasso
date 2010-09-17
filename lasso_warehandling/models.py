# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms
import datetime

class Entry(models.Model):
    customer = models.ForeignKey(Customer)
    arrival_date = models.DateField()
    price_per_kilo_per_entry = models.FloatField()
    def __unicode__(self):
        return u"%s @ %s for %s" % (self.id, self.arrival_date, self.customer)

def entry_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_kilo_per_entry = instance.customer.price_per_kilo_per_entry
pre_save.connect(entry_pre_save, sender=Entry)

class EntryRow(models.Model):
    entry = models.ForeignKey(Entry)
    custom_handling_date = models.DateField()
    customs_receipt_nr = models.CharField(max_length=200)
    customs_testimony_nr = models.CharField(max_length=200)
    transporter = models.CharField(max_length=200)
    product_nr = models.CharField(max_length=400)
    uom = models.CharField(max_length=200)
    units = models.IntegerField()
    units_left = models.IntegerField()
    nett_weight = models.FloatField()
    gross_weight = models.FloatField()
    product_value= models.FloatField()

    use_before = models.DateField()
    product_description = models.CharField(max_length=400)
    product_state = models.CharField(max_length=200)
    comment = models.TextField()
    arrival_temperature = models.FloatField()
    
    @property
    def id_str(self):
        return "%s.%s" % (self.entry.id, self.id)

    def __unicode__(self):
        return u"%s: %s (%s %s à %skg @ %s for %s)" % (self.id_str, self.product_description, self.units, self.uom, self.nett_weight, self.entry.arrival_date, self.entry.customer)


class Withdrawal(models.Model):
    customer = models.ForeignKey(Customer)
    price_per_kilo_per_withdrawal = models.FloatField()

    reference_nr = models.CharField(max_length=200)
    responsible = models.CharField(max_length=200)
    place_of_departure = models.CharField(max_length=200)
    
    insurance = models.CharField(max_length=200)
    transport_condition = models.CharField(max_length=200)
    transport_nr = models.CharField(max_length=200)
    order_nr = models.CharField(max_length=200)

    destination_address = models.TextField()
    withdrawal_date = models.DateField()
    arrival_date = models.DateField()
    vehicle_type = models.CharField(max_length=200)
    opening_hours = models.CharField(max_length=200)
    transporter = models.CharField(max_length=200)
    comment = models.TextField()

    def __unicode__(self):
        return u"%s @ %s" % (self.id, self.withdrawal_date)

def withdrawal_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_kilo_per_withdrawal = instance.customer.price_per_kilo_per_withdrawal
pre_save.connect(withdrawal_pre_save, sender=Withdrawal)

class WithdrawalRow(models.Model):
    withdrawal = models.ForeignKey(Withdrawal)
    entry_row = models.ForeignKey(EntryRow)
    old_units = models.IntegerField()
    units = models.IntegerField()

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
    price_per_unit = models.FloatField()
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

    def __unicode__(self):
        return u"%s for %s: %s à %s" % (self.date, self.entry_row, self.units_left, self.price_per_kilo_per_day)

def storagelog_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.date = datetime.datetime.now()
        instance.price_per_kilo_per_day = instance.entry_row.entry.customer.price_per_kilo_per_day
        instance.units_left = instance.entry_row.units_left
pre_save.connect(storagelog_pre_save, sender=StorageLog)

admin.site.register(StorageLog)
