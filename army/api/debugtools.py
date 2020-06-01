import sys, traceback
from army.api.log import log

def print_stack():
    if log.level==10:
#        traceback.print_stack()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=sys.stderr, limit=None)

def print_callstack():
    if log.level==10:
        for line in traceback.format_stack()[:-2]:
            print(line.strip())
