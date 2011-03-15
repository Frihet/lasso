# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from lasso.lasso_customer.models import *
from lasso.lasso_global.models import *
from django.db.models.signals import *
from django import forms
import datetime
from lasso.utils import *
import django.contrib.auth.models
import operator
import settings

_name = _("Lasso_Warehandling")
_name2 = _("lasso_warehandling")

class Entry(models.Model):
    customer = models.ForeignKey(Customer, related_name="customer_for_entry", verbose_name=_("Customer"))
    price = models.ForeignKey(WarehandlingPrice, related_name="price_for_entry", verbose_name=_("Price model"))
    original_seller = models.ForeignKey(OriginalSeller, blank=True, null=True, related_name="original_seller_for_entry", verbose_name=_("Original seller"))
    arrival_date = models.DateField(default=lambda: datetime.date.today(), verbose_name=_("Arrival date"))
    insurance = models.BooleanField(blank=True, verbose_name=_("Insurance"))
    transporter = models.ForeignKey(Transporter, verbose_name=_("Transporter"))
    insurance_percentage = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Insurance percentage"))
    price_per_kilo_per_entry = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Price per kilo per entry"))
    price_per_unit_per_entry = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Price per unit per entry"))
    price_min_per_entry = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per entry"))
    custom_handling_date = models.DateField(null=True, blank=True, verbose_name=_("Custom handling date"))
    customs_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Customs nr"))
    customer_entry_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Customer entry nr"))

    class Meta:
        permissions = (("view_entry", "View"),
                       ("view_own_entry", "View own"))
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')

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
        return _(u"%(id)s @ %(arrival_date)s for %(customer)s") % {'id': self.id, 'arrival_date': self.arrival_date, 'customer': self.customer}

def entry_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.insurance_percentage = Insurance.get()
        instance.price_per_kilo_per_entry = instance.price.price_per_kilo_per_entry
        instance.price_per_unit_per_entry = instance.price.price_per_unit_per_entry
        instance.price_min_per_entry = instance.price.price_min_per_entry
pre_save.connect(entry_pre_save, sender=Entry)

