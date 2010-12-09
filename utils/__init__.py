import datetime
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
import django.utils.safestring
import django.core.urlresolvers

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
        if not isinstance(value, (str, unicode)):
            return value
        value = value.strip()
        if value:
            return  [float(part.strip()) for part in value.split(' ')]
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

class ModelLinkWidget(django.forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            return ''
        if hasattr(value, 'all'):
            value = value.all()
        elif not isinstance(value, (list, tuple)):
            value = [value]
        lines = ("<a href='%s'>%s</a>" % (django.core.urlresolvers.reverse('admin:%s_%s_change' % (type(obj)._meta.app_label, type(obj)._meta.module_name), args=(obj.id,)), obj)
                 for obj in value)
        out = "<ul>%s</ul>" % ('\n'.join("<li>%s</li>" % (line,) for line in lines))
        return django.utils.safestring.mark_safe(unicode(out))

class ModelLinkField(django.forms.ModelChoiceField):
    widget = ModelLinkWidget
