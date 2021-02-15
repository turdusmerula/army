from army.api.log import log
from army.api.project import load_project
from army.api.version import Version
from helper import raised
import os
import unittest

prefix = 'test_project'
log.setLevel('CRITICAL')


class TestProject(unittest.TestCase):
    
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

    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
        os.chdir(cls.cwd)
        
#     def test_check_loading(self):
#         # check no error when loading
#         os.chdir('project_ok')
#         assert raised(army.api.project.load_project)==False
#     
#     def test_check_loading_failed(self):
#         # check no error when loading
#         os.chdir('project_failed')
#         assert raised(army.api.project.load_project)==army.api.project.ProjectException
# 
#     def test_load_project(self):
#         os.chdir('project_ok')
#         project = army.api.project.load_project()
# 
#         assert project.name=="project_ok"
#         assert project.description=="test project ok"
#         assert project.version==Version("1.0.0")
        