class EntryRow(models.Model):
    class Meta:
        verbose_name = _('Entry row')
        verbose_name_plural = _('Entry rows')

    entry = models.ForeignKey(Entry, related_name="rows", verbose_name=_("Entry"))
    customs_certificate_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Customs certificate nr"))
    product_nr = models.CharField(max_length=400, blank=True, verbose_name=_("Product nr"))
    uom = models.CharField(max_length=200, blank=True, verbose_name=_("UoM"))
    units = models.IntegerField(verbose_name=_("Units"))
    units_left = models.IntegerField(blank=True, verbose_name=_("Units left"))
    nett_weight = models.DecimalField(max_digits=12, decimal_places=6, verbose_name=_("Nett weight"))
    _nett_weight_left = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Nett weight left"))
    gross_weight = models.DecimalField(max_digits=12, decimal_places=6, verbose_name=_("Gross weight"))
    _gross_weight_left = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Gross weight left"))
    product_value = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True, verbose_name=_("Product value"))

    use_before = models.DateField(null=True, blank=True, verbose_name=_("Use before"))
    product_description = models.CharField(max_length=400, blank=True, verbose_name=_("Product description"))
    product_state = models.BooleanField(verbose_name=_("Product state"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))
    arrival_temperatures = FloatListField(verbose_name=_("Arrival temperatures"))

    auto_weight = models.BooleanField(default=True, verbose_name=_("Auto weight"))

    origin = models.ForeignKey(Origin, blank=True, null=True, verbose_name=_("Origin"))

    @property
    def cost(self):
        return self.entry_cost + self.insurance_cost

    @property
    def entry_cost(self):
        return max(self.gross_weight * self.entry.price_per_kilo_per_entry + self.units * self.entry.price_per_unit_per_entry,
                   self.entry.price_min_per_entry)        

    @property
    def insurance_cost(self):
        if not self.entry.insurance or not self.product_value:
            return 0
        return self.product_value * self.entry.insurance_percentage

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

    def get_nett_weight_left(self):
        if self.auto_weight:
            return self.nett_weight_per_unit * self.units_left
        else:
            return self._nett_weight_left
    def set_nett_weight_left(self, value):
        if self.auto_weight:
            raise Exception("Can not set nett weight left on EntryRow with auto_weight set")
        self._nett_weight_left = value
    nett_weight_left = property(get_nett_weight_left, set_nett_weight_left)

    def get_gross_weight_left(self):
        if self.auto_weight:
            return self.gross_weight_per_unit * self.units_left
        else:
            return self._gross_weight_left
    def set_gross_weight_left(self, value):
        if self.auto_weight:
            raise Exception("Can not set gross weight left on EntryRow with auto_weight set")
        self._gross_weight_left = value
    gross_weight_left = property(get_gross_weight_left, set_gross_weight_left)

    @property
    def product_value_left(self):
        if self.product_value_per_unit is None: return None
        return self.product_value_per_unit * self.units_left

    @property
    def id_str(self):
        return "%s.%s" % (self.entry.id, self.id)

    def log(self, until = None):
        # Note: Don't log today until tomorrow, stuff might be added afterwards!
        # Units left doesn't change until the day after a withdrawal, but on the same day for an entry!

        if until is None: until = datetime.date.today()

        log_items = []

        # Start logging on the arrival day, or on the day after the
        # last logged date if there is a log
        try:
            last_log = self.logs.order_by("-date")[0]
            last_date = last_log.date + datetime.timedelta(1)
            units_left = last_log.units_left
            if not self.auto_weight:
                 nett_weight_left = last_log.nett_weight_left
                 gross_weight_left = last_log.gross_weight_left
        except IndexError:
            last_date = self.entry.arrival_date
            units_left = self.units
            if not self.auto_weight:
                nett_weight_left = self.nett_weight
                gross_weight_left = self.gross_weight

        # Plus one day, because withdrawals are logged the day after they are done
        steps = [(withdrawal_row.withdrawal.withdrawal_date + datetime.timedelta(1), withdrawal_row)
                 for withdrawal_row in WithdrawalRow.objects.filter(entry_row = self,
                                                                    withdrawal__withdrawal_date__gte = last_date,
                                                                    withdrawal__withdrawal_date__lt = until
                                                                    ).order_by("withdrawal__withdrawal_date")]
        steps += [(until, WithdrawalRow(units=0, nett_weight=0, gross_weight=0))]

        for (next_date, withdrawal_row) in steps:
            for storage_date in xdaterange(last_date, next_date):
                # FIXME: Check for units_left / gross_weight > 0...
                log_item = StorageLog()
                log_item.units_left = units_left
                if not self.auto_weight:
                    log_item.nett_weight_left = nett_weight_left
                    log_item.gross_weight_left = gross_weight_left
                log_item.date = storage_date
                log_item.entry_row = self
                log_item.price_per_kilo_per_day = self.entry.price.price_per_kilo_per_day
                log_item.price_per_unit_per_day = self.entry.price.price_per_unit_per_day
                log_item.price_min_per_day = self.entry.price.price_min_per_day
                log_item.save()
                log_items.append(log_item)
            last_date = next_date
            units_left -= withdrawal_row.units
            if not self.auto_weight:
                nett_weight_left -= withdrawal_row.nett_weight
                gross_weight_left -= withdrawal_row.gross_weight

        return log_items

    def __unicode__(self):
        return _(u"%(id_str)s: %(product_description)s: %(units_left)s %(uom)s left à %(nett_weight_per_unit).2fkg (arr.: %(entry.arrival_date)s, for: %(entry.customer)s)") % {"id_str": self.id_str, "product_description": self.product_description, "units_left": self.units_left, "uom": self.uom or _('units'), "nett_weight_per_unit": self.nett_weight_per_unit, "entry.arrival_date": self.entry.arrival_date, "entry.customer": self.entry.customer}

