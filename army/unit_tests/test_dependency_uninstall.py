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
        self.tmpdir = tempfile.mkdtemp()
        shutil.copytree(self.path, self.tmpdir, dirs_exist_ok=True)
        os.chdir(self.tmpdir)
        os.environ["ARMY_PREFIX"] = self.tmpdir
        
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install"])
        
    def tearDown(self):
        os.chdir(self.path)
        shutil.rmtree(self.tmpdir)

    @classmethod
    def setUpClass(cls):
        # get current file path to find ressource files
        cls.cwd = os.getcwd()
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.cwd)
        del os.environ["ARMY_PREFIX"]

    def test_uninstall_no_param(self):
        res, stdout, stderr = run(["army", "uinstall"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==["nothing to uninstall"]

    def test_uinstall_project1_version_mismatch(self):
        os.chdir('project1')
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "version mismatch: lib1-1.0.1@lib1@1.0.1 conflicts with package lib1-1.0.0@lib1@1.0.0' from lib2-1.0.0@lib2@1.0.0",
            "install failed"
        ]

