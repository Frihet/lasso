from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Logs all used storage for the day'

    def handle(self, *args, **options):
        import lasso_warehandling.models
        for entry_row in lasso_warehandling.models.EntryRow.objects.all():
            logs = entry_row.log()
            if logs:
                print "Logging storage for %s: %s" % (entry_row, ','.join("%s: %s" % (log.date, log.units_left) for log in logs))
