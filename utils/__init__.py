import datetime
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
import django.utils.safestring
import django.core.urlresolvers
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt, ErrorDict, ErrorList, ValidationError
import django.forms.forms
import django.forms.fields
import django.forms.models

def xdaterange(d1, d2):
    return (d1 + datetime.timedelta(x)
            for x in xrange(0, (d2 - d1).days))

if not hasattr(django.forms.forms.BaseForm, 'pre_init_validation_baseform_init'):
    django.forms.forms.BaseForm.pre_init_validation_baseform_init = django.forms.forms.BaseForm.__init__
    def __init__(self, *arg, **kw):
        self.pre_init_validation_baseform_init(*arg, **kw)
        self.init_clean()
    django.forms.forms.BaseForm.__init__ = __init__
    def init_clean(self):
        self._errors = ErrorDict()
        for name, field in self.fields.items():
            if hasattr(field, 'init_clean'):
                try:
                    field.init_clean(self)
                except ValidationError, e:
                    self._errors[name] = self.error_class(e.messages)
        if not self._errors:
            self._errors = None
    django.forms.forms.BaseForm.init_clean = init_clean

    django.forms.models.BaseInlineFormSet.pre_init_validation_baseinlineformset_construct_form = django.forms.models.BaseInlineFormSet._construct_form
    def _construct_form(self, i, **kwargs):
        form = self.pre_init_validation_baseinlineformset_construct_form(i, **kwargs)
        if form._errors and self.fk.name in form._errors:
            del form._errors[self.fk.name]
        if not form._errors:
            form._errors = None
        return form
    django.forms.models.BaseInlineFormSet._construct_form = _construct_form

if not hasattr(django.forms.models.ModelChoiceField, 'init_clean'):
    def init_clean(self, form):
        if self.required and self.queryset.count() == 0:
            raise ValidationError(_("You must first create at least one of these before you can save."))
    django.forms.models.ModelChoiceField.init_clean = init_clean

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


class ReadonlyTextInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        final_attrs['type'] = 'hidden'
        return mark_safe(u'<input%s />' % flatatt(final_attrs) + force_unicode(value))

class ReadonlyCharField(django.forms.CharField):
    widget = ReadonlyTextInput
