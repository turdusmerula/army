from army.api.log import log
from army.api.version import Version
from helper import raised, run
import os
import unittest

prefix = 'test_plugin'
log.setLevel('CRITICAL')

# TODO: implement incompatible profiles
# plugin1 and plugin2 can not be loaded at the same time, it implies:
# implement in argparse an error when two commands with the same name are loaded in two groups at the same time
# load the profiles on set and refuse if there is an error
class TestDependencyRepos(unittest.TestCase):
    
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

    def test_plugin1(self):
        res, stdout = run(["army", "profile", "set", "plugin1"], merge=True)
        assert res==0

        res, stdout = run(["army", "command1"], merge=True)
        assert res==0
        assert stdout==["plugin1_command1"]

    def test_plugin2(self):
        res, stdout = run(["army", "profile", "set", "plugin2"], merge=True)
        assert res==0

        res, stdout = run(["army", "command1"], merge=True)
        assert res==0
        assert stdout==["plugin2_command1"]
