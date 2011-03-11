from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    (r'^lasso_warehandling/costlog/', include('lasso_warehandling.urls.costlog')),
    (r'^lasso_warehandling/entry/', include('lasso_warehandling.urls.entry')),
    (r'^lasso_warehandling/withdrawal/', include('lasso_warehandling.urls.withdrawal')),
    (r'^lasso_warehouse/overview/', include('lasso_warehouse.urls.overview')),
    (r'^lasso_labelprinting/', include('lasso_labelprinting.urls')),
    (r'^doc/', include('django.contrib.admindocs.urls')),
    (r'^rosetta/', include('rosetta.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^', include(admin.site.urls)),
)
