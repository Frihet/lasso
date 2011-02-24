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
    return _("%(username)s (%(first_name)s %(last_name)s)") % {"username": self.username, "first_name": self.first_name, "last_name": self.last_name}
User.__unicode__ = __unicode__

class UnitWorkType(models.Model):
    class Meta:
        verbose_name = _('Unit work type')
        verbose_name_plural = _('Unit work types')

    name = models.CharField(max_length=200, verbose_name=_("Name"))

    def __unicode__(self):
        return self.name

class Organization(Group):
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    title = models.CharField(max_length=200, blank=True, verbose_name=_("Title"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    phone = models.CharField(max_length=200, blank=True, verbose_name=_("Phone"))
    fax = models.CharField(max_length=200, blank=True, verbose_name=_("Fax"))

    def __unicode__(self):
        return self.title

def organization_pre_save(sender, instance, **kwargs):
    instance.name = type(instance).__name__ + "_" + instance.title
pre_save.connect(organization_pre_save, sender=Organization)

class Contact(User):
    address = models.TextField(blank=True, verbose_name=_("Address"))
    phone = models.CharField(max_length=200, blank=True, verbose_name=_("Phone"))
    fax = models.CharField(max_length=200, blank=True, verbose_name=_("Fax"))
    organization = models.ForeignKey(Organization, verbose_name=_("Organization"))

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

    customer_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Customer nr"))

    price_per_kilo_per_day = models.FloatField(default=0.0, verbose_name=_("Price per kilo per day"))
    price_per_kilo_per_entry = models.FloatField(default=0.0, verbose_name=_("Price per kilo per entry"))
    price_per_kilo_per_withdrawal = models.FloatField(default=0.0, verbose_name=_("Price per kilo per withdrawal"))

    price_per_unit_per_day = models.FloatField(default=0.0, verbose_name=_("Price per unit per day"))
    price_per_unit_per_entry = models.FloatField(default=0.0, verbose_name=_("Price per unit per entry"))
    price_per_unit_per_withdrawal = models.FloatField(default=0.0, verbose_name=_("Price per unit per withdrawal"))
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
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"))
    work_type = models.ForeignKey(UnitWorkType, verbose_name=_("Work type"))
    price_per_unit = models.FloatField(verbose_name=_("Price per unit"))

    def __unicode__(self):
        return _("%(customer)s: %(price_per_unit)s for %(work_type)s") % {"customer":self.customer, "price_per_unit":self.price_per_unit, "work_type":self.work_type}
