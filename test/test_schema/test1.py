from schema import Schema, And, Use, Optional
from collections import namedtuple

# schema = Schema([{'name': str,
#                   'age':  Use(lambda n: 18 <= n <= 99, "invalid age"),
#                   Optional('gender'): str
#                   }])
# 
# data = [{'name': 'Sue', 'age': 20, 'gender': 'Squid', "aa": 10},
#         {'name': 'Sam', 'age': 42},
#         {'name': 'Sacha', 'age': 20, 'gender': 'KID'}]
# 
# try:
#     validated = schema.validate(data)
#     print(validated)
# except Exception as e:
#     print(type(e))
#     print(e.__dict__)
# 
#     if len(e.errors)==4:
#         print(f"{e.autos[1]} {e}")
#     else:
#         print(e)


schema = Schema(
    {
        'name': str,
        'version': str,
        Optional('arch'): str,
        Optional('dependencies'): [str]
    }
)

data = {
        'name': 'test',
        'version': '1.0.0',
        'arch': 'arm-m0',
        'dependencies': [
                'coucou',
            ]
    }

try:
    validated = schema.validate(data)
    print(validated)
except Exception as e:
    print(type(e))
    print(e.__dict__)
 
    if len(e.errors)==4:
        print(f"{e.autos[1]} {e}")
    else:
        print(e)

# package = namedtuple("Package", data)
# (**data)
# print(package.name)
# print(package)

class Package(namedtuple("Package", data)):
    pass
#     def __init__(self):
#         super(Package, self)(name="yy")

package = Package(**data)
print(package)