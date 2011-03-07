from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import Group, User, UserManager, Permission
from django.db.models.signals import *
from lasso_global.models import *
import utils.modelhelpers
import re

_name = _("Lasso_Customer")
_name2 = _("lasso_customer")

if utils.modelhelpers.SubclasModelMixin not in User.__bases__:
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
    instance._is_new = instance.id is None
pre_save.connect(organization_pre_save, sender=Organization)
def organization_post_save(sender, instance, **kwargs):
    if instance._is_new:
        for permission in Permission.objects.filter(content_type__app_label="lasso_warehandling", content_type__name__in=("Entry", "storage log", "unit work", "Withdrawal"), name="View own").all():
            instance.permissions.add(permission)
    instance._is_new = False
post_save.connect(organization_post_save, sender=Organization)

class Contact(User):
    class Meta:
        permissions = (("change_access_contact", "Change access"),)

    address = models.TextField(blank=True, verbose_name=_("Address"))
    phone = models.CharField(max_length=200, blank=True, verbose_name=_("Phone"))
    fax = models.CharField(max_length=200, blank=True, verbose_name=_("Fax"))
    organization = models.ForeignKey(Organization, verbose_name=_("Organization"))
    title = models.CharField(max_length=30, blank=True, verbose_name=_("Title"))

def contact_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
    if not instance.username:
        instance.username = re.compile(r"[^a-z0-9]").sub("_", ("%s %s" % (instance.first_name, instance.last_name)).lower())
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(contact_pre_save, sender=Contact)

def contact_post_save(sender, instance, **kwargs):
    if instance.groups.filter(id=instance.organization.id).count() == 0:
        instance.groups.add(instance.organization)
        instance.save()
post_save.connect(contact_post_save, sender=Contact)

class Customer(Organization):
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    customer_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Customer nr"))

pre_save.connect(organization_pre_save, sender=Customer)
post_save.connect(organization_post_save, sender=Customer)

class OriginalSeller(Organization):
    class Meta:
        verbose_name = _('Original seller')
        verbose_name_plural = _('Original sellers')
    origin = models.ForeignKey(Origin, verbose_name=_("Default origin"), null=True, blank=True)
pre_save.connect(organization_pre_save, sender=OriginalSeller)
post_save.connect(organization_post_save, sender=OriginalSeller)

class Destination(Organization):
    class Meta:
        verbose_name = _('Destination')
        verbose_name_plural = _('Destinations')
pre_save.connect(organization_pre_save, sender=Destination)
post_save.connect(organization_post_save, sender=Destination)

class Transporter(Organization):
    class Meta:
        verbose_name = _('Transporter')
        verbose_name_plural = _('Transporters')
pre_save.connect(organization_pre_save, sender=Transporter)
post_save.connect(organization_post_save, sender=Transporter)

class UnitWorkPrices(models.Model):
    class Meta:
        verbose_name = _('Unit work price')
        verbose_name_plural = _('Unit work prices')
        unique_together = ("customer", "work_type")
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"))
    work_type = models.ForeignKey(UnitWorkType, verbose_name=_("Work type"))
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=6, verbose_name=_("Price per unit"))

    def __unicode__(self):
        return _("%(customer)s: %(price_per_unit)s for %(work_type)s") % {"customer":self.customer, "price_per_unit":self.price_per_unit, "work_type":self.work_type}

class WarehandlingPrice(models.Model):
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"))

    name = models.CharField(max_length=200, blank=True, verbose_name=_("Name"))
    is_default = models.BooleanField(blank=True, verbose_name=_("Is default"), default=False)

    price_per_kilo_per_day = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per kilo per day"))
    price_per_kilo_per_entry = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per kilo per entry"))
    price_per_kilo_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per kilo per withdrawal"))

    price_per_unit_per_day = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per unit per day"))
    price_per_unit_per_entry = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per unit per entry"))
    price_per_unit_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Price per unit per withdrawal"))

    price_min_per_day = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per day"))
    price_min_per_entry = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per entry"))
    price_min_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per withdrawal"))

    def __unicode__(self):
        return _("%(name)s entry=%(price_per_kilo_per_entry)s/kg+%(price_per_unit_per_entry)s/unit&min%(price_min_per_entry)s withdrawal=%(price_per_kilo_per_withdrawal)s/kg+%(price_per_unit_per_withdrawal)s/unit&min%(price_min_per_withdrawal)s day=%(price_per_kilo_per_day)s/kg+%(price_per_unit_per_day)s/unit&min%(price_min_per_day)s") % {
            'name': self.name,
            'price_per_kilo_per_day': self.price_per_kilo_per_day,
            'price_per_kilo_per_entry': self.price_per_kilo_per_entry,
            'price_per_kilo_per_withdrawal': self.price_per_kilo_per_withdrawal,
            
            'price_per_unit_per_day': self.price_per_unit_per_day,
            'price_per_unit_per_entry': self.price_per_unit_per_entry,
            'price_per_unit_per_withdrawal': self.price_per_unit_per_withdrawal,
                      
            'price_min_per_day': self.price_min_per_day,
            'price_min_per_entry': self.price_min_per_entry,
            'price_min_per_withdrawal': self.price_min_per_withdrawal}

