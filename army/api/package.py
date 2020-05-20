from army.api.version import Version

class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package(object):
    def __init__(self, name, description, version):
        self._name = name
        self._description = description
        self._version = Version(version)
    
    def name(self):
        return self._name
    
    def description(self):
        return self._description
    
    def version(self):
        return self._version

    def __repr__(self):
        return f"{self._name}:{self._version}"
