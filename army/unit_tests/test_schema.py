from army.api.log import log
from army.api.package import PackageReference
from army.api.schema import validate, Optional, Choice, SchemaError, Use
from army.api.version import Version, VersionRange
import os
import unittest
from helper import raised, run, redirect_stdout, redirect_stderr
import io


class TestSchema(unittest.TestCase):
    
    def setUp(self):
        log.setLevel('DEBUG')
        self._schema = {}
        
    def tearDown(self):
        pass

    def test_validate(self):
        validate({}, {})

    def test_choice(self):
        schema = {'value': Choice("a", "b", "c")}
        
        validate({'value': "a"}, schema)
        assert raised(validate, {'value': 'd'}, schema)==[SchemaError, """Key 'value' error:
d: value not in range ['a', 'b', 'c']"""]

    def test_package_reference(self):
        schema = {'value': Use(PackageReference)}
        
        validate({'value': "package@1.0.0"}, schema)

    
#     def test_empty_parser(self):
#         schema = {}
#         data = {}
#         check(data, schema)
# 
#     def test_optional_key(self):
#         check(None, Optional(str))
#         check('1', Optional(str))
#         assert raised(check, 1, Optional(str))==[ValidatorException, "1: invalid string"]
# 
#         schema = {
#             Optional('value'): str
#         }
#          
#         data = {}
#         check(data, schema)
# # 
#     def test_str(self):
#         check('value', str)
#         assert raised(check, 1, str)==[ValidatorException, "1: invalid string"]
#  
#     def test_recursive(self):
#         schema = {
#             'key1': str,
#             'key2': str,
#             Optional('key3'): {
#                 'key4': str,
#                 'key5': {
#                     'key6': str
#                 }
#             }
#         }
#          
#         data = {
#             'key1': 'value1',
#             'key2': 'value2',
#             'key3': {
#                 'key4': 'value3',
#                 'key5': {
#                     'key6': 'value4'
#                 }
#             }
#         }
#  
#         check(data, schema)
#  
#         data = {
#             'key1': 'value1',
#             'key2': 'value2',
#         }
#  
#         check(data, schema)
# 
#         data = {
#             'key1': 'value1',
#             'key2': 'value2',
#             'key3': {
#                 'key4': 1,
#                 'key5': {
#                     'key6': 'value4'
#                 }
#             }
#         }
#         assert raised(check, data, schema)==[ValidatorException, "1: invalid string"]
# 
#         data = {
#             'key1': 'value1',
#             'key2': 'value2',
#             'key3': {
#                 'key4': 'value3',
#                 'key5': {
#                     'key6': 'value4',
#                     'key7': 'value7'
#                 }
#             }
#         }
#         assert raised(check, data, schema)==[ValidatorException, "key7: unknown item"]
# 
#     def test_multiple_match(self):
#         pass
# 
#     def test_version(self):
#         check("1.0.0", Version)
#     
#     def test_str_key(self):
#         schema = {
#             str: str
#         }
#         data = {
#             'key1': 'value1',
#             'key2': 'value2'
#         }
#         check(data, schema)
# 
#     def test_unhandled_type(self):
#         class Unhandled():
#             pass
#         
#         schema = {
#             'key1': Unhandled,
#         }
#          
#         data = {
#             'key1': 0
#         }
#  
#         assert raised(check, data, schema)==[ValidatorException, "<class 'test_schema.TestSchema.test_unhandled_type.<locals>.Unhandled'>: schema type not handled"]
# 
#     def test_missing_value(self):
#         schema = {
#             'key1': str,
#             'key2': str,
#         }
#          
#         data = {
#             'key1': 'value1',
#         }
#  
#         assert raised(check, data, schema)==[ValidatorException, "key23: value missing"]
        