from django.db import models
import django.contrib.auth.models
from django.db.models.signals import *


class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True
    @property
    def group(self):
        return ', '.join(unicode(group) for group in self.groups.order_by('name').all())
def user_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        instance.is_staff = True
    if '$' not in instance.password:
        instance.set_password(instance.password)
pre_save.connect(user_pre_save, sender=User)

class Group(django.contrib.auth.models.Group):
    class Meta:
        proxy = True

