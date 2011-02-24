# Create your views here.

from django.http import *
from lasso.lasso_warehouse.models import *
from django.shortcuts import *
from django.contrib.admin.views.decorators import *
from django import template
from django.core.urlresolvers import *

@staff_member_required
def overview(request, *arg, **kw):
    info = {}
    return render_to_response('lasso_warehouse/overview.html', info, context_instance=template.RequestContext(request))

@staff_member_required
def overview_js(request, *arg, **kw):
    info = {
        'warehouses': dict((obj.pk, obj) for obj in Warehouse.objects.all()),
        'rows': dict((obj.pk, obj) for obj in Row.objects.all()),
        'pallet_spaces': dict((obj.pk, obj) for obj in PalletSpace.objects.all())}
    info['entries'] = dict((pallet_space.entry.pk, pallet_space.entry) for pallet_space in info['pallet_spaces'].itervalues() if pallet_space.entry != None)
    info['customers'] = dict((entry.customer.pk, entry.customer) for entry in info['entries'].itervalues())

    return render_to_response('lasso_warehouse/overview.js', info, context_instance=template.RequestContext(request), mimetype='text/javascript')
