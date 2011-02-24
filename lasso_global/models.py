# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import *
from django import forms
import datetime
from lasso.utils import *
import django.contrib.auth.models

class Origin(models.Model):
    class Meta:
        verbose_name = _('Origin')
        verbose_name_plural = _('Origins')

    name = models.CharField(max_length=200, blank=True, verbose_name=_("Name"))
    reference_nr = models.CharField(max_length=200, blank=True, verbose_name=_("Reference nr"))
    
    def __unicode__(self):
        return self.name

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
