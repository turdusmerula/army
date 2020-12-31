from army.api.log import log
import army.api.project
from army.api.dict_file import load_dict_file, DictFileException
import os
import unittest
from helper import raised, run
import army
import tempfile
import shutil

prefix = 'test_file_dict_data'
log.setLevel('DEBUG')


class TestLoadDictFile(unittest.TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."
        pass
        
    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

    @classmethod
    def setUpClass(cls):
        "Hook method for setting up class fixture before running tests in the class."
        # get current file path to find ressource files
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        pass


    def test_load_json(self):
        res = load_dict_file(os.path.join(self.path, "json"), "config")
        assert res['item']=="value"

    def test_load_json_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "json_error"), "config")==DictFileException

    def test_load_json_not_found(self):
        res = load_dict_file(os.path.join(self.path, "json"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "json_error"), "none", exist_ok=False)==DictFileException
        

    def test_load_yaml(self):
        res = load_dict_file(os.path.join(self.path, "yaml"), "config")
        assert res['item']=="value"

    def test_load_yaml_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "yaml_error"), "config")==DictFileException

    def test_load_yaml_not_found(self):
        res = load_dict_file(os.path.join(self.path, "yaml"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "yaml_error"), "none", exist_ok=False)==DictFileException


    def test_load_toml(self):
        res = load_dict_file(os.path.join(self.path, "toml"), "config")
        assert res['item']=="value"

    def test_load_toml_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "toml_error"), "config")==DictFileException

    def test_load_toml_not_found(self):
        res = load_dict_file(os.path.join(self.path, "toml"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "toml_error"), "none", exist_ok=False)==DictFileException


    def test_load_python(self):
        res = load_dict_file(os.path.join(self.path, "python"), "config")
        assert res['item']=="value"

    def test_load_python_error(self):
        assert raised(load_dict_file, os.path.join(self.path, "python_error"), "config")==DictFileException

    def test_load_python_not_found(self):
        res = load_dict_file(os.path.join(self.path, "python"), "none", exist_ok=True)
        assert res is None
        assert raised(load_dict_file, os.path.join(self.path, "python_error"), "none", exist_ok=False)==DictFileException

