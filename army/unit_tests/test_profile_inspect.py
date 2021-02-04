from army.api.log import log
from helper import raised, run
import os
import shutil
import tempfile
import unittest

prefix = 'test_profile'
log.setLevel('CRITICAL')
# log.setLevel('DEBUG')


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

    def test_inspect_profile_value2(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "value2"])
        assert res==0
        assert stdout==[
            "value: 2",
            ""
            ]
        assert len(stderr)==0

    def test_inspect_profile_value2_value3(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "value2", "value3"])
        assert res==0
        assert stdout==[
            "value: 3",
            ""
            ]
        assert len(stderr)==0

    def test_inspect_profile_dict_value2(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "dict_value2"])
        assert res==0
        assert stdout==[
            "dict_value:",
            "  value: 2",
            ""
            ]
        assert len(stderr)==0

    def test_inspect_profile_dict_value2_dict_value3(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "dict_value2", "dict_value3"])
        assert res==0
        assert stdout==[
            "dict_value:",
            "  value: 3",
            ""
            ]
        assert len(stderr)==0

    def test_inspect_profile_list_value(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "list_value"])
        assert res==0
        assert stdout==['list_value:', '- 1', '- 2', '- 3', '']
        assert len(stderr)==0

    def test_inspect_profile_list_value_list_value2(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "list_value", "list_value2"])
        assert res==0
        assert stdout==['list_value:', '- 1', '- 2', '- 3', '- 4', '- 5', '- 6', '']
        assert len(stderr)==0

    def test_inspect_profile_combined_value(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "combined_value"])
        assert res==0
        assert stdout==['combined_value:', '- item1: 1', '- item2: 2', '- item3:', '  - a', '  - b', '  - c', '']
        assert len(stderr)==0

    def test_inspect_profile_combined_value_combined_value2(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "combined_value", "combined_value2"])
        assert res==0
        assert stdout==['combined_value:', '- item1: 1', '- item2: 2', '- item3:', '  - a', '  - b', '  - c', '- item1: 2', '- item2: 3', '- item3:', '  - d', '  - e', '  - f', '- item4: 4', '']
        assert len(stderr)==0

    def test_inspect_profile_subst_a(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "subst_a"])
        assert res==0
        assert stdout==['a:', '- value1', '- value2', '']
        assert len(stderr)==0

    def test_inspect_profile_subst_b(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "subst_b"])
        assert res==0
        assert stdout==['b:', "  item: ''", '']
        assert len(stderr)==0
        
    def test_inspect_profile_subst_a_subst_b(self):
        res, stdout, stderr = run(["army", "profile", "inspect", "subst_a", "subst_b"])
        assert res==0
        assert stdout==['a:', '- value1', '- value2', 'b:', '  item: value1 value2', '']
        assert len(stderr)==0


#     def test_inspect_profile_a(self):
#         res, stdout, stderr = run(["army", "profile", "inspect", "a"])
#         assert res==0
#         assert len(stdout)==4
#         assert len(stderr)==0
# 
#     def test_inspect_profile_a_b(self):
#         res, stdout, stderr = run(["army", "profile", "inspect", "a", "b"])
#         assert res==0
#         assert len(stdout)==4
#         assert len(stderr)==0
# 
#     def test_inspect_profile_a_b_c(self):
#         res, stdout, stderr = run(["army", "profile", "inspect", "a", "b", "c"])
#         assert res==0
#         assert len(stdout)==4
#         assert len(stderr)==0
