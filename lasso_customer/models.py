from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import Group, User, UserManager
from django.db.models.signals import *
import utils.modelhelpers
import re

User.__bases__ += (utils.modelhelpers.SubclasModelMixin,)

@utils.modelhelpers.subclassproxy
def __unicode__(self):
    return "%s (%s %s)" % (self.username, self.first_name, self.last_name)
User.__unicode__ = __unicode__

class UnitWorkType(models.Model):
    class Meta:
        verbose_name = _('Unit work type')
        verbose_name_plural = _('Unit work types')

    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class Organization(Group):
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    title = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=200, blank=True)
    fax = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.title

def organization_pre_save(sender, instance, **kwargs):
    instance.name = type(instance).__name__ + "_" + instance.title
pre_save.connect(organization_pre_save, sender=Organization)

class Contact(User):
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=200, blank=True)
    fax = models.CharField(max_length=200, blank=True)
    organization = models.ForeignKey(Organization)

def contact_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
        instance.username = re.compile(r"[^a-z0-9]").sub("_", ("%s %s" % (instance.first_name, instance.last_name)).lower())
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(contact_pre_save, sender=Contact)

class Customer(Organization):
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    customer_nr = models.CharField(max_length=200, blank=True)

    price_per_kilo_per_day = models.FloatField(default=0.0)
    price_per_kilo_per_entry = models.FloatField(default=0.0)
    price_per_kilo_per_withdrawal = models.FloatField(default=0.0)

    price_per_unit_per_day = models.FloatField(default=0.0)
    price_per_unit_per_entry = models.FloatField(default=0.0)
    price_per_unit_per_withdrawal = models.FloatField(default=0.0)
pre_save.connect(organization_pre_save, sender=Customer)

class OriginalSeller(Organization):
    class Meta:
        verbose_name = _('Original seller')
        verbose_name_plural = _('Original sellers')
pre_save.connect(organization_pre_save, sender=OriginalSeller)

class Destination(Organization):
    class Meta:
        verbose_name = _('Destination')
        verbose_name_plural = _('Destinations')
pre_save.connect(organization_pre_save, sender=Destination)

class Transporter(Organization):
    class Meta:
        verbose_name = _('Transporter')
        verbose_name_plural = _('Transporters')
pre_save.connect(organization_pre_save, sender=Transporter)

class UnitWorkPrices(models.Model):
    class Meta:
        verbose_name = _('Unit work price')
        verbose_name_plural = _('Unit work prices')
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    price_per_unit = models.FloatField()

    def __unicode__(self):
        return "%s: %s for %s" % (self.customer, self.price_per_unit, self.work_type)
