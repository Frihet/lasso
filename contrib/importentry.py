#! /usr/bin/python

import sys, csv

filename = sys.argv[1]

f = csv.reader(open(filename), dialect="excel")

# Read header:
header = {}
months = {}
month = None

mode = ['header']
for row in f:
    if mode[-1] == 'header':
        if row[0] == 'Auslagerung':
            mode[-1] = 'months'
        elif row[0] == 'Bemerkung':
            mode.append('comment')
            header[row[0]] = row[3]
        elif row[2] == 'Lager Nr.:':
            header['entry_id'] = "%s-%s-%s" % (row[7], row[6][1:], row[4])
        elif row[0] != '':
            header[row[0]] = row[3]
    elif mode[-1] == 'comment':
        if row[3] == '':
            del mode[-1]
        else:
            header['Bemerkung'] += '\n' + row[3]
    elif mode[-1] == 'months':
        if row[0] == 'Monat:':
            month = row[1]
            months[month] = {}
            mode.append('month')
    elif mode[-1] == 'month':
        if row[0] == 'Auslagerung':
            del mode[-1]
        elif row[0] == 'Ein- und Auslagerung:':
            months[month]['entry_price'] = row[3]
        elif row[0] == 'Lagergeld:':
            months[month]['storage_price'] = row[3]

for name, value in header.iteritems():
    print "%s: %s" % (name, value)

print

for month_name, values in months.iteritems():
    print month_name
    print "----------------"
    for name, value in values.iteritems():
        print "    %s: %s" % (name, value)
