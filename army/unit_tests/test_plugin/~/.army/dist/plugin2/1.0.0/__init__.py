import sys
import os

def load_plugin():
    # add plugin to python path
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    
    import plugin1.command1
    import plugin1.command2
    
