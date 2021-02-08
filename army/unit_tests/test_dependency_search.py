from army.api.log import log
import army.api.project
from army.api.version import Version
import os
import unittest
from helper import raised, run
import army

prefix = 'test_local_repository_hierarchy'
log.setLevel('CRITICAL')


class TestDependencySearch(unittest.TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."

    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."
        os.chdir(self.path)

    @classmethod
    def setUpClass(cls):
        "Hook method for setting up class fixture before running tests in the class."
        # get current file path to find ressource files
        cls.cwd = os.getcwd()
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        os.chdir(cls.path)
        os.environ["ARMY_PREFIX"] = cls.path
        
    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        os.chdir(cls.cwd)
        del os.environ["ARMY_PREFIX"]

    def test_search_no_param(self):
        res, stdout, stderr = run(["army", "search"])
        assert res!=0
        assert len(stdout)==0
        assert len(stderr)>0
        
    def test_search_package(self):
        res, stdout, stderr = run(["army", "search", "project"])
        print(stdout)
        assert res==0
        assert len(stdout)==4
        assert len(stderr)==0

