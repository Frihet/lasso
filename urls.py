from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    (r'^lasso_warehandling/costlog/', include('lasso_warehandling.urls.costlog')),
    (r'^lasso_warehouse/overview/', include('lasso_warehouse.urls.overview')),
    (r'^doc/', include('django.contrib.admindocs.urls')),
    (r'^rosetta/', include('rosetta.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^', include(admin.site.urls)),
)
