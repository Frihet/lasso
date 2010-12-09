from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, UserManager
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

class Organization(User):
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    _username_prefix = ""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=200, blank=True)
    fax = models.CharField(max_length=200, blank=True)
    def __unicode__(self):
        return self.name

def organization_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
        instance.username = instance._username_prefix + re.compile(r"[^a-z0-9]").sub("_", instance.name.lower())
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(organization_pre_save, sender=Organization)

class Contact(Organization):
    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    _username_prefix = "co_"
    for_organization = models.ForeignKey(Organization, related_name = 'contacts')
pre_save.connect(organization_pre_save, sender=Contact)

class Customer(Organization):
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    _username_prefix = "cu_"
    price_per_kilo_per_day = models.FloatField()
    price_per_kilo_per_entry = models.FloatField()
    price_per_kilo_per_withdrawal = models.FloatField()

    price_per_unit_per_day = models.FloatField()
    price_per_unit_per_entry = models.FloatField()
    price_per_unit_per_withdrawal = models.FloatField()
pre_save.connect(organization_pre_save, sender=Customer)

class Transporter(Organization):
    class Meta:
        verbose_name = _('Transporter')
        verbose_name_plural = _('Transporters')
    _username_prefix = "tr_"
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
