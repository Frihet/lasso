from django.utils.translation import ugettext_lazy as _
from django.db import models
from lasso.lasso_warehandling.models import *

class Warehouse(models.Model):
    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Row(models.Model):
    class Meta:
        verbose_name = _('Row')
        verbose_name_plural = _('Rows')

    warehouse = models.ForeignKey(Warehouse)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s in %s" % (self.name, self.warehouse.name)

class PalletSpace(models.Model):
    class Meta:
        verbose_name = _('Pallet space')
        verbose_name_plural = _('Pallet spaces')

    row = models.ForeignKey(Row)
    entry_row = models.ForeignKey(EntryRow, null=True, blank=True, related_name="locations")
    name = models.CharField(max_length=200)
    size_w = models.FloatField()
    size_h = models.FloatField()
    size_d = models.FloatField()

    def __unicode__(self):
        return "%s-%s in %s" % (self.row.name, self.name, self.row.warehouse.name)
