from army.api.version import Version

class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package(object):
    def __init__(self, name, description, version, repository):
        self._name = name
        self._description = description
        self._version = Version(version)
        self._repository = repository
        
    def name(self):
        return self._name
    
    def description(self):
        return self._description
    
    def version(self):
        return self._version

    def repository(self):
        return self._repository
    
    def load(self):
        pass
    
    def dependencies(self):
        return []

    def __repr__(self):
        return f"{self._name}:{self._version}"