import logging

FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('console')
log.setLevel('ERROR') # default log mode warning

def get_log_level():
    if log.level==10:
        return "debug"
    elif log.level==20:
        return "info"
    elif log.level==30:
        return "warning"
    elif log.level==40:
        return "error"
    else:
        return "critical"
