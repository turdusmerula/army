import sys, traceback
from log import log

def print_stack():
    if log.level==10:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback is None:
            # print_stack called outside of an exception context
            pass
            
#             print(dir(sys._getframe()))
#            stack = traceback.extract_stack(sys._getframe().f_back, limit=None)
#             print(stack)
        else:
            traceback.print_tb(exc_traceback, file=sys.stdout)
        
