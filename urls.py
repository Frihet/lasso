from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^lasso/', include('lasso.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^rosetta/', include('rosetta.urls')),

    (r'^i18n/', include('django.conf.urls.i18n')),

    (r'costlog/(?P<year>\d+)/(?P<month>\d+)', 'lasso.lasso_warehandling.views.costlog'),

)