def entry_row_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.units_left = instance.units
        if not instance.auto_weight:
            instance.nett_weight_left = instance.nett_weight
            instance.gross_weight_left = instance.gross_weight
    if instance.origin is None and instance.entry.original_seller is not None:
        instance.origin = instance.entry.original_seller.origin

#    Saving a withdrawal updates units_left so deleting all logs then
#    doesn't work...
#    for log in instance.logs.all():
#        log.delete()
pre_save.connect(entry_row_pre_save, sender=EntryRow)

class Withdrawal(models.Model):
    class Meta:
        permissions = (("view_withdrawal", "View"),
                       ("view_own_withdrawal", "View own"))
        verbose_name = _('Withdrawal')
        verbose_name_plural = _('Withdrawals')

    customer = models.ForeignKey(Customer, related_name='customer_for_withdrawal', verbose_name=_("Customer"))

    responsible = models.ForeignKey(django.contrib.auth.models.User, related_name="responsible_for", verbose_name=_("Responsible"))
    place_of_departure = models.CharField(max_length=200, blank=True, verbose_name=_("Place of departure"), default=settings.LASSO_DEFAULT_PLACE_OF_DEPARTURE)
    
    transport_condition = models.ForeignKey(TransportCondition, blank=True, null=True, verbose_name=_("Transport condition"))
    transport_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Transport nr"))
    order_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Order nr"))

    destination = models.ForeignKey(Destination, related_name='destination_for_withdrawal', verbose_name=_("Destination"))
    withdrawal_date = models.DateField(default=lambda: datetime.date.today(), verbose_name=_("Withdrawal date"))
    arrival_date = models.DateField(null=True, blank=True, default=lambda: datetime.date.today()+datetime.timedelta(1), verbose_name=_("Arrival_date"))
    vehicle_type = models.ForeignKey(VehicleType, verbose_name=_("Vehicle type"))
    opening_hours = models.CharField(max_length=200, blank=True, verbose_name=_("Opening hours"))
    transporter = models.ForeignKey(Transporter, verbose_name=_("Transporter"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))

    @property
    def reference_nr(self):
        try:
            # Don't ask my why...
            # 2007 = 01..12
            # 2008 = 21..32
            # 2009 = 41..52
            # 2010 = 61..72
            month = (self.withdrawal_date.year - 2007) * 20 + self.withdrawal_date.month

            origin = 248
            return ('%3s.%2s.%4s' % (origin, month, self.customer.customer_nr)).replace(' ', '0')
        except:
            return "XXX.XX.XXXX"

    @property
    def insurance(self):
        if reduce(operator.__and__, [row.entry_row.entry.insurance for row in self.rows], True):
            return 2
        if reduce(operator.__or__, [row.entry_row.entry.insurance for row in self.rows], True):
            return 1
        return 0

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

