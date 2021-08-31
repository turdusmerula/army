from army.api.version import Version, VersionRange
from army.api.debugtools import print_stack
from army.api.log import log
from schema import Schema, SchemaError, Optional, Hook, And, Or, Regex, Const, _callable_str
# class SchemaException(Exception):
#     def __init__(self, message):
#         self.message = message
# 
# class ValidatorException(Exception):
#     def __init__(self, message, location=None):
#         if location is None:
#             self.message = message
#         else:
#             self.message = f"{location}: {message}"
# 
# 
def validate(data, schema, *args, **kwargs):
    from army.api.dict_file import Dict
    log.debug(f"validate: {data} with {schema}")

    s = Schema(schema, *args, **kwargs)
    if data is dict:
        s.validate(data)
    elif data is Dict:
        s.validate(data._data)
        

#     if schema in _validators
# #     _recursive_check(data, schema)
# 
# def _recursive_check(data, schema):
# #     print("---", data, schema)
#     if isinstance(schema, dict):
#         context = {}
#         
#         # check each item
#         for item in data:
#             # search for schema validating item
#             s = None
#             for key in schema:
#                 if isinstance(key, Validator):
#                     try:
#                         key.check(item)
#  
#                         # this key validates item
#                         if s is None:
#                             s = schema[key]
#                         else:
#                             raise SchemaException(f"{item}: inconsistent schema, multiple matches")
#                     except ValidatorException as e:
#                         pass
#                 else:
#                     if key in _validators:
#                         try:
#                             # key is a registered type, validate it
#                             _validators[key]().check(item)
#                             if s is None:
#                                 s = schema[key]
#                             else:
#                                 raise SchemaException(f"{item}: inconsistent schema, multiple matches")
#                         except ValidatorException as e:
#                             pass
#                     elif item==key:
#                         # item matches the key directly
#                         if s is None:
#                             s = schema[key]
#                         else:
#                             raise SchemaException(f"{item}: inconsistent schema, multiple matches")
#             
#             if s is None:
#                 raise ValidatorException(f"{item}: unknown item")
#             else:
#                 _recursive_check(data[item], s)
#         
#         # check for missing items
# #         for key in schema:
# #             for item in data:
# #                 if isinstance(key, Validator):
# #                     pass
# #                 else:
# #                     pass
# 
#     elif isinstance(schema, Validator):
#         schema.check(data)
#     else:
#         if schema in _validators:
#             _validators[schema]().check(data)
#         elif schema==data:
#             pass
#         else:
#             raise ValidatorException(f"{schema}: schema type not handled")
# 
# class Context():
#     def __init__(self, value):
#         self.value = value
# 
# class Validator(object):
#     def __init__(self):
#         pass
# 
#     def match(self, value):
#         """ check if value matches """
#         return False
# 
#     def check(self, context):
#         """ check consistency """
#         """ @raise if context is not consistent """
#         pass
# 
# class SingletonValidator(object):
#     def __init__(self):
#         super(SingletonValidator, self).__init__()
# 
#     def check(self, context):
#         if len(context)==0:
#             raise ValidatorException(f"missing value")
#         elif len(context)>1:
#             raise ValidatorException(f"expected one value, found {len(context)}")
#         else:
#             if self.match(context[0].value)==False:
#                 raise ValidatorException(f"{context[0].value}: invalid {self.name}")
#                 
# 
# class VariantValidator(SingletonValidator):
#     def match(self, value):
#         # match anything
#         return True
# 
#     @property
#     def name(self):
#         return "variant"
# 
#     def __repr__(self):
#         return "<variant>"
# 
# class BooleanValidator(SingletonValidator):
#     def match(self, value):
#         if isinstance(value, bool):
#             return True
#         return False
# 
#     @property
#     def name(self):
#         return "boolean value"
# 
#     def __repr__(self):
#         return "<bool>"
# 
# class IntValidator(SingletonValidator):
#     def match(self, value):
#         if isinstance(value, int):
#             return True
#         return False
# 
#     @property
#     def name(self):
#         return "integer value"
# 
#     def __repr__(self):
#         return "<int>"
# 
# class FloatValidator(SingletonValidator):
#     def match(self, value):
#         if isinstance(value, float):
#             return True
#         return False
# 
#     @property
#     def name(self):
#         return "floating point value"
# 
#     def __repr__(self):
#         return "<float>"
# 
# class StringValidator(SingletonValidator):
#     def match(self, value):
#         if isinstance(value, str):
#             return True
#         return False
# 
#     @property
#     def name(self):
#         return "string"
# 
#     def __repr__(self):
#         return "<string>"
# 
# class VersionRangeStringValidator(SingletonValidator):
#     def match(self, value):
#         try:
#             # provide at least one version to resolve 'latest'
#             version = VersionRange(versions=["0.0.0"])
#             version.select(value)
#             return True
#         except Exception as e:
#             return False
# 
#     @property
#     def name(self):
#         return "version range"
# 
#     def __repr__(self):
#         return "<version range>"
# 
# class VersionStringValidator(SingletonValidator):
#     def match(self, value):
#         try:
#             version = Version(value)
#             return True
#         except Exception as e:
#             return False
# 
#     @property
#     def name(self):
#         return "version"
# 
#     def __repr__(self):
#         return "<version>"
# 
# 
# class DictValidator(SingletonValidator):
#     pass
# 
# class Optional(SingletonValidator):
#     def __init__(self, schema):
#         super(Optional, self).__init__()
#         self._schema = schema
#         
#     def check(self, value):
#         if value is None:
#             return
# 
#         _recursive_check(value, self._schema)
# 
#     def __repr__(self):
#         return f"{self._schema}?"
# 
# 
# # class PackageString(Validator):
# #     def __init__(self):
# #         super(PackageString, self).__init__()
# #     
# #     def check(self, value):
# #         if not isinstance(value, str):
# #             raise ValidatorException(f"{value}: invalid package name")
# #         # TODO: validate name
# # 
# #     def __repr__(self):
# #         return "<package>"
# 

