from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import *
import re

class UnitWorkType(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class Customer(User):

    name = models.CharField(max_length=200)
    address = models.TextField()
    price_per_kilo_per_day = models.FloatField()
    price_per_kilo_per_entry = models.FloatField()
    price_per_kilo_per_withdrawal = models.FloatField()

    def __unicode__(self):
        return self.name

def customer_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
        instance.username = re.compile(r"[^a-z0-9]").sub("_", instance.name.lower())
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(customer_pre_save, sender=Customer)


class UnitWorkPrices(models.Model):
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    price_per_unit = models.FloatField()

    def __unicode__(self):
        return "%s: %s for %s" % (self.customer, self.price_per_unit, self.work_type)
