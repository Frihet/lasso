from django.conf.urls.defaults import *
from django.conf import settings
import os.path

urlpatterns = patterns('',
    (r'^print$', 'lasso_labelprinting.views.print_labels'),
    (r'^adresses$', 'lasso_labelprinting.views.addresses'),
)
