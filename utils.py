import datetime

def xdaterange(d1, d2):
    return (d1 + datetime.timedelta(x)
            for x in xrange(0, (d2 - d1).days))
