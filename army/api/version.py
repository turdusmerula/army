import semantic_version

class VersionException(Exception):
    def __init__(self, message):
        self.message = message

class Version(semantic_version.Version):
    def __init__(self, value):
        if isinstance(value, Version):
            try:
                super(Version, self).__init__(str(value))
            except Exception as e:
                raise VersionException(str(e))
        elif isinstance(value, str):
            try:
                super(Version, self).__init__(value)
            except Exception as e:
                raise VersionException(str(e))            
        else:
            raise VersionException(f"Invalid version {value}")


class VersionRange(object):
    def __init__(self, versions=[]):
        self._versions = []
        for version in versions:
            if isinstance(version, Version):
                self._versions.append(version)
            else:
                self._versions.append(Version(version))
            

    def max(self):
        max = self._versions[0]
        for version in self._versions:
            if version>max:
                max = version
        return Version(max)

    def filter(self, range):
        if range=="latest":
            return [self.max()]
        
        s = semantic_version.SimpleSpec(range)
        versions = []
        for version in s.filter(self._versions):
            versions.append(Version(version))
        return versions

    def select(self, range):
        if range=="latest":
            return self.max()

        s = semantic_version.SimpleSpec(range)
        return s.select(self._versions)

    def __contains__(self, range):
        return self.select(range) is not None

    def __getitem__(self, range):
        return self.select(str(range))

    def clear_versions(self, value):
        self._versions.clear()

    def add_version(self, value):
        self._versions.append(value)

    def __str__(self):
        return str(self)