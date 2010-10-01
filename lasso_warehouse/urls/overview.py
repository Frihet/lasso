from django.conf.urls.defaults import *
from django.conf import settings
import os.path

urlpatterns = patterns('',
    (r'^js$', 'lasso_warehouse.views.overview_js'),
    (r'^$', 'lasso_warehouse.views.overview'),
)
