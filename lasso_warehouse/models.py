from django.utils.translation import ugettext_lazy as _
from django.db import models
from lasso.lasso_warehandling.models import *

class Warehouse(models.Model):
    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    name = models.CharField(max_length=200, verbose_name=_("Name"))

    def __unicode__(self):
        return self.name

class Row(models.Model):
    class Meta:
        verbose_name = _('Row')
        verbose_name_plural = _('Rows')

    warehouse = models.ForeignKey(Warehouse, verbose_name=_("Warehouse"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    def __unicode__(self):
        return _("%(name)s in %(warehouse.name)s") % {"name":self.name, "warehouse.name":self.warehouse.name}

class PalletSpace(models.Model):
    class Meta:
        verbose_name = _('Pallet space')
        verbose_name_plural = _('Pallet spaces')

    row = models.ForeignKey(Row, verbose_name=_("Row"))
    entry_row = models.ForeignKey(EntryRow, null=True, blank=True, related_name="locations", verbose_name=_("Entry row"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    size_w = models.FloatField(verbose_name=_("Width"))
    size_h = models.FloatField(verbose_name=_("Height"))
    size_d = models.FloatField(verbose_name=_("Depth"))

    def __unicode__(self):
        return _("%(row.name)s-%(name)s in %(row.warehouse.name)s") % {"row.name":self.row.name, "name":self.name, "row.warehouse.name":self.row.warehouse.name}

class EmptyPalletSpace(PalletSpace):
    dummy = _('empty pallet space')
    class Meta:
        verbose_name = _('Empty pallet space')
        verbose_name_plural = _('Empty pallet spaces')
    class Meta:
        proxy = True

class FilledPalletSpace(PalletSpace):
    dummy = _('filled pallet space')
    class Meta:
        verbose_name = _('Filled pallet space')
        verbose_name_plural = _('Filled pallet spaces')
    class Meta:
        proxy = True
