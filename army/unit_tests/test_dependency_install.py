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


class TestDependencyInstall(unittest.TestCase):
    
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

    def test_install_no_param_no_project(self):
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==["nothing to install"]

    def test_install_project1_version_mismatch(self):
        os.chdir('project1')
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "version mismatch: lib1-1.0.1@lib1@1.0.1 conflicts with package lib1-1.0.0@lib1@1.0.0' from lib2-1.0.0@lib2@1.0.0",
            "install failed"
        ]

    def test_install_project2_no_dependency(self):
        os.chdir('project2')
        res, stdout, stderr = run(["army", "install"])
        assert res==0
        assert stdout==[
            "lib1-1.0.1@lib1@1.0.1 install",
            "install finished ok"
        ]
        assert len(stderr)==0
        
    def test_install_project2_already_installed(self):
        os.chdir('project2')
        res, stdout, stderr = run(["army", "install"])
        assert res==0
        assert stdout==[
            "lib1-1.0.1@lib1@1.0.1 install",
            "install finished ok"
        ]
        assert len(stderr)==0
        
        res, stdout, stderr = run(["army", "install"])
        assert res==0
        assert stdout==[
            "lib1-1.0.1@lib1@1.0.1 already installed, skip",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_project6_installed_package_nok(self):
        os.chdir('project6')
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "Error loading package lib1-1.0.1@lib1@1.0.1",
            "install failed"
        ]
        

    def test_install_package(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1"])
        assert res==0
        assert stdout==[
            "lib1-1.1.2@lib1@1.1.2 install",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_version(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1@1.0.0"])
        assert res==0
        assert stdout==[
            "lib1-1.0.0@lib1@1.0.0 install",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_repo(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1-1.0.0@lib1"])
        assert res==0
        assert stdout==[
            "lib1-1.0.0@lib1@1.0.0 install",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_repo_version(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1-1.0.0@lib1@1.0.0"])
        assert res==0
        assert stdout==[
            "lib1-1.0.0@lib1@1.0.0 install",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_semantic_version(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1"])
        assert res==0
        assert stdout==[
            "lib1-1.1.2@lib1@1.1.2 install",
            "install finished ok"
        ]
        assert len(stderr)==0

        res, stdout, stderr = run(["army", "install", "lib1"])
        assert res==0
        assert stdout==[
            "lib1-1.1.2@lib1@1.1.2 already installed, skip",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_already_installed(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1@~1.0.0"])
        assert res==0
        assert stdout==[
            "lib1-1.0.1@lib1@1.0.1 install",
            "install finished ok"
        ]
        assert len(stderr)==0

    def test_install_package_not_found(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib10"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "lib10: package not found"
        ]

    def test_install_package_version_not_found(self):
        os.chdir('project4')
        res, stdout, stderr = run(["army", "install", "lib1@1.4.0"])
        assert res!=0
        assert len(stdout)==0
        assert stderr==[
            "lib1: no version matching 1.4.0"
        ]