class Use(object):
    def __init__(self, callable_, error=None):
        if not callable(callable_):
            raise TypeError("Expected a callable, not %r" % callable_)
        self._callable = callable_
        self._error = error

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._callable)

    def validate(self, data):
        try:
            return self._callable.validate(data)
        except SchemaError as x:
            raise SchemaError([None] + x.autos, [self._error.format(data) if self._error else None] + x.errors)
        except BaseException as x:
            f = _callable_str(self._callable)
            raise SchemaError("%s(%r) raised %r" % (f, data, x), self._error.format(data) if self._error else None)

class Choice(object):
    def __init__(self, *args, error=None):
        super(Choice, self).__init__()
        
        self._values = list(args)
        self._error = error
 
    def validate(self, value): 
        if value not in self._values:
            if self._error is None:
                raise SchemaError(f"{value}: value not in range {self._values}")
            else:
                raise SchemaError(f"{value}: {self._error}")

    def __repr__(self):
        res = ""
        for value in self._values:
            if res=="":
                res = f"{value}"
            else:
                res += f" or {value}"
        return res
#     def __repr__(self):
#         return "<range>"
#     
# # class Array(Validator):
# #     def __init__(self, schema):
# #         super(Array, self).__init__()
# #         self._schema = schema
# #     
# #     def check(self, values):
# #         if not isinstance(values, list):
# #             raise ValidatorException(f"'{values}' is not a valid array list")
# #         for value in values:
# #             self._schema.check(value)
# # 
# #     def __repr__(self):
# #         return f"[{self._schema}]"
# # 
# # # an array that can be used as a dict when only one element
# # class CompactArray(Validator):
# #     def __init__(self, schema):
# #         super(CompactArray, self).__init__()
# #         self._schema = schema
# #     
# #     def check(self, values):
# #         if isinstance(values, list):
# #             for value in values:
# #                 self._schema.check(value)
# #         else:
# #             self._schema.check(values)
# # 
# #     def __repr__(self):
# #         return f"[{self._schema}]"
# # 
# # class Dict(Validator):
# #     def __init__(self, schema):
# #         super(Dict, self).__init__()
# #         self._schema = schema
# #     
# #     def check(self, values):
# #         if not isinstance(values, dict):
# #             raise ValidatorException(f"'{values}' is not a valid dictionnary")
# #         for value in values:
# #             if value not in self._schema:
# #                 raise SchemaException(f"{value}: unknown item")
# #             else:
# #                 self._schema[value].check(values[value])
# #     
# #     def __repr__(self):
# #         return f"{self._schema}"
# #     
# # class VariableDict(Validator):
# #     def __init__(self, schemakey, schemavalue):
# #         super(VariableDict, self).__init__()
# #         self._schemakey = schemakey
# #         self._schemavalue = schemavalue
# #     
# #     def check(self, values):
# #         if not isinstance(values, dict):
# #             raise ValidatorException(f"'{values}' is not a valid dictionnary")
# #         for value in values:
# #             self._schemakey.check(value)
# #             self._schemavalue.check(values[value])
# # 
# #     def __repr__(self):
# #         return "{"f"{self._schemakey}: {self._schemavalue}""}"
# 
# _validators = {
#     int: IntValidator,
#     float: FloatValidator,
#     bool: BooleanValidator,
#     str: StringValidator,
#     Version: VersionStringValidator,
#     VersionRange: VersionRangeStringValidator,
#     dict: DictValidator
# }
