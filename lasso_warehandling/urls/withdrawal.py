from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^(?P<withdrawal_id>\d+)/print$', 'lasso_warehandling.views.withdrawal_print'),
)
