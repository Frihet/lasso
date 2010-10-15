from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import *
import re

class UnitWorkType(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class Contact(User):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=200)
    fax = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

def contact_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
        instance.username = re.compile(r"[^a-z0-9]").sub("_", instance.name.lower())
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(contact_pre_save, sender=Contact)

class Customer(Contact):
    price_per_kilo_per_day = models.FloatField()
    price_per_kilo_per_entry = models.FloatField()
    price_per_kilo_per_withdrawal = models.FloatField()

    price_per_unit_per_day = models.FloatField()
    price_per_unit_per_entry = models.FloatField()
    price_per_unit_per_withdrawal = models.FloatField()
pre_save.connect(contact_pre_save, sender=Customer)

class Transporter(Contact):
    pass
pre_save.connect(contact_pre_save, sender=Transporter)

class UnitWorkPrices(models.Model):
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    price_per_unit = models.FloatField()

    def __unicode__(self):
        return "%s: %s for %s" % (self.customer, self.price_per_unit, self.work_type)
