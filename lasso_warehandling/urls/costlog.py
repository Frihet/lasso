from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^(?P<year>\d+)/(?P<month>\d+)/for/(?P<customer>\d+)/(?P<entry>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^(?P<year>\d+)/for/(?P<customer>\d+)/(?P<entry>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^for/(?P<customer>\d+)/(?P<entry>\d+)$', 'lasso_warehandling.views.costlog'),

    (r'^(?P<year>\d+)/(?P<month>\d+)/for/(?P<customer>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^(?P<year>\d+)/for/(?P<customer>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^for/(?P<customer>\d+)$', 'lasso_warehandling.views.costlog'),

    (r'^(?P<year>\d+)/(?P<month>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^(?P<year>\d+)$', 'lasso_warehandling.views.costlog'),
    (r'^$', 'lasso_warehandling.views.costlog'),
)
