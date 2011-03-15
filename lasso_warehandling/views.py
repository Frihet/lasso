# Create your views here.
from django.utils.translation import ugettext_lazy as _
from django.http import *
from lasso.lasso_warehandling.models import *
from lasso.lasso_customer.models import *
from django.shortcuts import *
from django.contrib.admin.views.decorators import *
from django import template
from django.core.urlresolvers import *
import django.template.loader
import datetime
import calendar
import django.http
import shutil
import tempfile
import subprocess
import utils.latex
import urllib
import socket
import settings

class CostlogForm(forms.Form):
    year = forms.IntegerField(required=False, label=_("Year"))
    month = forms.IntegerField(required=False, label=_("Month"))
    customer = forms.ModelChoiceField(queryset = Customer.objects.all(), required=False, label=_("Customer"))
    entry = forms.ModelChoiceField(queryset = Entry.objects.all(), required=False, label=_("Entry"))
    style = forms.ChoiceField(choices=(('long', _('Long')), ('short', _('Short'))), required=False, label=_("Style"))
    group_by = forms.ChoiceField(choices=(('all', _("Don't group")), ('customer', _('Customer')), ('entry', _('Entry')), ('entry_row', _('Entry row'))), required=False, label=_("Group by"))

KWARG_PARAMS = ('year', 'month', 'customer', 'entry')

