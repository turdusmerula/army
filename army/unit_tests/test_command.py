from army.api.command import ArmyParser, get_army_parser, parser, group, command, option
from army.api.argparse import ArgparseException
from army.api.log import log
import os
import unittest
from helper import raised, run, redirect_stdout, redirect_stderr
import io
import sys


prefix = 'test_file_dict_data'
log.setLevel('DEBUG')



class TestCommand(unittest.TestCase):
    
    def setUp(self):
        self.parser = ArmyParser(command="army")
        
        self.build_group_chain = self.parser.add_group(chain=True)
        self.command1 = self.build_group_chain.add_command(name="command1", help="test command 1")
        self.build_group_chain.add_command(name="command2", help="test command 2")
        self.build_group_chain.add_command(name="command3", help="test command 3")

    def test_parser_type(self):
        assert isinstance(self.parser, ArmyParser)
        
    def test_parser_help(self):
        argv = ["army", "--help"]

        output = io.StringIO()
        with redirect_stderr(output):
            with self.assertRaises(SystemExit):
                self.parser.parse(argv) 
            
        print()
        print(output.getvalue())
        assert output.getvalue()=="""Usage: army [OPTIONS] COMMAND [ARGS]

Options:
    -v            Activate verbose/debug    
    --help, -h    Show this message and exit

Dependency Management Commands:

Commands:
    command1    test command 1
    command2    test command 2
    command3    test command 3

"""

    def test_command1_help(self):
        argv = ["army", "command1", "--help"]

        output = io.StringIO()
        with redirect_stderr(output):
            with self.assertRaises(SystemExit):
                self.parser.parse(argv) 
            
        print()
        print(output.getvalue())
        assert output.getvalue()=="""Usage: army command1 [OPTIONS] [COMMAND] [ARGS]

Options:
    -v            Activate verbose/debug    
    --help, -h    Show this message and exit

Dependency Management Commands:

Commands:
    command1    test command 1
    command2    test command 2
    command3    test command 3

"""

    def test_check_parser(self):
        argv = ["army"]

        assert raised(self.parser.parse, argv)==[ArgparseException, "army: command missing"]

    def test_check_command1(self):
        argv = ["army", "command1"]

        a = None
        def command1_callback(ctx, *argv, **kwargs):
            nonlocal a
            a = 1
        self.command1.add_callback(command1_callback)
        
        self.parser.parse(argv)
        
        assert a==1

