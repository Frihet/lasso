# -*- coding: utf-8 -*-

import datetime
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from lasso.utils import *

class Command(BaseCommand):
    args = ''

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    default=False,
                    dest='dry-run',
                    help='Run without changing the database'),
        make_option('--assert',
                    action='append',
                    type='string',
                    default=[],
                    dest='assert',
                    help='Fail if certain types of assertions fail (type can be "merge", "integrity", "format", "generic"...)'),
        )
    help = 'Imports FLS CSV formatted data'

    def handle(self, *args, **options):
        import lasso.lasso_warehandling.models
        import lasso.lasso_warehouse.models
        import lasso.lasso_customer.models

	import sys, csv, os.path, re, datetime

	def filewalk(path):
	    for root, dirs, files in os.walk(path):
		for f in files:
		    yield os.path.join(root, f)

	entry_re = re.compile(r"Ein.*lagerung.*\.csv")
	withdrawal_re = re.compile(r"Lieferscheine.*\.csv")

	customers = {}
        transporters = {}

	errors = []
	
        def signal_error(msg, etype='generic'):
	    if etype in options.get('assert', ''):
		raise AssertionError(msg)
	    errors.append(msg)

	def myassert(expr, msg, etype):
	    if not expr:
		signal_error(msg, etype)

	def assert_integrity(expr, msg):
	    myassert(expr, msg, "integrity")

	def assert_format_constant(var, value):
	    if var != value:
		signal_error("%s not found in file" % (value,), etype='format')

	def mergeset(dct, index, value):
	    if value:
		if index not in dct:
		    dct[index] = value
		else:
		    if dct[index] != value:
			signal_error("Trying to merge different values for %s: %s != %s" % (index, repr(value), repr(dct[index])), "merge")

	def movemerge(srcdct, srcindex, dstdct, dstindex):
	    if srcindex in srcdct:
		mergeset(dstdct, dstindex, srcdct[srcindex])

        def obj_from_dict(model, dct):
            obj = model()
            header = dct
            if 'header' in header:
                header = header['header']
            for key, value in header.iteritems():
                setattr(obj, key, value)
            dct['obj'] = obj
            return obj

	def value_to_date(value):
            value = value.strip()
            if value in ("", "x", "X"): return None
	    try:
		if '/' in value:
		    parts = [int(x) for x in value.strip().split('/')]
		    return datetime.date(parts[2], parts[0], parts[1])
		else:
		    # Don't ask me why; but this is how date formatting works in XLS documents...
		    return datetime.date(1899, 12, 30) + datetime.timedelta(int(value.strip()), 0, 0)
	    except:
                signal_error("'%s' is not a date" % (value,), "valueformat")
		return None

	def value_to_int(value):
            value = value.strip()
            if value in ("", "x", "X"): return None
	    try:
                return int(value)
	    except:
                signal_error("'%s' is not an integer" % (value,), "valueformat")
		return None

	def value_to_float(origvalue):
            value = origvalue.strip()
            if value in ("", "x", "X"): return None
            value = value.replace(" ", "").replace("°", ".").replace(",", ".").replace("'", "")
            if value.startswith("ca."):
                value = value[3:]
            if value.startswith("CHF"):
                value = value[3:]
            if value.startswith("Minus"):
                value = "-" + value[5:]
            if value.endswith("C"):
                value = value[:-1]
            if value.endswith("."):
                value = value[:-1]
	    try:
                return float(value)
	    except:
                signal_error("'%s' is not a float" % (origvalue,), "valueformat")
		return None

        def value_to_bool(origvalue):
            return origvalue.strip().lower() in ('i.o', 'durch uns/par nous')

	for filename in filewalk('./'):
	    if entry_re.search(filename) or withdrawal_re.search(filename):
		customer_id = filename.split(os.path.sep)[1]
		if customer_id not in customers:
		    customers[customer_id] = {'header': {}, 'entries': {}, 'withdrawals':{}}

	    if entry_re.search(filename):
		header_transform = {"Warenwert": ("product_value", value_to_float),
				    "Produkte Nr.": ("product_nr", str),
				    "Temp. beim Eingang": ("arrival_temperature", value_to_float),
				    "Äusseres Aussehen": ("product_state", value_to_bool),
				    #"Karton à ": ("", str),
				    #"AP/ KG": ("", str),
				    "Verzollungsdatum": ("custom_handling_date", value_to_date),
				    "Firma": ("customer", str),
				    "Gewicht netto": ("nett_weight", value_to_float),
				    "Gewicht brutto": ("gross_weight", value_to_float),
				    "Artikelbezeichnung": ("product_description", str),
				    "Anzahl Karton": ("units", value_to_int),
				    "Eingangsdatum": ("arrival_date", value_to_date),
				    "Bemerkung zu Mängel": ("comment", str),
				    "Haltbarkeitsdatum": ("use_before", value_to_date),
				    "Lieferant": ("transporter", str),
				    "Zollquittungs Nr.": ("customs_receipt_nr", str),
				    "Zeugnis Nr.": ("customs_testimony_nr", str)}
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
			    name = row[0]
			    if name in header_transform:
				name, t = header_transform[name]
				header[name] = t(row[3])
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
			    mergeset(header, 'price_per_kilo_per_entry', row[3])
			elif row[0] == 'Lagergeld:':
			    months[month]['price_per_kilo_per_day'] = row[3]
                if header['units'] != None:
                    if header['customer']:
                        mergeset(customers[customer_id]['header'], 'name', header['customer'].split(',')[0].strip())
                        mergeset(customers[customer_id]['header'], 'address', '\n'.join(item.strip() for item in header['customer'].split(',')))
                    entry_id, entry_row_id = header['entry_id'].split('.')
                    if entry_id not in customers[customer_id]['entries']:
                        customers[customer_id]['entries'][entry_id] = {'header': {}, 'rows': {}}
                    entry = customers[customer_id]['entries'][entry_id]
                    movemerge(header, 'price_per_kilo_per_entry', entry['header'], 'price_per_kilo_per_entry')
                    movemerge(header, 'arrival_date', entry['header'], 'arrival_date')
                    movemerge(header, 'transporter', entry['header'], 'transporter')
                    entry['rows'][entry_row_id] = {'header': header, 'months': months}
                    if entry['header']['transporter']:
                        transporter = entry['header']['transporter']

                        address = ""
                        if ',' in transporter:
                            transporter, address = transporter.split(',', 1)
                            address = '\n'.join(item.strip() for item in address.split(","))
                            entry['header']['transporter'] = transporter

                        transporters[transporter] = {'header': {'name': transporter, 'address': address}}

	    elif withdrawal_re.search(filename):
		f = list(csv.reader(open(filename), dialect="excel"))

		# Read header:
		header = {}
		rows = []

		assert_format_constant(f[10][0], 'LF Nr.')
		assert_format_constant(f[32][0], 'Stock')

		header['withdrawal_id'] = f[10][1]
		header['reference_nr'] = f[15][3]
		header['responsible'] = f[17][3]
		header['place_of_departure'] = f[14][0]

		header['insurance'] = value_to_bool(f[22][3])
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
		    row['units'] = value_to_int(f[row_nr][7])
		    row['origin'] = f[row_nr][6]
		    rows.append(row)

                if header['transporter']:
                    address = ""
                    if ',' in header['transporter']:
                        header['transporter'], address = transporter.split(',', 1)
                        address = '\n'.join(item.strip() for item in address.split(","))
                    transporters[header['transporter']] = {'header': {'name': header['transporter'], 'address': address}}
		if header['customer_name']:
		    customers[customer_id]['name'] = header['customer_name']
		if header['customer_address']:
		    customers[customer_id]['address'] = header['customer_address']
		customers[customer_id]['withdrawals'][header['withdrawal_id']] = {'header': header, 'rows': rows}


	# More integrity checks and intra-structure mangling:

	for name, customer in customers.iteritems():
            last_price_per_kilo_per_day_month = 0
            last_price_per_kilo_per_day = 0.0
            last_price_per_kilo_per_entry_date = None
            last_price_per_kilo_per_entry = 0.0
            for entry_id, entry in customer['entries'].iteritems():
                assert_integrity('arrival_date' in entry['header'], "Arrival date not in entry %s for %s" % (entry_id, name))
                if ('price_per_kilo_per_entry' in entry['header']
                    and (last_price_per_kilo_per_entry_date is None
                         or (    'arrival_date' in entry['header']
                             and entry['header']['arrival_date'] > last_price_per_kilo_per_entry_date))):
                    last_price_per_kilo_per_entry_date = entry['header']['arrival_date']
                    last_price_per_kilo_per_entry = entry['header']['price_per_kilo_per_entry']
                for entry_row_id, entry_row in entry['rows'].iteritems():
                    for month_name, values in entry_row['months'].iteritems():
                        if month_name > last_price_per_kilo_per_day_month and 'price_per_kilo_per_day' in values:
                            last_price_per_kilo_per_day_month = month_name
                            last_price_per_kilo_per_day = values['price_per_kilo_per_day']
            if last_price_per_kilo_per_day_month > 0:
                customer['header']['price_per_kilo_per_day'] = last_price_per_kilo_per_day
            if last_price_per_kilo_per_entry_date is not None:
                customer['header']['price_per_kilo_per_entry'] = last_price_per_kilo_per_entry
	    for withdrawal_id, withdrawal in customer['withdrawals'].iteritems():
		for row in withdrawal['rows']:
		    entry_id, entry_row_id = row['entry_row_id'].split('.')
		    assert_integrity(entry_id in customer['entries'],
				     "Entry %s does not exist" % (entry_id,))
		    assert_integrity(entry_row_id in customer['entries'][entry_id]['rows'],
				     "Entry row %s does not exist in entry %s" %(entry_row_id, entry_id))
		    entry_row = customer['entries'][entry_id]['rows'][entry_row_id]
		    movemerge(row, 'origin', entry_row['header'], 'origin')
		    movemerge(withdrawal['header'], 'insurance', entry['header'], 'insurance')

	if errors:
	    print "==================================={ ERRORS }==================================="
	    for error in errors:
		print error
	    print "================================================================================"


	if not options.get('dry-run', False):
	    # Create data objects
	    for name, transporter in transporters.iteritems():
                transporter_obj = obj_from_dict(lasso.lasso_customer.models.Transporter, transporter)
                transporter_obj.save()

	    for name, customer in customers.iteritems():
                customer['header'].setdefault('price_per_kilo_per_day', 0)
                customer['header'].setdefault('price_per_kilo_per_entry', 0)
                customer['header'].setdefault('price_per_kilo_per_withdrawal', 0)
                customer['header'].setdefault('price_per_unit_per_day', 0)
                customer['header'].setdefault('price_per_unit_per_entry', 0)
                customer['header'].setdefault('price_per_unit_per_withdrawal', 0)
                customer_obj = obj_from_dict(lasso.lasso_customer.models.Customer, customer)
                customer_obj.save()

		for entry_id, entry in customer['entries'].iteritems():
                    transporter_id = entry['header']['transporter']
                    transporter_obj = transporters[transporter_id]['obj']
                    del entry['header']['transporter']
                    entry_obj = obj_from_dict(lasso.lasso_warehandling.models.Entry, entry)
                    entry_obj.transporter = transporter_obj
                    entry_obj.customer = customer_obj
                    entry_obj.save()

		    for entry_row_id, entry_row in entry['rows'].iteritems():
                        entry_row_obj = obj_from_dict(lasso.lasso_warehandling.models.EntryRow, entry_row)
                        entry_row_obj.entry = entry_obj
                        entry_row_obj.save()

                        entry_row['next_storagelog'] = entry['header']['arrival_date']

			#for month_name, values in entry_row['months'].iteritems():
                        #    for name, value in values.iteritems():
                        #        pass

                withdrawals =  customer['withdrawals'].values()
                withdrawals.sort(lambda a, b: cmp(a['header']['withdrawal_date'], b['header']['withdrawal_date']))

		for withdrawal in withdrawals:
                    transporter_id = withdrawal['header']['transporter']
                    transporter_obj = transporters[transporter_id]['obj']
                    del withdrawal['header']['transporter']
                    withdrawal_obj = obj_from_dict(lasso.lasso_warehandling.models.Withdrawal, withdrawal)
                    withdrawal_obj.transporter = transporter_obj
                    withdrawal_obj.customer = customer_obj
                    withdrawal_obj.save()

		    for withdrawal_row in withdrawal['rows']:
                        entry_id, entry_row_id = withdrawal_row['entry_row_id'].split('.')
                        entry = customer['entries'][entry_id]
                        entry_row = entry['rows'][entry_row_id]

                        withdrawal_row_obj = obj_from_dict(lasso.lasso_warehandling.models.WithdrawalRow, withdrawal_row)
                        withdrawal_row_obj.withdrawal = withdrawal_obj
                        withdrawal_row_obj.entry_row = entry_row['obj']
                        withdrawal_row_obj.save()
                        
                        for storage_date in xdaterange(entry_row['next_storagelog'], withdrawal_obj.withdrawal_date + datetime.timedelta(1)):
                            log_item = lasso.lasso_warehandling.models.StorageLog()
                            log_item.date = storage_date
                            log_item.entry_row = entry_row['obj']
                            log_item.price_per_kilo_per_day = entry_row['months'][storage_date.month]['price_per_kilo_per_day']
                            log_item.save()
                        entry_row['next_storagelog'] = withdrawal_obj.withdrawal_date + datetime.timedelta(1)

		for entry_id, entry in customer['entries'].iteritems():
		    for entry_row_id, entry_row in entry['rows'].iteritems():
                        tomorrow =  datetime.date.today() + datetime.timedelta(1)
                        for storage_date in xdaterange(entry_row['next_storagelog'], tomorrow):
                            log_item = lasso.lasso_warehandling.models.StorageLog()
                            log_item.date = storage_date
                            log_item.entry_row = entry_row['obj']
                            log_item.price_per_kilo_per_day = entry_row['months'][storage_date.month]['price_per_kilo_per_day']
                            log_item.save()
                        entry_row['next_storagelog'] = tomorrow

	else:
	    for name, transporter in transporters.iteritems():
		print "Transporter: %s" % (name,)
		for name, value in transporter['header'].iteritems():
		    print "    %s: %s" % (name, str(value).replace('\n', '\n        '))

		print

	    for name, customer in customers.iteritems():
		print "Customer: %s" % (name,)
		for name, value in customer['header'].iteritems():
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

		    for withdrawal_row in withdrawal['rows']:
			for name, value in withdrawal_row.iteritems():
			    print "                %s: %s" % (name, str(value).replace('\n', '\n                    '))
			print "            ----------------"
