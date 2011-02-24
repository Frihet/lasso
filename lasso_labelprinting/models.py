from django.utils.translation import ugettext_lazy as _
from django.db import models

class Address(models.Model):
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    customer_nr = models.IntegerField(verbose_name=_("Customer nr"))
    platform = models.CharField(max_length = 20, verbose_name=_("Platform"))
    name = models.CharField(max_length = 200, verbose_name=_("Name"))
    street = models.CharField(max_length = 200, verbose_name=_("Street"))
    zip = models.CharField(max_length = 200, verbose_name=_("Zip"))
    city = models.CharField(max_length = 200, verbose_name=_("City"))

    @property
    def as_dict(self):
        return {"customer_nr": self.customer_nr,
                "platform": self.platform,
                "name": self.name,
                "street": self.street,
                "zip": self.zip,
                "city": self.city}

    def __unicode__(self):
        return _("%(customer_nr)s %(name)s") % {"customer_nr":self.customer_nr, "name":self.name}
