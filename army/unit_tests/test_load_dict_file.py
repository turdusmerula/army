from army.api.dict_file import load_dict_file, DictFileException, Dict
from army.api.log import log
import unittest
from helper import raised, run
import os

prefix = 'test_file_dict_data'
log.setLevel('DEBUG')


def TestDict():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLoadDictFile))
    test_suite.addTest(unittest.makeSuite(TestDictObject))
    return test_suite


class TestLoadDictFile(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        # get current file path to find ressource files
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        pass


#     def test_load_json(self):
#         res = load_dict_file(os.path.join(self.path, "json"), "config")
#         assert res['item']=="value"
# 
#     def test_load_json_error(self):
#         assert raised(load_dict_file, os.path.join(self.path, "json_error"), "config")==DictFileException
# 
#     def test_load_json_not_found(self):
#         res = load_dict_file(os.path.join(self.path, "json"), "none", exist_ok=True)
#         assert res is None
#         assert raised(load_dict_file, os.path.join(self.path, "json_error"), "none", exist_ok=False)==DictFileException
        

    def test_load_yaml(self):
        res = load_dict_file(os.path.join(self.path, "yaml"), "config")
        assert res['item']=="value"

    def test_load_yaml_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "yaml_error"), "config")[0]==DictFileException

    def test_load_yaml_not_found(self):
        res = load_dict_file(os.path.join(self.path, "yaml"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "yaml_error"), "none", exist_ok=False)[0]==DictFileException


#     def test_load_toml(self):
#         res = load_dict_file(os.path.join(self.path, "toml"), "config")
#         assert res['item']=="value"
# 
#     def test_load_toml_error(self):
#         assert raised(load_dict_file, os.path.join(self.path, "toml_error"), "config")==DictFileException
# 
#     def test_load_toml_not_found(self):
#         res = load_dict_file(os.path.join(self.path, "toml"), "none", exist_ok=True)
#         assert res is None
#         assert raised(load_dict_file, os.path.join(self.path, "toml_error"), "none", exist_ok=False)==DictFileException


    def test_load_python(self):
        res = load_dict_file(os.path.join(self.path, "python"), "config")
        assert res['item']=="value"

    def test_load_python_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "python_error"), "config")[0]==DictFileException

    def test_load_python_not_found(self):
        res = load_dict_file(os.path.join(self.path, "python"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "python_error"), "none", exist_ok=False)[0]==DictFileException


class TestDictObject(unittest.TestCase):
    
    def setUp(self):
        self.dict1 = Dict(data={
            "a": "1",
            "e": "0",
            "f": "0",
            "g": "{{f}}",
            "array": [1, 2, 3, 4]
        })
        
        self.dict2 = Dict(data={
            "b": "{{a}}",
            "c": "{{b}}",
            "d": "{{nonexists}}",
            "e": "{{e}} 1",
            
            "g": "{{g}}",
            "h": "{{g}} 1",
            
            "array": [1, 2, 3],
            "dict": {
                "c": 10
            },

            "recursive1": "{{recursive1}}",
            "recursive2": "{{/recursive2}}",
            
            "recursive3_0": "{{/recursive3_3}}",
            "recursive3_1": "{{/recursive3_0}}",
            "recursive3_2": "{{/recursive3_1}}",
            "recursive3_3": "{{recursive3_2}}",
            
        }, parent=self.dict1)

        self.dict3 = Dict(data={

        }, parent=self.dict2)
        
    def test_get_ok(self):
        assert self.dict1.get("/a")=="1"
        assert self.dict2.get("/a")=="1"
        assert self.dict2.get("a")=="1"

    def test_get_default(self):
        assert self.dict1.get("/default", default="0")=="0"

    def test_get_keyerror(self):
        assert raised(self.dict1.get, "/nonexists")[0]==KeyError

    def test_get_raw(self):
        assert self.dict2.get("b", raw=True)=="{{a}}"
        assert self.dict2.get("b", raw=False)=="1"

    def test_get_recursive1(self):
        assert self.dict2.get("recursive1")==""

    def test_get_recursive2(self):
        assert self.dict2.get("recursive2")==""

    def test_get_recursive3(self):
        assert self.dict2.get("recursive3_0")==""
        assert self.dict2.get("recursive3_1")==""
        assert self.dict2.get("recursive3_2")==""
        assert self.dict2.get("recursive3_3")==""

    def test_e(self):
        assert self.dict2.get("e")=="0 1"
        assert self.dict2.get("e")=="0 1"
        
    def test_c(self):
        print("---", self.dict2.get("c"))
        assert self.dict2.get("c")=="1"
        assert self.dict2.get("c")=="1"

    def test_h(self):
        assert raised(self.dict1.get, "h")[0]==KeyError
        assert self.dict2.get("h")=="0 1"
        assert self.dict2.get("/h")=="0 1"
        assert self.dict3.get("h")=="0 1"
        assert self.dict3.get("/h")=="0 1"

    def test_subscript(self):
        assert self.dict1["a"]=="1"
        assert self.dict2["/h"]=="0 1"
    

    def test_cut_subst(self):
        res = self.dict2._cut_subst("value {{test}} text {{newtest}} end")
        assert res==[[0, 'value '], [1, 'test'], [0, ' text '], [1, 'newtest'], [0, ' end']]

#     def test_is_recursive_path(self):
#         assert self.dict2._is_recursive_path("e")==True
#         assert self.dict2._is_recursive_path("/e")==True
        
#     def test_resolve_substs(self):
#         assert self.dict2._resolve_substs("/a", stack=[])=="1"
#         assert self.dict2._resolve_substs("a", stack=[])=="1"
#         assert self.dict2._resolve_substs("/b", stack=[])=="1"
#         assert self.dict2._resolve_substs("b", stack=[])=="1"
#         assert self.dict2._resolve_substs("/c", stack=[])=="1"
#         assert self.dict2._resolve_substs("c", stack=[])=="1"
