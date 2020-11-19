import army.api.config
from army.api.log import log
import os
import unittest
from helper import raised

prefix = 'test_config'
log.setLevel('CRITICAL')

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."

    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

    @classmethod
    def setUpClass(cls):
        "Hook method for setting up class fixture before running tests in the class."
        # get current file path to find ressource files
        path = os.path.dirname(__file__)
        print(os.getcwd())
        os.chdir(path)

    @classmethod
    def tearDownClass(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class."
         

    def test_check_loading(self):
        # check no error when loading
        assert raised(army.api.config.load_configuration, None, prefix)==False
    
    def test_load_config(self):
        config = army.api.config.load_configuration(None, prefix)

        # show loaded configuration
        
        parent = config
        etc_config = None
        while parent is not None:
#             print(type(parent), parent.__dict__, parent.value)
            if isinstance(parent, army.api.config.ArmyConfig) and parent.path==f"{prefix}/etc/army/army.toml":
                etc_config = parent
            parent = parent.parent

        assert etc_config is not None
        
        assert len(config.repo)==6
         
        # check attributes
        assert config.verbose=="debug"
        assert etc_config.verbose=="critical"
        
        assert raised(lambda: config.toto)==AttributeError

if __name__ == '__main__':
    unittest.main(verbosity=2)
