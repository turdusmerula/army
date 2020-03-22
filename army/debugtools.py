import sys, traceback
from log import log

def print_stack():
    if log.level==10:
    #        traceback.print_stack()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=sys.stdout)
