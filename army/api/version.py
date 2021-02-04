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

# class VersionRange(semantic_version.SimpleSpec):
#     def __init__(self, value, versions=[]):
#         self._versions = versions
#         self._latest = None
#         
#         if value=="latest":
#             if len(self._versions)==0:
#                 raise VersionException("latest: no version provided")
#             self._latest = f"=={self.max()}"
#             super(VersionRange, self).__init__(self._latest)
#         else:
#             super(VersionRange, self).__init__(value)
# 
#     def max(self):
#         max = Version(self._versions[0])
#         for version in self._versions:
#             if Version(version)>max:
#                 max = Version(version)
#         return max
# 
#     def match(self, value):
#         if isinstance(value, Version):
#             return super(VersionRange, self).match(value)
#         else:
#             return super(VersionRange, self).match(Version(value))
# 
#     def clear_versions(self, value):
#         self._versions.clear()
#         self._latest = None
# 
#     def add_version(self, value):
#         self._versions.append(value)
#         self._latest = f"=={self.max()}"
#         super(VersionRange, self).__init__(self._latest)

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
        return max

    def filter(self, range):
        if range=="latest":
            return self.max()
        
        s = semantic_version.SimpleSpec(range)
        versions = []
        for version in s.filter(self._versions):
            versions.append(version)
        return versions

    def select(self, range):
        if range=="latest":
            return self.max()

        s = semantic_version.SimpleSpec(range)
        return s.select(self._versions)

    def __contains__(self, range):
        return self.select(range) is not None

    def __getitem__(self, range):
        return self.select(range)

    def clear_versions(self, value):
        self._versions.clear()

    def add_version(self, value):
        self._versions.append(value)
