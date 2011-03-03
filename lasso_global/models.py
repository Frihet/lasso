# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import *
from django import forms
import datetime
from lasso.utils import *
import django.contrib.auth.models

_name = _("Lasso_Global")
_name2 = _("lasso_global")

# Note: This is a singleton!!!
class Insurance(models.Model):
    class Meta:
        verbose_name = _('Insurance')
        verbose_name_plural = _('Insurances')

    percent = models.FloatField(verbose_name=_("Percent"))

    def __unicode__(self):
        return unicode(self.percent)

    @classmethod
    def get(cls):
        all = cls.objects.all()
        if all:
            return all[0].percent
        return 0.0

class Origin(models.Model):
    class Meta:
        verbose_name = _('Origin')
        verbose_name_plural = _('Origins')

    name = models.CharField(max_length=200, blank=True, verbose_name=_("Name"))
    reference_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Reference nr"))
    
    def __unicode__(self):
        return self.name

class TransportCondition(models.Model):
    class Meta:
        verbose_name = _('Transport condition')
        verbose_name_plural = _('Transport conditions')

    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class VehicleType(models.Model):
    class Meta:
        verbose_name = _('Vehicle type')
        verbose_name_plural = _('Vehicle types')

    name = models.CharField(max_length=200)
    min_temp = models.FloatField(verbose_name=_("Min. temp."))
    max_temp = models.FloatField(verbose_name=_("Max. temp."))

    def __unicode__(self):
        return self.name
