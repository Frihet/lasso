# Create your views here.

from django.http import HttpResponse
from lasso.lasso_warehandling.models import *
from django.shortcuts import *
from django.contrib.admin.views.decorators import *
from django import template
import calendar

@staff_member_required
def costlog(request, *arg, **kw):
    entry_filter = {'entry__arrival_date__year': kw['year']}
    withdrawal_filter = {'withdrawal__withdrawal_date__year': kw['year']}
    storage_filter = {'date__year': kw['year']}
    year = int(kw['year'])
    if 'month' in kw:
        entry_filter['entry__arrival_date__month'] = kw['month']
        withdrawal_filter['withdrawal__withdrawal_date__month'] = kw['month']
        storage_filter['date__month'] = kw['month']
        months = [int(kw['month'])]

    info = {'sum_in': {'units': 0,
                       'nett_weight':0,
                       'gross_weight':0,
                       'cost':0},
            'sum_out': {'units': 0,
                        'nett_weight':0,
                        'gross_weight':0,
                        'cost':0},
            'sum': {'units':0,
                    'nett_weight':0,
                    'gross_weight':0,
                    'cost':0,
                    'total_cost':0}}

    info['dates'] = []
    for month in months:
        for day in xrange(*calendar.monthrange(year, month)):
            info['dates'].append(datetime.date(year, month, day) )

    info['storage_log'] = {}
    for d in info['dates']:
        info['storage_log'][d] = {
            'sum_in': {'units': 0,
                       'nett_weight':0,
                       'gross_weight':0,
                       'cost':0},
            'sum_out': {'units': 0,
                        'nett_weight':0,
                        'gross_weight':0,
                        'cost':0},
            'sum': {'units':0,
                    'nett_weight':0,
                    'gross_weight':0,
                    'cost':0,
                    'total_cost':0},
            'entry_items': {},
            'withdrawal_items': {},
            'storage_items': {}}
    
    for item in EntryRow.objects.filter(**entry_filter):
        e = info['storage_log'][item.entry.arrival_date]
        e['entry_items'][item.id] = item 
        for i in (e,info):
            i['sum_in']['units'] += item.units
            i['sum_in']['nett_weight'] += item.nett_weight
            i['sum_in']['gross_weight'] += item.gross_weight
            i['sum_in']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost
    
    for item in WithdrawalRow.objects.filter(**withdrawal_filter):
        e = info['storage_log'][item.withdrawal.withdrawal_date]
        e['withdrawal_items'][item.id] = item
        for i in (e,info):
            i['sum_out']['units'] += item.units
            i['sum_out']['nett_weight'] += item.nett_weight
            i['sum_out']['gross_weight'] += item.gross_weight
            i['sum_out']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    for item in StorageLog.objects.filter(**storage_filter):
        e = info['storage_log'][item.date]
        e['storage_items'][item.entry_row.id] = item 
        for i in (e,info):
            i['sum']['units'] += item.units_left
            i['sum']['nett_weight'] += item.nett_weight_left
            i['sum']['gross_weight'] += item.gross_weight_left
            i['sum']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    return render_to_response('lasso_warehandling/costlog.html', info, context_instance=template.RequestContext(request))

