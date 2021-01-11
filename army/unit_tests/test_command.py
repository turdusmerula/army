from army.api.log import log
from army.api.command import create_parser, ArmyParser
import os
import unittest
from helper import raised, run
import io

prefix = 'test_file_dict_data'
log.setLevel('DEBUG')



class TestCommand(unittest.TestCase):
    
    def setUp(self):
        self.parser = create_parser(command="army")
        
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        # get current file path to find ressource files
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        pass


    def test_parser_type(self):
        assert isinstance(self.parser, ArmyParser)