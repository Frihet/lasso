# -*- coding: utf-8 -*-
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

def zprint(text,copies, port=9100, lmarg=50, tmarg=25, ip="10.0.10.201"):
    # Ok, this printer has a wierd character encoding...
    text = text.translate('\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\x8f\x92\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\x9d\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4}{\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7|\xf9\xfa\xfb\xfc\xfd\xfe\xff')

    data = ''
    for job in xrange(0, copies):
        lheight = 40
        lpos = tmarg
        data += "^XA\n"
        for line in text.split("\n"):
            data += "^CI4\n"
            data += "^FO%s,%s^A0N,40,40^FD%s^FS\n" % (lmarg, lpos, line.strip())
            lpos += lheight

        data += "^FO%s,200\n" % (lmarg,)
        data += "^BQN,50,200,N,N,N\n"
        data +="^FD>;%s^FS\n" % (text.replace("\n", "; "),)

        data += "^XZ\n"

    fp = socket.create_connection((ip, port))
    try:
        fp.send("~HS\n")
        pstat = fp.recv(128).strip().split(",")
        paper_out = pstat[1]
        paused = pstat[2]
        if paper_out != "0":
            raise Exception("Out of paper")
        if paused != "0":
            raise Exception("Paused")
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

            f = os.fdopen(f, "w")
            try:
                for chunk in request.FILES['labellistfile'].chunks():
                    f.write(chunk)
            finally:
                f.close()

            converter = lasso.contrib.DocumentConverter.DocumentConverter()
            converter.convert(path, csvpath)

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

                        zprint(("%(name)s (%(customer_nr)s)\n%(street)s\n%(zip)s %(platform)s %(city)s" % addr.as_dict).encode('latin-1'), 1)

        finally:
            try:
                os.unlink(csvpath)
            except:
                pass
            try:
                os.unlink(path)
            except:
                pass

        messages.append("Printed labels")

    return render_to_response('lasso_labelprinting/print_labels.html', {'messages':messages}, context_instance=template.RequestContext(request))


@staff_member_required
def addresses(request):
    messages = []
    if 'addressfile' in request.FILES:

        f, path = tempfile.mkstemp(request.FILES['addressfile'].name)
        csvpath = path + ".csv"
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

        finally:
            try:
                os.unlink(csvpath)
            except:
                pass
            try:
                os.unlink(path)
            except:
                pass

        messages.append("Uploaded addresses")

    return render_to_response('lasso_labelprinting/addresses.html', {'messages':messages}, context_instance=template.RequestContext(request))
