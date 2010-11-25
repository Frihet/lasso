from django.db import models

class Address(models.Model):
    customer_nr = models.IntegerField()
    platform = models.CharField(max_length = 20)
    name = models.CharField(max_length = 200)
    street = models.CharField(max_length = 200)
    zip = models.CharField(max_length = 200)
    city = models.CharField(max_length = 200)

    @property
    def as_dict(self):
        return {"customer_nr": self.customer_nr,
                "platform": self.platform,
                "name": self.name,
                "street": self.street,
                "zip": self.zip,
                "city": self.city}

    def __unicode__(self):
        return "%s %s" % (self.customer_nr, self.name)
