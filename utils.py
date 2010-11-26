import datetime
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _

def xdaterange(d1, d2):
    return (d1 + datetime.timedelta(x)
            for x in xrange(0, (d2 - d1).days))

class FloatListInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if not isinstance(value, (str, unicode)):
            if value is None: value = []
            value = ' '.join(str(part) for part in value)
        return forms.TextInput.render(self, name, value, attrs)

class FloatListFormField(forms.Field):
    default_error_messages = {'invalid': _(u'Enter real numbers.')}

    widget = FloatListInput

    def clean(self, value):
        super(FloatListFormField, self).clean(value)
        if value:
            try:
                res = [float(part.strip()) for part in value.split(' ') if part.strip()]
                return res
            except (ValueError, TypeError), e:
                print e
                raise forms.ValidationError(self.error_messages['invalid'])
        else:
            return []

class FloatListField(models.Field):
    description = "A list of float values"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(FloatListField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'text'

    def to_python(self, value):
        if value:
            return  [float(part) for part in value.split(' ')]
        else:
            return []

    def get_db_prep(self, value, connection = None, prepared=False):
        return ' '.join(str(part) for part in value)

    def get_db_prep_save(self, value, connection = None):
        return self.get_db_prep(value, connection)

    def formfield(self, **kwargs):
        defaults = {'form_class': FloatListFormField}
        defaults.update(kwargs)
        return super(FloatListField, self).formfield(**defaults)
