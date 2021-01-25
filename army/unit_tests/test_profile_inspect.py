from army.api.log import log
from helper import raised, run
import os
import shutil
import tempfile
import unittest

prefix = 'test_profile'
# log.setLevel('CRITICAL')
log.setLevel('DEBUG')


class TestProfileInspect(unittest.TestCase):
    
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

#     def test_inspect_current_profile(self):
#         res, stdout, stderr = run(["army", "profile", "inspect"])
#         assert res==0
#         assert len(stdout)==4
#         assert len(stderr)==0
#         
#     def test_inspect_profile_path(self):
#         res, stdout, stderr = run(["army", "profile", "inspect"])
#         assert res==0
#         assert len(stdout)==4
#         assert len(stderr)==0

    def test_inspect_profile_a(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "a"])
        assert res==0
        assert len(stdout)==4
        assert len(stderr)==0

    def test_inspect_profile_a_b(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "a", "b"])
        assert res==0
        assert len(stdout)==4
        assert len(stderr)==0

    def test_inspect_profile_a_b_c(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "a", "b", "c"])
        assert res==0
        assert len(stdout)==4
        assert len(stderr)==0
