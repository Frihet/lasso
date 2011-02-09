# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import *
from django.contrib.admin.views.decorators import *
from django import template
from django.core.urlresolvers import *
from django.http import *
import lasso_labelprinting.models
import os
import tempfile
import lasso.contrib.DocumentConverter
import csv
import codecs
import socket
import settings

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
        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg, tmarg, platsize, platsize, zencode(args['platform']))

        # The barcode
        text = zencode("%(customer_nr)s;%(name)s;%(street)s;%(zip)s;%(city)s;%(platform)s" % args)
        data += "^FO%s,%s\n" % (lmarg + 300, tmarg)
        data += "^BQN,N,5,N,N,N\n"
        data +="^FD>;%s^FS\n" % (text,)

        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg, 50, 50, zencode("FLS"))
        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg + 50, 50, 50, zencode("Vecom"))

        data += "^FO%s,%s^A0N,40,40^A0%s,%s^FD%s^FS\n" % (lmarg + 550, tmarg + 150, 50, 50, zencode(args['customer_nr']))

        data += "^FO%s,%s^A0N,40,40^FD%s^FS\n" % (lmarg, tmarg + 200, "-------------------")

        lpos = tmarg + 200 + lheight

        text = zencode("%(name)s\n%(street)s\n%(zip)s %(city)s" % args)
        for line in text.split("\n"):
            data += "^FO%s,%s^A0N,40,40^A0,%s,%s^FD%s^FS\n" % (lmarg, lpos, lheight-5, lheight-5, line.strip())
            lpos += lheight

        # Job number
        text = "%s/%s" % (job+1, copies)
        data += "^FO%s,%s^A0N,40,40^A0,%s,%s^FD%s^FS\n" % (775-lmarg-len(text)*23, 600-lheight, lheight-5, lheight-5, text)

        data += "^XZ\n"

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
def print_labels(request):
    messages = []
    if 'labellistfile' in request.FILES:
        f, path = tempfile.mkstemp(request.FILES['labellistfile'].name)
        csvpath = path + ".csv"
        try:
            try:
                f = os.fdopen(f, "w")
                try:
                    for chunk in request.FILES['labellistfile'].chunks():
                        f.write(chunk)
                finally:
                    f.close()

                converter = lasso.contrib.DocumentConverter.DocumentConverter()
                converter.convert(path, csvpath)

                addresses = []
                with open(csvpath, 'r') as f:
                    r = iter(csv.reader(f, dialect="excel"))
                    headers1 = r.next()
                    headers = r.next()
                    headers = [col.decode('utf-8') for col in headers]
                    for row in r:
                        row = dict(zip(headers, [col.decode('utf-8') for col in row]))
                        if row[u"Kdn. Nr. "].strip() == '':
                            break
                        total = int(row[u"TOTAL ¢ "])
                        if total > 0:
                            customer_nr = row[u"Kdn. Nr. "]
                            assert customer_nr.startswith("D1")
                            customer_nr = int(customer_nr[2:].lstrip("0") or "0")

                            addr = lasso_labelprinting.models.Address.objects.get(customer_nr=customer_nr)

                            addresses.append({'customer_nr': customer_nr, 'address': addr.as_dict, 'total': total})

                def acmp(a, b):
                    return cmp(a['customer_nr'], b['customer_nr'])
                addresses.sort(acmp)

                for address in addresses:
                    try:
                        #print "X", address['customer_nr'], address['address'], address['total']
                        zprint(address['address'], address['total'])
                    except Exception, e:
                        return render_to_response('lasso_labelprinting/print_labels.html', {'global_errors':[_('Unable to print document: %(error)s') % {'error': str(e)}]}, context_instance=template.RequestContext(request))
            except Exception, e:
                return render_to_response('lasso_labelprinting/print_labels.html', {'global_errors':[_('Unable to convert document: %(error)s') % {'error': str(e)}]}, context_instance=template.RequestContext(request))

        finally:
            try:
                os.unlink(csvpath)
            except:
                pass
            try:
                os.unlink(path)
            except:
                pass

        messages.append(_("Printed labels"))

    return render_to_response('lasso_labelprinting/print_labels.html', {'messages':messages}, context_instance=template.RequestContext(request))


@staff_member_required
def addresses(request):
    messages = []
    if 'addressfile' in request.FILES:

        f, path = tempfile.mkstemp(request.FILES['addressfile'].name)
        csvpath = path + ".csv"
        try:
            try:

                f = os.fdopen(f, "w")
                try:
                    for chunk in request.FILES['addressfile'].chunks():
                        f.write(chunk)
                finally:
                    f.close()

                converter = lasso.contrib.DocumentConverter.DocumentConverter()
                converter.convert(path, csvpath)

                with open(csvpath, 'r') as f:
                    r = iter(csv.reader(f, dialect="excel"))
                    headers = r.next()
                    headers = [col.decode('utf-8') for col in headers]
                    for row in r:
                        row = dict(zip(headers, [col.decode('utf-8') for col in row]))

                        addrs = lasso_labelprinting.models.Address.objects.filter(customer_nr = int(row['Lf. Nr.']))
                        if len(addrs):
                            addr = addrs[0]
                        else:
                            addr = lasso_labelprinting.models.Address()

                        addr.customer_nr = int(row['Lf. Nr.'])
                        addr.platform = row['Plattform']
                        addr.name = row['Firma']
                        addr.street = row['Strasse']
                        addr.zip = row['PLZ']
                        addr.city = row['Ort']
                        addr.save()
            except Exception, e:
                return render_to_response('lasso_labelprinting/addresses.html', {'global_errors':[_('Unable to convert document: %(error)s') % {'error': str(e)}]}, context_instance=template.RequestContext(request))

        finally:
            try:
                os.unlink(csvpath)
            except:
                pass
            try:
                os.unlink(path)
            except:
                pass

        messages.append(_("Uploaded addresses"))

    return render_to_response('lasso_labelprinting/addresses.html', {'messages':messages}, context_instance=template.RequestContext(request))