class WithdrawalRow(models.Model):
    class Meta:
        verbose_name = _('Withdrawal row')
        verbose_name_plural = _('Withdrawal rows')

    withdrawal = models.ForeignKey(Withdrawal, related_name="rows", verbose_name=_("Withdrawal"))
    entry_row = models.ForeignKey(EntryRow, related_name="withdrawal_rows", verbose_name=_("Entry row"))
    old_units = models.IntegerField(blank=True, verbose_name=_("Old units"))
    units = models.IntegerField(verbose_name=_("Units"))
    old_nett_weight = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Old nett weight"))
    _nett_weight = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, default=0, verbose_name=_("Nett weight"))
    old_gross_weight = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Old gross weight"))
    _gross_weight = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, default=0, verbose_name=_("Gross weight"))

    price_per_kilo_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Price per kilo per withdrawal"))
    price_per_unit_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Price per unit per withdrawal"))
    price_min_per_withdrawal = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per withdrawal"))

    @property
    def cost(self):
        return max(self.gross_weight * self.price_per_kilo_per_withdrawal + self.units * self.price_per_unit_per_withdrawal,
                   self.price_min_per_withdrawal)

    def get_nett_weight(self):
        if self.entry_row.auto_weight:
            return self.entry_row.nett_weight_per_unit * self.units
        else:
            return self._nett_weight
    def set_nett_weight(self, value):
        #if self.entry_row.auto_weight:
        #    raise Exception("Can not set nett weight for EntryRow with auto_weight set")
        self._nett_weight = value
    nett_weight = property(get_nett_weight, set_nett_weight)

    def get_gross_weight(self):
        if self.entry_row.auto_weight:
            return self.entry_row.gross_weight_per_unit * self.units
        else:
            return self._gross_weight
    def set_gross_weight(self, value):
        #if self.entry_row.auto_weight:
        #    raise Exception("Can not set gross weight for EntryRow with auto_weight set")
        self._gross_weight = value
    gross_weight = property(get_gross_weight, set_gross_weight)

    @property
    def id_str(self):
        return "%s.%s" % (self.withdrawal.id, self.id)

    def __unicode__(self):
        return _(u"%(id_str)s (%(units)s @ %(withdrawal.withdrawal_date)s from %(entry_row)s)") % {"id_str": self.id_str, "units": self.units, "withdrawal.withdrawal_date": self.withdrawal.withdrawal_date, "entry_row": self.entry_row}

def withdrawal_row_post_init(sender, instance, **kwargs):
    if instance.id is None:
        instance.old_units = 0
        if not instance.entry_row.auto_weight:
            instance.old_nett_weight = 0.0
            instance.old_gross_weight = 0.0
pre_save.connect(withdrawal_row_post_init, sender=WithdrawalRow)

def withdrawal_row_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.price_per_kilo_per_withdrawal = instance.entry_row.entry.price.price_per_kilo_per_withdrawal
        instance.price_per_unit_per_withdrawal = instance.entry_row.entry.price.price_per_unit_per_withdrawal
        instance.price_min_per_withdrawal = instance.entry_row.entry.price.price_min_per_withdrawal

    instance.entry_row.units_left -= instance.units - instance.old_units
    instance.old_units = instance.units
    if not instance.entry_row.auto_weight:
        instance.entry_row.nett_weight_left -= instance.nett_weight - instance.old_nett_weight
        instance.entry_row.gross_weight_left -= instance.gross_weight - instance.old_gross_weight
        instance.old_nett_weight = instance.nett_weight
        instance.old_gross_weight = instance.gross_weight
    instance.entry_row.save()
    for log in instance.entry_row.logs.filter(date__gte=instance.withdrawal.withdrawal_date).all():
        log.delete()
pre_save.connect(withdrawal_row_pre_save, sender=WithdrawalRow)

def withdrawal_row_pre_delete(sender, instance, **kwargs):
    instance.entry_row.units_left += instance.old_units
    if not instance.entry_row.auto_weight:
        instance.entry_row.nett_weight_left += instance.old_nett_weight
        instance.entry_row.gross_weight_left += instance.old_gross_weight
    instance.entry_row.save()
pre_delete.connect(withdrawal_row_pre_delete, sender=WithdrawalRow)


class UnitWork(models.Model):
    class Meta:
        verbose_name = _('Unit work')
        verbose_name_plural = _('Unit works')
        permissions = (("view_unitwork", "View"),
                       ("view_own_unitwork", "View own"))

    entry = models.ForeignKey(Entry, verbose_name=_("Entry"), null=True, related_name="unit_works")
    withdrawal = models.ForeignKey(Withdrawal, verbose_name=_("Withdrawal"), null=True, related_name="unit_works")

    work_type = models.ForeignKey(UnitWorkPrices, verbose_name=_("Work type"))
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=6, blank=True, verbose_name=_("Price per unit"))
    date = models.DateField(verbose_name=_("Date"))
    units = models.IntegerField(verbose_name=_("Units"))

    @property
    def cost(self):
        return self.units * self.price_per_unit

    def __unicode__(self):
        return u"%s of %s @ %s for %s" % (self.work_type.work_type, self.units, self.date, self.work_type.customer)

