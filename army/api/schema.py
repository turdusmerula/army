from army.api.version import Version, VersionRange
from army.api.debugtools import print_stack
from army.api.log import log

class SchemaException(Exception):
    def __init__(self, message):
        self.message = message


class Schema(object):
    
    def __init__(self, data, schema={}):
        self._data = data
        self._schema = schema
        
    def check(self):
        for item in self._data:
            
            if item not in self._schema:
                raise SchemaException(f"{item}: unknown item")
            else:
                self._schema[item].check(self._data[item])

class ValidatorException(Exception):
    def __init__(self, message):
        self.message = message
                
class Validator(object):
    def __init__(self):
        pass
    
    def check(self, value):
        pass
    
class Variant(Validator):
    def __init__(self):
        super(Variant, self).__init__()
    
    def check(self, value):
        pass

class Int(Validator):
    def __init__(self):
        super(Int, self).__init__()
    
    def check(self, value):
        raise "not implemented"

class String(Validator):
    def __init__(self):
        super(String, self).__init__()
    
    def check(self, value):
        if not isinstance(value, str):
            raise ValidatorException(f"'{value}' is not a valid string")

class VersionRangeString(Validator):
    def __init__(self):
        super(VersionRangeString, self).__init__()
    
    def check(self, value):
        try:
            # provide at least one version to resolve 'latest'
            version = VersionRange(value, versions=["0.0.0"])
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise ValidatorException(f"'{value}' is not a valid version range")

class VersionString(Validator):
    def __init__(self):
        super(VersionString, self).__init__()
    
    def check(self, value):
        try:
            version = Version(value)
        except Exception as e:
            raise ValidatorException(f"'{value}' is not a valid version")

class Optional(Validator):
    def __init__(self, schema):
        super(Optional, self).__init__()
        self._schema = schema
        
    def check(self, value):
        if value is not None:
            self._schema.check(value)

class PackageString(Validator):
    def __init__(self):
        super(PackageString, self).__init__()
    
    def check(self, value):
        if not isinstance(value, str):
            raise ValidatorException(f"'{value}' is not a valid package name")
        # TODO: validate name
        
class Array(Validator):
    def __init__(self, schema):
        super(Array, self).__init__()
        self._schema = schema
    
    def check(self, values):
        if not isinstance(values, list):
            raise ValidatorException(f"'{values}' is not a valid array list")
        for value in values:
            self._schema.check(value)

class Dict(Validator):
    def __init__(self, schema):
        super(Dict, self).__init__()
        self._schema = schema
    
    def check(self, values):
        if not isinstance(values, dict):
            raise ValidatorException(f"'{values}' is not a valid dictionnary")
        for value in values:
            if value not in self._schema:
                raise SchemaException(f"{value}: unknown item")
            else:
                self._schema[value].check(values[value])

class VariableDict(Validator):
    def __init__(self, schemakey, schemavalue):
        super(VariableDict, self).__init__()
        self._schemakey = schemakey
        self._schemavalue = schemavalue
    
    def check(self, values):
        if not isinstance(values, dict):
            raise ValidatorException(f"'{values}' is not a valid dictionnary")
        for value in values:
            self._schemakey.check(value)
            self._schemavalue.check(values[value])
