import settings

class ExcWare(object):
    def process_exception(self, request, exception):
        if settings.DEBUG_IN_TERMINAL:
            import pdb, sys, traceback
            sys.last_traceback = sys.exc_info()[2]
            print "================================================================================"
            traceback.print_exc()
            pdb.pm()
        return None
