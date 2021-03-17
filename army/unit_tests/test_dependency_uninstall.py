import army
from army.api.log import log
from army.api.package import load_installed_package
import army.api.project
from army.api.version import Version
from helper import raised, run
import os
import unittest
import tempfile
import shutil

prefix = 'test_local_repository'
log.setLevel('CRITICAL')


class TestDependencyUninstall(unittest.TestCase):
    
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
        del os.environ["ARMY_PREFIX"]

    def test_uninstall_no_param(self):
        res, stdout, stderr = run(["army", "uinstall"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==["nothing to install"]

    def test_uinstall_project1_version_mismatch(self):
        os.chdir('project1')
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "version mismatch: lib1-1.0.1@lib1@1.0.1 conflicts with package lib1-1.0.0@lib1@1.0.0' from lib2-1.0.0@lib2@1.0.0",
            "install failed"
        ]

