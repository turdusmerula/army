import sys
import os
#sys.path.append(os.path.dirname(__name__))

from army.api.version import Version, VersionRange

Version("1.0.0") in VersionRange("==1.0.0")
Version("1.0.1") in VersionRange("~1.0.0")
Version("1.0.0") in VersionRange("latest", ["0.0.1", "0.0.2", "1.0.0"])

print(VersionRange("==1.0.0").match(Version("1.1.0")))
print(str(VersionRange("~1.0.0")))
print(VersionRange("~1.0.0"))