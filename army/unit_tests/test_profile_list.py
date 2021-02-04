from army.api.log import log
from helper import raised, run
import os
import shutil
import tempfile
import unittest

prefix = 'test_profile'
log.setLevel('CRITICAL')


class TestProfileList(unittest.TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."
        self.tmpdir = tempfile.mkdtemp()
        shutil.copytree(self.path, self.tmpdir, dirs_exist_ok=True)
        os.chdir(self.tmpdir)
        os.environ["ARMY_PREFIX"] = self.tmpdir

    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."
        os.chdir(self.path)
        shutil.rmtree(self.tmpdir)
        del os.environ["ARMY_PREFIX"]

    @classmethod
    def setUpClass(cls):
        "Hook method for setting up class fixture before running tests in the class."
        # get current file path to find ressource files
        cls.cwd = os.getcwd()
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        os.chdir(cls.cwd)

    def test_list_no_param(self):
        res, stdout, stderr = run(["army", "profile", "list"])
        assert stdout==['name            | path            | description | ', 
                        'subst_c         | ~/.army/profile |             | ', 
                        'subst_a         | ~/.army/profile |             | ', 
                        'combined_value  | ~/.army/profile |             | ', 
                        'combined_value2 | ~/.army/profile |             | ', 
                        'value3          | ~/.army/profile |             | ', 
                        'dict_value2     | ~/.army/profile |             | ', 
                        'dict_value3     | ~/.army/profile |             | ', 
                        'value2          | ~/.army/profile |             | ', 
                        'subst_b         | ~/.army/profile |             | ', 
                        'list_value2     | ~/.army/profile |             | ', 
                        'list_value      | ~/.army/profile |             | ']
        assert res==0
        assert len(stderr)==0
        
