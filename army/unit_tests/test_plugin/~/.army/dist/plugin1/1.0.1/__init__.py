from army.api.log import log
import os
import sys

# add plugin to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# show passed plugin configuration
log.debug(config)

import plugin1.group
import plugin1.command1
import plugin1.command2
