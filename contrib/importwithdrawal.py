#! /usr/bin/python

import sys, csv

filename = sys.argv[1]

f = list(csv.reader(open(filename), dialect="excel"))

# Read header:
header = {}
rows = []

assert f[10][0] == 'LF Nr.'
assert f[32][0] == 'Stock'

header['reference_nr'] = f[15][3]
header['responsible'] = f[17][3]
header['place_of_departure'] = f[14][0]

header['insurance'] = f[22][3]
header['transport_condition'] = f[23][3]
header['transport_nr'] = f[24][3]
header['order_nr'] = f[25][1];

header['destination_address'] = f[14][5] + '\n' + f[15][5] + '\n' + f[16][5] + '\n' + f[17][5]

header['withdrawal_date'] = f[19][8]
header['arrival_date'] = f[20][8]
header['vehicle_type'] = f[22][8]
header['opening_hours'] = f[24][8]
header['transporter'] = f[27][5]
header['comment'] = f[25][8]

header['customer_name'] = f[27][0]


row_nr = 33
while f[row_nr][0] != 'CONFIRMATION DE RECEPTION DES MARCHANDISES':
    row_nr += 1
row_max = row_nr - 4

for row_nr in xrange(33, row_max, 2):
    if f[row_nr][0] == '':
        break
    row = {}
    row['entry_row_id'] = f[row_nr][0]
    row['units'] = f[row_nr][7]
    row['origin'] = f[row_nr][6]
    rows.append(row)

for name, value in header.iteritems():
    print "%s: %s" % (name, value)

print

for row in rows:
    for name, value in row.iteritems():
        print "    %s: %s" % (name, value)
    print "----------------"
