import semantic_version

class VersionException(Exception):
    def __init__(self, message):
        self.message = message

class Version(semantic_version.Version):
    def __init__(self, value):
        if isinstance(value, Version):
            super(Version, self).__init__(str(value))
        elif isinstance(value, str):
            super(Version, self).__init__(value)
        else:
            raise VersionException(f"Invalid version {value}")

class VersionRange(semantic_version.SimpleSpec):
    def __init__(self, value, versions=[]):
        self._versions = versions
        self._latest = None
        
        if value=="latest":
            if len(self._versions)==0:
                raise VersionException("latest: no version provided")
            self._latest = f"=={self._max_version()}"
            super(VersionRange, self).__init__(self._latest)
        else:
            super(VersionRange, self).__init__(value)

    def _max_version(self):
        max = Version(self._versions[0])
        for version in self._versions:
            if Version(version)>max:
                max = Version(version)
        return max

    def match(self, value):
        if isinstance(value, Version):
            return super(VersionRange, self).match(value)
        else:
            return super(VersionRange, self).match(Version(value))

    def add_version(self, value):
        self._versions.append(value)
        self._latest = f"=={self._max_version()}"
        super(VersionRange, self).__init__(self._latest)
