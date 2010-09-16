# -*- coding: utf-8 -*-
from django.db import models
from lasso.lasso_customer.models import *
from django.contrib import admin
from django.db.models.signals import *
from django import forms

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
    product_description = models.CharField(max_length=400)
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


class Withdrawal(models.Model):
    price_per_kilo_out = models.FloatField()
    withdrawal_date = models.DateField()
    arrival_date = models.DateField()

    def __unicode__(self):
        return u"%s @ %s" % (self.id, self.withdrawal_date)

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
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    date = models.DateField()
    units = models.IntegerField()

    def __unicode__(self):
        return u"%s of %s @ %s for %s" % (self.work_type, self.units, self.date, self.customer)
