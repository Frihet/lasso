#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, csv, os.path, re, datetime

def filewalk(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            yield os.path.join(root, f)

entry_re = re.compile(r"Ein.*lagerung.*\.csv")
withdrawal_re = re.compile(r"Lieferscheine.*\.csv")

customers = {}

def value_to_date(value):
    try:
        if '/' in value:
            parts = [int(x) for x in value.strip().split('/')]
            return datetime.date(parts[2], parts[0], parts[1])
        else:
            # Don't ask me why; but this is how date formatting works in XLS documents...
            return datetime.date(1899, 12, 30) + datetime.timedelta(int(value.strip()), 0, 0)
    except:
        # Ok, no number neither, so ignore it!
        return None

for filename in filewalk('./'):
    if entry_re.search(filename) or withdrawal_re.search(filename):
        customer_id = filename.split(os.path.sep)[1]
        if customer_id not in customers:
            customers[customer_id] = {'entries': {}, 'withdrawals':{}}

    if entry_re.search(filename):
        header_transform = {"Warenwert": "product_value",
                            "Produkte Nr.": "product_nr",
                            "Temp. beim Eingang": "arrival_temperature",
                            "Äusseres Aussehen": "product_state",
                            #"Karton à ": "",
                            #"AP/ KG": "",
                            "Verzollungsdatum": "custom_handling_date",
                            "Firma": "customer",
                            "Gewicht netto": "nett_weight",
                            "Gewicht brutto": "gross_weight",
                            "Artikelbezeichnung": "product_description",
                            "Anzahl Karton": "units",
                            "Eingangsdatum": "arrival_date",
                            "Bemerkung zu Mängel": "comment",
                            "Haltbarkeitsdatum": "use_before",
                            "Lieferant": "transporter",
                            "Zollquittungs Nr.": "customs_receipt_nr",
                            "Zeugnis Nr.": "customs_testimony_nr"}
        month_transform = {"Januar": 1,
                           "Februar": 2,
                           "März": 3,
                           "April": 4,
                           "Mai": 5,
                           "Juni": 6,
                           "Juli": 7,
                           "August": 8,
                           "September": 9,
                           "Oktober": 10,
                           "November": 11,
                           "Dezember": 12}

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
                    header['entry_id'] = "%s-%s" % (row[6][1:], row[4]) # Ignoring company id row[7]
                    if '.' not in header['entry_id']:
                        header['entry_id'] += '.00'
                elif row[0] != '':
                    value = row[3]
                    if row[0].endswith('datum'):
                        value = value_to_date(value)
                    name = row[0]
                    if name in header_transform:
                        name = header_transform[name]
                        header[name] = value
            elif mode[-1] == 'comment':
                if row[3] == '':
                    del mode[-1]
                else:
                    header['Bemerkung'] += '\n' + row[3]
            elif mode[-1] == 'months':
                if row[0] == 'Monat:':
                    month = month_transform[row[1].strip()]
                    months[month] = {}
                    mode.append('month')
            elif mode[-1] == 'month':
                if row[0] == 'Auslagerung':
                    del mode[-1]
                elif row[0] == 'Ein- und Auslagerung:':
                    assert 'price_per_kilo_per_entry' not in header
                    header['price_per_kilo_per_entry'] = row[3]
                elif row[0] == 'Lagergeld:':
                    months[month]['storage_price'] = row[3]
        if header['customer']:
            if 'name' not in customers[customer_id]:
                customers[customer_id]['name'] = header['customer'].split(',')[0]
            if 'address' not in customers[customer_id]:
                customers[customer_id]['address'] = header['customer'].replace(',', '\n')
        entry_id, entry_row_id = header['entry_id'].split('.')
        if entry_id not in customers[customer_id]['entries']:
            customers[customer_id]['entries'][entry_id] = {'header': {}, 'rows': {}}
        entry = customers[customer_id]['entries'][entry_id]
        if 'price_per_kilo_per_entry' in entry['header']:
            assert entry['header']['price_per_kilo_per_entry'] == header['price_per_kilo_per_entry']
        elif header.get('price_per_kilo_per_entry', '') != "":
            entry['header']['price_per_kilo_per_entry'] = header['price_per_kilo_per_entry']
        del header['price_per_kilo_per_entry']
        if 'arrival_date' in entry['header']:
            assert entry['header']['arrival_date'] == header['arrival_date']
        elif header.get('arrival_date', '') != "":
            entry['header']['arrival_date'] = header['arrival_date']
        del header['arrival_date']
        entry['rows'][entry_row_id] = {'header': header, 'months': months}

    elif withdrawal_re.search(filename):
        f = list(csv.reader(open(filename), dialect="excel"))

        # Read header:
        header = {}
        rows = []

        assert f[10][0] == 'LF Nr.'
        assert f[32][0] == 'Stock'

        header['withdrawal_id'] = f[10][1]
        header['reference_nr'] = f[15][3]
        header['responsible'] = f[17][3]
        header['place_of_departure'] = f[14][0]

        header['insurance'] = f[22][3]
        header['transport_condition'] = f[23][3]
        header['transport_nr'] = f[24][3]
        header['order_nr'] = f[25][1];

        header['destination_address'] = f[14][5] + '\n' + f[15][5] + '\n' + f[16][5] + '\n' + f[17][5]

        header['withdrawal_date'] = value_to_date(f[19][8])
        header['arrival_date'] = value_to_date(f[20][8])
        header['vehicle_type'] = f[22][8]
        header['opening_hours'] = f[24][8]
        header['transporter'] = f[27][5]
        header['comment'] = f[25][8]

        header['customer_name'] = f[27][0]
        header['customer_address'] = "%s\n%s\n%s" % (f[27][0], f[28][0], f[29][0])

        row_nr = 33
        while f[row_nr][0] != 'CONFIRMATION DE RECEPTION DES MARCHANDISES':
            row_nr += 1
        row_max = row_nr - 4

        for row_nr in xrange(33, row_max, 2):
            if f[row_nr][0] == '':
                break
            row = {}
            row['entry_row_id'] = "%s-%s" % (header['arrival_date'].year, f[row_nr][0])
            row['units'] = f[row_nr][7]
            row['origin'] = f[row_nr][6]
            rows.append(row)

        if header['customer_name']:
            customers[customer_id]['name'] = header['customer_name']
        if header['customer_address']:
            customers[customer_id]['address'] = header['customer_address']
        customers[customer_id]['withdrawals'][header['withdrawal_id']] = {'header': header, 'rows': rows}


# More integrity checks and intra-structure mangling:

for name, customer in customers.iteritems():
    for withdrawal_id, withdrawal in customer['withdrawals'].iteritems():
        for row in withdrawal['rows']:
            entry_id, entry_row_id = row['entry_row_id'].split('.')
            assert entry_id in customer['entries']
            assert entry_row_id in customer['entries'][entry_id]['rows']
            entry_row = customer['entries'][entry_id]['rows'][entry_row_id]
            if 'origin' in entry_row['header']:
                assert entry_row['header']['origin'] == row['origin']
            else:
                entry_row['header']['origin'] = row['origin']
            del row['origin']

for name, customer in customers.iteritems():
    print "%s" % (name,)
    for name, value in customer.iteritems():
        if name in ('entries', 'withdrawals'): continue
        print "    %s: %s" % (name, str(value).replace('\n', '\n        '))

    print

    print "    Entries"
    for entry_id, entry in customer['entries'].iteritems():
        print "        %s" % (entry_id,)
        
#        continue
        for name, value in entry['header'].iteritems():
            print "            %s: %s" % (name, str(value).replace('\n', '\n                        '))
        
        print

        for entry_row_id, entry_row in entry['rows'].iteritems():
            print "            %s" % (entry_row_id,)

            for name, value in entry_row['header'].iteritems():
                print "                %s: %s" % (name, str(value).replace('\n', '\n                        '))

            print

            for month_name, values in entry_row['months'].iteritems():
               print "                %s" % (month_name,)
               for name, value in values.iteritems():
                   print "                    %s: %s" % (name, str(value).replace('\n', '\n                        '))

    print "    Withdrawals"
    for withdrawal_id, withdrawal in customer['withdrawals'].iteritems():
        print "        %s" % (withdrawal_id,)

#        continue

        for name, value in withdrawal['header'].iteritems():
            print "            %s: %s" % (name, str(value).replace('\n', '\n                    '))

        print

        for row in withdrawal['rows']:
            for name, value in row.iteritems():
                print "                %s: %s" % (name, str(value).replace('\n', '\n                    '))
            print "            ----------------"
