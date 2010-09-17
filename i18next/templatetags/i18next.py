from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext

register = template.Library()

@stringfilter
def ugettext_filter(value):
    return ugettext(value)
register.filter('ugettext', ugettext_filter)
register.filter('_', ugettext_filter)
