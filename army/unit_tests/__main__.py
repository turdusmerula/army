#!/bin/python3
import os
import sys
sys.path.append(os.path.dirname(__file__))
import unittest 

from test_army_install import *
# from test_load_dict_file import *
# from test_argparse import *
# from test_command import *
# from test_version import *
# from test_version_range import *
# from test_project import *
# from test_schema import *
#
# from test_dependency_repos import *
# from test_dependency_search import *
# from test_dependency_install import *
# from test_dependency_uninstall import *
#
# from test_profile_list import *
# from test_profile_inspect import *

# TODO
# from test_profile_current import *
# from test_profile_search import *
# from test_profile_set import *

if __name__ == '__main__':
    unittest.main(verbosity=2)
