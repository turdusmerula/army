from army.api.log import log
import army.api.project
from army.api.version import Version
import os
import unittest
from helper import raised, run
import army
import tempfile
import shutil

prefix = 'test_local_repository_hierarchy'
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

    def test_install_no_param(self):
        res, stdout, stderr = run(["army", "install"])
        assert res!=0
        assert len(stdout)==0
        assert len(stderr)>0
        
#     def test_install_package(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1"])
#         assert res==0
#         assert len(stdout)==1
#         assert stdout[0]=="install package project1@1.2.0"
#         assert len(stderr)==0
#  
#     def test_install_package_exact_version(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1@1.0.0"])
#         assert res==0
#         assert len(stdout)==1
#         assert stdout[0]=="install package project1@1.0.0"
#         assert len(stderr)==0
#   
#     def test_install_package_semantic_version(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project2@~1.3.0"])
#         assert res==0
#         assert len(stdout)==2
#         assert stdout[1]=="install package project2@1.3.4"
#         assert len(stderr)==0
#   
#     def test_install_package_repository(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1-v1.0.0@project1"])
#         assert res==0
#         assert len(stdout)==1
#         assert stdout[0]=="install package project1@1.0.0"
#         assert len(stderr)==0
#   
#     def test_install_package_repository_version(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1-v1.0.0@project1@1.0.0"])
#         assert res==0
#         assert len(stdout)==1
#         assert stdout[0]=="install package project1@1.0.0"
#         assert len(stderr)==0
# 
#     def test_install_already_installed(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1"])
#         res, stdout, stderr = run(["army", "install", "project1"])
#         assert res==0
#         assert len(stdout)==0
#         assert len(stderr)==1
#         assert stderr[0]=="package project1@1.2.0 already installed"
#     
#     def test_install_package_not_found(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project10"])
#         assert res>0
#         assert len(stdout)==0
#         assert len(stderr)==1
#         assert stderr[0]=="project10: package not found"
#     
#     def test_install_incompatible_versions(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install", "project1@1.2.0"])
#         res, stdout, stderr = run(["army", "install", "project1@1.0.0"])
#         assert res>0
#         assert len(stdout)==0
#         assert len(stderr)==1
#         assert stderr[0]=="'project1@1.0.0' conflicts with installed package 'project1@1.2.0'"
#     
#     def test_install_project_dependencies(self):
#         os.chdir('project4')
#         res, stdout, stderr = run(["army", "install"])
#         assert res==0
#         assert len(stdout)==3
#         assert len(stderr)==0
# 
#     def test_install_project_dependencies_incompatible_version(self):
#         os.chdir('project5')
#         res, stdout, stderr = run(["army", "install"])
# #         print(res, stdout, stderr)
#         assert res>0
#         assert len(stdout)==0
#         assert len(stderr)==1
#         assert stderr[0]=="'project2@1.3.4' from 'project3' conflicts with package 'project2@1.3.2' from project"