def sum_costlog_data(unit_filter, entry_filter, withdrawal_filter, storage_filter, year, months, group_by = None):
    def setup_info():
        return {'sum_work': {'units': 0,
                             'cost':0},
                'sum_in': {'units': 0,
                           'nett_weight':0,
                           'gross_weight':0,
                           'entry_cost': 0,
                           'insurance_cost': 0,
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
                'customers': {},
                'entries': {},
                'entry_items': {},
                'work_items': {},
                'withdrawal_items': {},
                'storage_items': {}}

    last_date = datetime.date.today()
    logs = StorageLog.objects.filter(**storage_filter).order_by("-date")
    if len(logs):
        last_date = logs[0].date

    dates = []
    for month in months:
        for day in xrange(1, calendar.monthrange(year, month)[1]+1):
            d = datetime.date(year, month, day)
            if d <= last_date:
                dates.append(d)

    def setup_full_info():
        res = setup_info()
        res['storage_log'] = {}
        res['short_storage_log'] = []
        for d in dates:
            res['storage_log'][d] = setup_info()
        return res

    def get_infos(customer, entry, entry_row, d):
        "Ensure sum-collection-info-dicts exists and return them!"
        customer_id = customer and customer.id or None
        entry_id = entry and entry.id or None
        entry_row_id = entry_row and entry_row.id or None
        if (group_by is None or 'customer' in group_by) and customer_id not in info['per_customer']:
            info['per_customer'][customer_id] = setup_full_info()
            info['per_customer'][customer_id]['obj'] = customer
        if (group_by is None or 'entry' in group_by) and entry_id not in info['per_entry']:
            info['per_entry'][entry_id] = setup_full_info()
            info['per_entry'][entry_id]['obj'] = entry
        if (group_by is None or 'entry_row' in group_by) and entry_row_id not in info['per_entry_row']:
            info['per_entry_row'][entry_row_id] = setup_full_info()
            info['per_entry_row'][entry_row_id]['obj'] = entry_row
        infos = ()
        if group_by is None or 'all' in group_by:
            infos += (info['total'], info['total']['storage_log'][d])
        if group_by is None or 'customer' in group_by:
            infos += (info['per_customer'][customer_id], info['per_customer'][customer_id]['storage_log'][d])
        if group_by is None or 'entry' in group_by:
            infos += (info['per_entry'][entry_id], info['per_entry'][entry_id]['storage_log'][d])
        if group_by is None or 'entry_row' in group_by:
            infos += (info['per_entry_row'][entry_row_id], info['per_entry_row'][entry_row_id]['storage_log'][d])
        return infos

    def calculate_short_storage_log(info):
        last_short = None
        for d in dates:
            last_long = info['storage_log'].get(d - datetime.timedelta(1), None)
            current_long = info['storage_log'][d]

            if (last_short is None or
                current_long['entry_items']):

                last_short = setup_info()
                last_short['days'] = 0
                last_short['start_date'] = d
                info['short_storage_log'].append(last_short)

            for group in ('sum_work', 'sum_in', 'sum_out'):
                for key, value in current_long[group].iteritems():
                    last_short[group][key] += value

            for key in ('units', 'nett_weight', 'gross_weight'):
                last_short['sum'][key] = current_long['sum'][key]
            for key in ('cost', 'total_cost'):
                last_short['sum'][key] += current_long['sum'][key]

            last_short['days'] += 1
            last_short['end_date'] = d

            if current_long['withdrawal_items']:
                last_short = None

        if info['short_storage_log'] and info['short_storage_log'][0]['sum']['units'] == 0 and info['short_storage_log'][0]['sum']['total_cost'] == 0:
            del info['short_storage_log'][0]
        if info['short_storage_log'] and info['short_storage_log'][-1]['sum']['units'] == 0 and info['short_storage_log'][-1]['sum']['total_cost'] == 0:
            del info['short_storage_log'][-1]

    info = {'dates': dates,
            'total': setup_full_info(),
            'per_customer': {},
            'per_entry': {},
            'per_entry_row': {}}

    for item in EntryRow.objects.filter(**entry_filter):
        for i in get_infos(item.entry.customer, item.entry, item, item.entry.arrival_date):
            i['entry_items'][item.id] = item
            i['sum_in']['units'] += item.units
            i['sum_in']['nett_weight'] += item.nett_weight
            i['sum_in']['gross_weight'] += item.gross_weight
            i['sum_in']['entry_cost'] += item.entry_cost
            i['sum_in']['insurance_cost'] += item.insurance_cost
            i['sum_in']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    for item in UnitWork.objects.filter(**unit_filter):
        for i in get_infos(item.work_type.customer, item.entry, None, item.date):
            i['work_items'][item.id] = item
            i['sum_work']['units'] += item.units
            i['sum_work']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    for item in WithdrawalRow.objects.filter(**withdrawal_filter):
        for i in get_infos(item.entry_row.entry.customer, item.entry_row.entry, item.entry_row, item.withdrawal.withdrawal_date):
            i['withdrawal_items'][item.id] = item
            i['sum_out']['units'] += item.units
            i['sum_out']['nett_weight'] += item.nett_weight
            i['sum_out']['gross_weight'] += item.gross_weight
            i['sum_out']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    for item in StorageLog.objects.filter(**storage_filter):
        for i in get_infos(item.entry_row.entry.customer, item.entry_row.entry, item.entry_row, item.date):
            i['storage_items'][item.id] = item
            i['sum']['units'] += item.units_left
            i['sum']['nett_weight'] += item.nett_weight_left
            i['sum']['gross_weight'] += item.gross_weight_left
            i['sum']['cost'] += item.cost
            i['sum']['total_cost'] += item.cost

    if group_by is None or 'all' in group_by:
        calculate_short_storage_log(info['total'])
    if group_by is None or 'customer' in group_by:
        for customer, customer_info in info['per_customer'].iteritems():
            calculate_short_storage_log(customer_info)
    if group_by is None or 'entry' in group_by:
        for entry, entry_info in info['per_entry'].iteritems():
            calculate_short_storage_log(entry_info)

    if group_by is None or 'entry_row' in group_by:
        for entry_row, entry_row_info in info['per_entry_row'].iteritems():
            calculate_short_storage_log(entry_row_info)

    return info

def kw_to_filters(year, month=None, customer=None, entry=None):
    year = int(year)
    filters = {}
    filters['entry_filter'] = {'entry__arrival_date__year': year}
    filters['withdrawal_filter'] = {'withdrawal__withdrawal_date__year': year}
    filters['storage_filter'] = {'date__year': year}
    filters['unit_filter'] = {'date__year': year}
    filters['year'] = year
    filters['months'] = range(1, 13)

    if month is not None:
        filters['unit_filter']['date__month'] = month
        filters['entry_filter']['entry__arrival_date__month'] = month
        filters['withdrawal_filter']['withdrawal__withdrawal_date__month'] = month
        filters['storage_filter']['date__month'] = month
        filters['months'] = [int(month)]

    if customer is not None:
        filters['unit_filter']['work_type__customer__id'] = customer
        filters['entry_filter']['entry__customer__id'] = customer
        filters['withdrawal_filter']['withdrawal__customer__id'] = customer
        filters['storage_filter']['entry_row__entry__customer__id'] = customer

    if entry is not None:
        filters['unit_filter']['entry__id'] = entry
        filters['entry_filter']['entry__id'] = entry
        filters['withdrawal_filter']['entry_row__entry__id'] = entry
        filters['storage_filter']['entry_row__entry__id'] = entry

    return filters

def empty_filters():
    filters = {}
    filters['entry_filter'] = {'id':-1}
    filters['withdrawal_filter'] = {'id':-1}
    filters['storage_filter'] = {'id':-1}
    filters['unit_filter'] = {'id':-1}
    filters['year'] = 2010
    filters['months'] = []
    return filters

@staff_member_required
def costlog(request, *arg, **kw):
    oldkw = dict(kw)
    params = dict(request.GET.iteritems())
    oldparams = dict(params)
    info = {}

    if request.GET:
        info.update(request.GET.iteritems())
        for name in KWARG_PARAMS:
            if name in request.GET:
                if request.GET[name]:
                    kw[name] = request.GET[name]
                elif name in kw:
                    del kw[name]

    if 'year' not in kw or kw['year'] == '0':
        today = datetime.date.today()
        kw['year'] = today.year
        kw['month'] = today.month
    
    group_by = request.GET.get('group_by', 'all')

    info.update(kw)
    info['groups'] = []
    info['config_form'] = CostlogForm(info)

    if not request.user.has_perm('lasso_warehandling.view_storagelog'):
        customers = Customer.objects.filter(id__in = [group.id for group in request.user.groups.all()])
        if not request.user.has_perm('lasso_warehandling.view_own_storagelog') or len(customers) == 0:
            info.update(sum_costlog_data(**empty_filters()))
            return render_to_response('lasso_warehandling/costlog.html', info, context_instance=template.RequestContext(request))
        if 'customer' not in kw or int(kw['customer']) not in [customer.id for customer in customers]:
            kw['customer'] = customers[0].id

    if 'action_lager_monatuebersicht' in params:
        params['group_by'] = 'entry_row'
        params['format'] = 'pdf'
        params['template'] = 'lager_monatuebersicht'
        del params['action_lager_monatuebersicht']

    if 'action_lager_inventar_monat' in params:
        params['group_by'] = 'entry_row'
        params['format'] = 'pdf'
        params['template'] = 'inventar_monat'
        del params['action_lager_inventar_monat']

    if kw != oldkw or params != oldparams:
        return HttpResponseRedirect(reverse('lasso_warehandling.views.costlog', kwargs=kw) + '?' + urllib.urlencode(params))

    def make_link(**kwargs):
        new_params = dict(request.GET.iteritems())
        new_kwargs = dict(kw)
        for name, value in kwargs.iteritems():
            if name in KWARG_PARAMS:
                new_kwargs[name] = value
            else:
                new_params[name] = value
        return reverse('lasso_warehandling.views.costlog', kwargs=new_kwargs) + '?' + urllib.urlencode(new_params)

    info['print_link_lager_monatuebersicht'] = make_link(group_by = 'entry_row', format = 'pdf', template = 'lager_monatuebersicht')
    info['print_link_lager_inventar_monat'] = make_link(group_by = 'entry_row', format = 'pdf', template = 'inventar_monat')

    if not request.user.has_perm('lasso_warehandling.view_storagelog'):
        info['config_form'].fields['customer'].widget.attrs['disabled'] = 'disabled'
        info['config_form'].fields['entry'].queryset = info['config_form'].fields['entry'].queryset.filter(customer__in = request.user.groups.all())

    if 'year' in kw:
        info.update(sum_costlog_data(group_by = [group_by], **kw_to_filters(**kw)))

        if group_by == 'all':
            info['groups'] = [info['total']]
        elif group_by == 'customer':
            info['groups'] = info['per_customer'].values()
        elif group_by == 'entry':
            info['groups'] = info['per_entry'].values()
        elif group_by == 'entry_row':
            info['groups'] = info['per_entry_row'].values()

    if request.GET.get('format', 'html') in ('tex', 'pdf'):
        tpl = request.GET.get('template', 'lager_monatuebersicht')
        assert '/' not in tpl
        return utils.latex.render_to_response("lasso_warehandling/costlog/%s.tex" % (tpl,), info, template.RequestContext(request))

    return render_to_response('lasso_warehandling/costlog.html', info, template.RequestContext(request))

@staff_member_required
def withdrawal_print(request, withdrawal_id, *arg, **kw):
    info = {}
    info['withdrawal'] = Withdrawal.objects.get(id=withdrawal_id)
    info['units'] = sum(row.units for row in info['withdrawal'].rows.all())
    info['nett_weight'] = sum(row.nett_weight for row in info['withdrawal'].rows.all())
    info['gross_weight'] = sum(row.gross_weight for row in info['withdrawal'].rows.all())

    return utils.latex.render_to_response("lasso_warehandling/withdrawal_print.tex", info, template.RequestContext(request))

def zencode(str):
    return unicode(str).encode('cp850')

def zprint(args,copies,lmarg=50, tmarg=25):
    data = ''
    for job in xrange(0, copies):
        lheight = 60
        lpos = tmarg
        data += "^XA\n"
        data += "^CI13\n"

        platsize = 200
        #data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg, tmarg, platsize, platsize, zencode(args['platform']))

        # The barcode
        text = zencode("%(id)s;%(arrival_date)s;%(units)s;%(use_before)s;%(product_description)s" % args)
        data += "^FO%s,%s\n" % (lmarg + 300, tmarg)
        data += "^BQN,N,5,N,N,N\n"
        data +="^FD>;%s^FS\n" % (text,)

        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg, 50, 50, zencode("FLS"))
        #data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg + 50, 50, 50, zencode("Vecom"))

        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg + 150, 50, 50, zencode(args['id']))

        data += "^FO%s,%s^A0N,40,40^FD%s^FS\n" % (lmarg, tmarg + 200, "-------------------")

        lpos = tmarg + 200 + lheight

        text = zencode("""E. Datum: %(arrival_date)s
Anz. Kart.: %(units)s
Halt. Datum: %(use_before)s
Art. Bez.: %(product_description)s""" % args)
        for line in text.split("\n"):
            data += "^FO%s,%s^A0N,40,40^A0,%s,%s^FD%s^FS\n" % (lmarg, lpos, lheight-5, lheight-5, line.strip())
            lpos += lheight

        # Job number
        text = "%s/%s" % (job+1, copies)
        data += "^FO%s,%s^A0N,40,40^A0,%s,%s^FD%s^FS\n" % (775-lmarg-len(text)*23, 600-lheight, lheight-5, lheight-5, text)

        data += "^XZ\n"

    print "==========================================================="
    print data
    return
    fp = socket.create_connection(settings.LASSO_LABELPRINTING_PRINTER)
    try:
        # Not supported by ZPL emulation mode for Citizen
        # fp.send("~HS\n")
        # pstat = fp.recv(128).strip().split(",")
        # paper_out = pstat[1]
        # paused = pstat[2]
        # if paper_out != "0":
        #     raise Exception("Out of paper")
        # if paused != "0":
        #     raise Exception("Paused")
        fp.send(data)
    finally:
        fp.close()


@staff_member_required
def entry_print(request, entry_id, *arg, **kw):
    entry = Entry.objects.get(id=entry_id)
    info = {'entry': entry}

    if request.method == 'POST':
        labels = 0
        for row in entry.rows.all():
            row_labels = int(request.POST.get(row.id_str + '_labels') or '0')
            labels += row_labels
            zprint(
                {'id': row.id_str,
                 'arrival_date': entry.arrival_date,
                 'units': row.units,
                 'use_before': row.use_before,
                 'product_description': row.product_description},
                row_labels)
        info['messages'] = [_('%(labels)s labels printed') % {'labels': labels}]

    return render_to_response('lasso_warehandling/print_entry.html', info, template.RequestContext(request))
