class ArchException(Exception):
    def __init__(self, message):
        self.message = message

class Arch(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
    
    def name(self):
        return self._name 
    
    def parent(self):
        return self._parent



