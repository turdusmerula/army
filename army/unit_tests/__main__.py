#!/bin/python3
import os
import sys
sys.path.append(os.path.dirname(__file__))
import unittest 

# import unit_tests
from test_config2 import *
from test_project import *
from test_dependency_repos import *
from test_dependency_search import *
from test_dependency_install import *
from test_load_dict_file import *
from test_argparse import *

if __name__ == '__main__':
    unittest.main(verbosity=2)