def unitwork_pre_save(sender, instance, **kwargs):
    instance.price_per_unit = instance.work_type.price_per_unit
    if instance.date is None:
        if instance.entry is not None:
            instance.date = instance.entry.arrival_date
        elif instance.withdrawal is not None:
            instance.date = instance.withdrawal.withdrawal_date
pre_save.connect(unitwork_pre_save, sender=UnitWork)


class StorageLog(models.Model):
    class Meta:
        verbose_name = _('Storage log')
        verbose_name_plural = _('Storage log entries')
        permissions = (("view_storagelog", "View"),
                       ("view_own_storagelog", "View own"))

    entry_row = models.ForeignKey(EntryRow, related_name="logs", verbose_name=_("Entry row"))
    date = models.DateField(verbose_name=_("Date"))
    price_per_kilo_per_day = models.DecimalField(max_digits=12, decimal_places=6, verbose_name=_("Price per kilo per day"))
    price_per_unit_per_day = models.DecimalField(max_digits=12, decimal_places=6, verbose_name=_("Price per unit per day"))
    price_min_per_day = models.DecimalField(max_digits=12, decimal_places=6, default=0.0, verbose_name=_("Minimum price per day"))
    units_left = models.IntegerField(verbose_name=_("Units left"))
    _nett_weight_left = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Nett weight left"))
    _gross_weight_left = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True, verbose_name=_("Gross weight left"))

    @property
    def cost(self):
        # 0.00001 is our precission for the moment: Note: We might not
        # get to 0.0 exactly due to rounding errors. Maybe we should
        # have used an integer field and multiplied with
        # 0.000something instead of float?
        if self.gross_weight_left <= 0.00001 and self.units_left <= 0.00001:
            return 0
        return max(self.gross_weight_left * self.price_per_kilo_per_day + self.units_left * self.price_per_unit_per_day,
                   self.price_min_per_day)        

    @property
    def nett_weight_left(self):
        if  self.entry_row.auto_weight:
            return self.entry_row.nett_weight_per_unit * self.units_left
        else:
            return self._nett_weight_left

    @property
    def gross_weight_left(self):
        if  self.entry_row.auto_weight:
            return self.entry_row.gross_weight_per_unit * self.units_left
        else:
            return self._gross_weight_left

    def __unicode__(self):
        return u"%s for %s: %s à %s/kg + %s/unit" % (self.date, self.entry_row, self.units_left, self.price_per_kilo_per_day, self.price_per_unit_per_day)

def storagelog_pre_save(sender, instance, **kwargs):
    if getattr(instance, 'date', None) is None: instance.date = datetime.date.today()
    if getattr(instance, 'price_per_kilo_per_day', None) is None: instance.price_per_kilo_per_day = instance.entry_row.entry.price.price_per_kilo_per_day
    if getattr(instance, 'price_per_unit_per_day', None) is None: instance.price_per_unit_per_day = instance.entry_row.entry.price.price_per_unit_per_day
    if getattr(instance, 'price_min_per_day', None) is None: instance.price_min_per_day = instance.entry_row.entry.price.price_min_per_day
    if getattr(instance, 'units_left', None) is None: instance.units_left = instance.entry_row.units_left
    if not instance.entry_row.auto_weight:
        if getattr(instance, 'nett_weight_left', None) is None: instance.nett_weight_left = instance.entry_row.nett_weight_left
        if getattr(instance, 'gross_weight_left', None) is None: instance.gross_weight_left = instance.entry_row.gross_weight_left
pre_save.connect(storagelog_pre_save, sender=StorageLog)
