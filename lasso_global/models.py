# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import *
from django import forms
import datetime
from lasso.utils import *
import django.contrib.auth.models

class Origin(models.Model):
    name = models.CharField(max_length=200, blank=True)
    reference_nr = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return self.name

# Note: This is a singleton!!!
class Insurance(models.Model):
    percent = models.FloatField()

    def __unicode__(self):
        return unicode(self.percent)

    @classmethod
    def get(cls):
        all = cls.objects.all()
        if all:
            return all[0].percent
        return 0.0
