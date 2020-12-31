from army.api.log import log
from army.api.argparse import create_parser, CommandException
import os
import unittest
from helper import raised, run
import io

prefix = 'test_file_dict_data'
log.setLevel('DEBUG')

# TODO: check two arguments/option does not use the same name

def TestArgparse():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestArgparseOption))
    test_suite.addTest(unittest.makeSuite(TestArgparseArgument))
    test_suite.addTest(unittest.makeSuite(TestArgparseArgumentFixedArray))
    test_suite.addTest(unittest.makeSuite(TestArgparseCommand))
    return test_suite

class TestArgparseOption(unittest.TestCase):
    
    def setUp(self):
        self.parser = create_parser(command="army")
        self.parser.add_command(name="test2", help="test2 command")
        self.parser.add_command(name="test1", help="test1 command")
        
        # option shortcut array
        self.verbose_option = self.parser.add_option(shortcut="v", help="Activate verbose/debug", flag=True, count=4)
        # 3 short flags
        self.a_option = self.parser.add_option(shortcut="a", help="A", flag=True, default=True)
        self.b_option = self.parser.add_option(shortcut="b", help="B", flag=True, default=False)
        self.c_option = self.parser.add_option(shortcut="c", help="C", flag=True)
        # option text value with shortcut
        self.target_option = self.parser.add_option(name="target", shortcut="t", value="TEXT", help="Select target", default=None)
        # option text value without shortcut
        self.name_option = self.parser.add_option(name="name", value="TEXT", help="Show name")
        # option flag with shortcut
        self.parser.add_option(name="help", shortcut="h", help="Show this message and exit", flag=True)
        # option flag without shortcut
        self.parser.add_option(name="version", help="show army version", flag=True)
        # option name array
        self.parser.add_option(name="file", help="file list", value="FILE", count=4)
        # option name not usable as python variable name
        self.parser.add_option(name="top-dir", help="top directory name", value="NAME", default=".")
                
        # add subcommands
        self.build_group = self.parser.add_group(name="build", help="Build Commands")
        # add a hidden group to allow chaining a group of commands
        self.build_group_chain = self.build_group.add_group(chain=True)
        self.build_group_chain.add_command(name="clean", help="clean project")
        self.build_group_chain.add_command(name="compile", help="compile the whole project")
        self.build_group.add_command(name="test", help="launch tests")
        
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        # get current file path to find ressource files
        cls.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prefix)
        
    @classmethod
    def tearDownClass(cls):
        pass


    def test_empty_parser(self):
        parser = create_parser()
        argv = ["army"]
        
        #TODO
        parser.parse(argv)
    
    def test_show_help(self):
        output = io.StringIO()
        self.parser.show_help(file=output)
        print()
        print(output.getvalue())
        assert output.getvalue()=="""Usage: army [OPTIONS] COMMAND [ARGS]

Options:
    -v                   Activate verbose/debug    
    -a                   A (True)                  
    -b                   B (False)                 
    -c                   C                         
    --target, -t TEXT    Select target (None)      
    --name       TEXT    Show name                 
    --help, -h           Show this message and exit
    --version            show army version         
    --file       FILE    file list                 
    --top-dir    NAME    top directory name (.)    

Build Commands:
    clean      clean project            
    compile    compile the whole project
    test       launch tests             

Commands:
    test1    test1 command
    test2    test2 command
"""

    def test_parser_callback(self):
        argv = ["army", "--target=aaa", "--name=test"]
        
        _a = None
        _b = None
        _target = None
        _name = None
        _top_dir = "."
        def parser_callback(ctx, a, b, target, *args, **kwargs):
            nonlocal _a, _b, _target, _name, _top_dir
            _a = a
            _b = b
            _target = target
            _name = kwargs.get("name", None)
            _top_dir = kwargs.get("top-dir", None)
            
            assert "version" not in kwargs
            
        self.parser.add_callback(parser_callback)
        self.parser.parse(argv)
        
        assert _a==True
        assert _b==False
        assert _target=="aaa"
        assert _name=="test"
        assert _top_dir=="."
        
    def test_parse_option_shortcut_unknow(self):
        argv = ["army", "-vu"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_option_shortcut_no_value(self):
        argv = ["army", "-t"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_option_shortcut_chain_flags(self):
        a = None
        b = None
        c = None
        argv = ["army", "-abc"]
        def a_callback(option, value):
            nonlocal a
            a = value
        def b_callback(option, value):
            nonlocal b
            b = value
        def c_callback(option, value):
            nonlocal c
            c = value
        
        self.a_option.add_callback(a_callback)
        self.b_option.add_callback(b_callback)
        self.c_option.add_callback(c_callback)
        
        self.parser.parse(argv)

        assert a==True
        assert b==True
        assert c==True

    def test_parse_option_shortcut_array_count_error(self):
        argv = ["army", "-vvvvv"]
        assert raised(self.parser.parse, argv)==CommandException
    
    def test_parse_option_shortcut_value(self):
        t = None
        argv = ["army", "-t", "value"]
        def t_callback(option, value):
            nonlocal t
            t = value
        
        self.target_option.add_callback(t_callback)
        
        self.parser.parse(argv)

        assert t=="value"


    def test_parse_option_name_unknow(self):
        argv = ["army", "--test"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_option_name_no_value(self):
        argv = ["army", "--target"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_option_name_equal_value(self):
        name = None
        argv = ["army", "--name=test"]
        def name_callback(option, value):
            nonlocal name
            name = value
        
        self.name_option.add_callback(name_callback)
        
        self.parser.parse(argv)

        assert name=="test"

    def test_parse_option_name_value(self):
        name = None
        argv = ["army", "--name", "value"]
        def name_callback(option, value):
            nonlocal name
            name = value
        
        self.name_option.add_callback(name_callback)
        
        self.parser.parse(argv)

        assert name=="value"
    
    def test_parse_option_name_array_count_error(self):
        argv = ["army", "--file", "a", "--file", "b", "--file", "c", "--file", "d", "--file", "e"]
        assert raised(self.parser.parse, argv)==CommandException

    

class TestArgparseArgument(unittest.TestCase):
    
    def setUp(self):
        self.parser = create_parser(command="army")
        
        # 3 short flags
        self.a_option = self.parser.add_option(shortcut="a", help="A", flag=True)
        self.b_option = self.parser.add_option(shortcut="b", help="B", flag=True)
        self.c_option = self.parser.add_option(shortcut="c", help="C", flag=True)
        
        # add arguments
        self.parser.add_argument(name="value1")
        self.parser.add_argument(name="value2")
        
    def test_parse_argument_missing(self):
        argv = ["army", "1"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_argument_unknown(self):
        argv = ["army", "1", "2", "3"]
        assert raised(self.parser.parse, argv)==CommandException
    
    def test_parse_argument(self):
        argv = ["army", "1", "2"]
        
        v1 = None
        v2 = None
        def parser_callback(ctx, value1, value2, *args, **kwargs):
            nonlocal v1, v2
            v1 = value1
            v2 = value2
        
        self.parser.add_callback(parser_callback)
        
        self.parser.parse(argv)

        assert v1=="1"
        assert v2=="2"


class TestArgparseArgumentFixedArray(unittest.TestCase):
    
    def setUp(self):
        self.parser = create_parser(command="army")

        # add arguments
        self.parser.add_argument(name="value1")
        self.parser.add_argument(name="value2", count=3)
        
    def test_parse_argument_missing(self):
        argv = ["army", "1"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_argument_missing2(self):
        argv = ["army", "1", "2"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_parse_argument_unknown(self):
        argv = ["army", "1", "2", "3", "4", "5"]
        assert raised(self.parser.parse, argv)==CommandException
    
    def test_parse_argument(self):
        argv = ["army", "1", "2", "3", "4"]
        
        v1 = None
        v2 = None
        def parser_callback(ctx, value1, value2, *args, **kwargs):
            nonlocal v1, v2
            v1 = value1
            v2 = value2
        
        self.parser.add_callback(parser_callback)
        
        self.parser.parse(argv)

        assert v1=="1"
        assert v2==["2", "3", "4"]


class TestArgparseCommand(unittest.TestCase):
    
    def setUp(self):
        self.parser = create_parser(command="army")
        
        self.test1_command = self.parser.add_command(name="test1", help="test1 command")
        self.test1_command.add_option(name="help", shortcut="h", help="Show this message and exit", flag=True)
        
        self.test2_command = self.parser.add_command(name="test2", help="test2 command")
        self.test2_command.add_option(name="help", shortcut="h", help="Show this message and exit", flag=True)

    def test_call_command_test1(self):
        argv = ["army", "test1", "--help"]

        def parser_callback(ctx, *args, **kwargs):
            pass

        def test1_callback(ctx, help, *args, **kwargs):
            assert help==True

        self.parser.add_callback(parser_callback)
        self.test1_command.add_callback(test1_callback)
        
        self.parser.parse(argv)
    
    def test_call_command_unknown(self):
        argv = ["army", "test3"]
        assert raised(self.parser.parse, argv)==CommandException

    def test_call_command_invalid_parameter(self):
        argv = ["army", "test1", "param"]
        assert raised(self.parser.parse, argv)==CommandException
