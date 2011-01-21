# Create your views here.
from django.utils.translation import ugettext_lazy as _
from django.http import *
from lasso.lasso_warehandling.models import *
from lasso.lasso_customer.models import *
from django.shortcuts import *
from django.contrib.admin.views.decorators import *
from django import template
from django.core.urlresolvers import *
import datetime
import calendar

class CostlogForm(forms.Form):
    year = forms.IntegerField(required=False, label=_("Year"))
    month = forms.IntegerField(required=False, label=_("Month"))
    customer = forms.ModelChoiceField(queryset = Customer.objects.all(), required=False, label=_("Customer"))
    entry = forms.ModelChoiceField(queryset = Entry.objects.all(), required=False, label=_("Entry"))

@staff_member_required
def costlog(request, *arg, **kw):
    redirect = False
    if request.GET:
        for name, value in request.GET.items():
            if value == '':
                 if name in kw:
                     del kw[name]
            else:
                kw[name] = value
        redirect = True

    if 'year' in kw and kw['year'] == '0':
        today = datetime.date.today()
        kw['year'] = today.year
        kw['month'] = today.month
        redirect = True

    if not request.user.has_perm('lasso_warehandling.view_costlog'):
        if not not request.user.has_perm('lasso_warehandling.view_own_costlog'):
            return render_to_response('lasso_warehandling/costlog.html', info, context_instance=template.RequestContext(request))
        if 'customer' not in kw or int(kw['customer']) != request.user.id:
            kw['customer'] = request.user.id
            redirect = True

    if redirect:
        return HttpResponseRedirect(reverse('lasso_warehandling.views.costlog', kwargs=kw))

    info = dict(kw)
    info.update({'config_form': CostlogForm(kw),
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
                 'dates': [],
                 'storage_log': {}})

    if not request.user.has_perm('lasso_warehandling.view_costlog'):
        info['config_form'].fields['customer'].widget.attrs['disabled'] = 'disabled'
        info['config_form'].fields['entry'].queryset = info['config_form'].fields['entry'].queryset.filter(customer = request.user)

    if 'year' in kw:
        entry_filter = {'entry__arrival_date__year': kw['year']}
        withdrawal_filter = {'withdrawal__withdrawal_date__year': kw['year']}
        storage_filter = {'date__year': kw['year']}
        year = int(kw['year'])
        months = range(1, 13)

        if 'month' in kw:
            entry_filter['entry__arrival_date__month'] = kw['month']
            withdrawal_filter['withdrawal__withdrawal_date__month'] = kw['month']
            storage_filter['date__month'] = kw['month']
            months = [int(kw['month'])]
         
        if 'customer' in kw:
            entry_filter['entry__customer__id'] = kw['customer']
            withdrawal_filter['withdrawal__customer__id'] = kw['customer']
            storage_filter['entry_row__entry__customer__id'] = kw['customer']

        if 'entry' in kw:
            entry_filter['entry__id'] = kw['entry']
            withdrawal_filter['entry_row__entry__id'] = kw['entry']
            storage_filter['entry_row__entry__id'] = kw['entry']

        for month in months:
            for day in xrange(1, calendar.monthrange(year, month)[1]+1):
                info['dates'].append(datetime.date(year, month, day) )

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

@staff_member_required
def withdrawal_print(request, withdrawal_id, *arg, **kw):
    info = {}
    info['withdrawal'] = Withdrawal.objects.get(id=withdrawal_id)
    info['units'] = sum(row.units for row in info['withdrawal'].rows.all())
    info['nett_weight'] = sum(row.nett_weight for row in info['withdrawal'].rows.all())
    info['gross_weight'] = sum(row.gross_weight for row in info['withdrawal'].rows.all())

    return render_to_response('lasso_warehandling/withdrawal_print.html', info, context_instance=template.RequestContext(request))
