from django.db import models
from django.contrib import admin
from lasso.lasso_warehandling.models import *

class Warehouse(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
admin.site.register(Warehouse)

class Row(models.Model):
    warehouse = models.ForeignKey(Warehouse)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s in %s" % (self.name, self.warehouse.name)
admin.site.register(Row)

class PalletSpace(models.Model):
    row = models.ForeignKey(Row)
    entry = models.ForeignKey(Entry, null=True, blank=True, related_name="locations")
    name = models.CharField(max_length=200)
    size_w = models.FloatField()
    size_h = models.FloatField()
    size_d = models.FloatField()

    def __unicode__(self):
        return "%s-%s in %s" % (self.row.name, self.name, self.row.warehouse.name)

admin.site.register(PalletSpace)
