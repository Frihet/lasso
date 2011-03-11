from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^(?P<entry_id>\d+)/print$', 'lasso_warehandling.views.entry_print'),
)
