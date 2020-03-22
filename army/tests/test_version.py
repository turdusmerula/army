import sys
import os
sys.path.append(os.path.dirname(__name__))

from version import Version

print(Version("1"))
print(Version("1.2"))
print(Version("1.2.3"))
print(Version("1.2.3-b"))

try:
    print(Version(""))
except Exception as e:
    print(format(e))

try:
    print(Version("1.1.1.1"))
except Exception as e:
    print(format(e))

try:
    print(Version("1.a"))
except Exception as e:
    print(format(e))

values = [
    ["1", "1"],
    ["1", "2"],
    ["2", "1"],
    
    ["2.0", "2.0"],
    ["2.0", "1.9"],
    ["1.9", "2.0"],

    ["2.0.0", "2.0.0"],
    ["2.0.0", "1.9.9"],
    ["1.9.9", "2.0.0"],

    ["2.0.0-aa", "2.0.0-aa"],
    ["2.0.0-aa", "2.0.0-ab"],
    ["2.0.0-ab", "2.0.0-aa"],
]

for v in values:
    vl = Version(v[0])
    vr = Version(v[1])
    print(f"{vl}<{vr}: {vl<vr}")
    print(f"{vl}<={vr}: {vl<=vr}")
    print(f"{vl}>{vr}: {vl>vr}")
    print(f"{vl}>={vr}: {vl>=vr}")
    print(f"{vl}=={vr}: {vl==vr}")
    print("---")
