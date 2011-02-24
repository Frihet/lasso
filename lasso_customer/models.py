from django.db import models
from django.contrib import admin

class UnitWorkType(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
admin.site.register(UnitWorkType)

class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    price_per_kilo_per_day = models.FloatField()
    price_per_kilo_per_entry = models.FloatField()
    price_per_kilo_per_withdrawal = models.FloatField()

    def __unicode__(self):
        return self.name

class UnitWorkPrices(models.Model):
    customer = models.ForeignKey(Customer)
    work_type = models.ForeignKey(UnitWorkType)
    price_per_unit = models.FloatField()

    def __unicode__(self):
        return "%s: %s for %s" % (self.customer, self.price_per_unit, self.work_type)

class UnitWorkPricesInline(admin.TabularInline):
    model = UnitWorkPrices

class CustomerAdmin(admin.ModelAdmin):
    inlines = [UnitWorkPricesInline,]

admin.site.register(Customer, CustomerAdmin)
