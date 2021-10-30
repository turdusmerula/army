from army.api.console import ItemList
from army.api.log import log
import os
import unittest
from helper import raised, run, redirect_stdout, redirect_stderr
import io
from datetime import date

log.setLevel('DEBUG')


class TestConsole(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass

    
    def test_render(self):
        output = io.StringIO()
        
        tab = ItemList(columns=['name', 'rank', 'date'])
        tab.add_line({'name': 'value1', 'rank': 1, 'date': date.fromisoformat('2019-12-04')})
        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-30')})

        tab.render(file=output)

        print()
        print(output.getvalue())
        assert output.getvalue()=="""name   | rank | date       | 
value1 | 1    | 2019-12-04 | 
value2 | 1    | 2021-10-30 | 
"""

    def test_sort(self):
        output = io.StringIO()
        
        tab = ItemList(columns=['name', 'rank', 'date'])

        tab.add_line({'name': 'value3', 'rank': 5, 'date': date.fromisoformat('2018-01-04')})
        tab.add_line({'name': 'value3', 'rank': 1, 'date': date.fromisoformat('2018-01-04')})
        tab.add_line({'name': 'value3', 'rank': 5, 'date': date.fromisoformat('2018-01-01')})
        tab.add_line({'name': 'value3', 'rank': 1, 'date': date.fromisoformat('2018-01-04')})
        tab.add_line({'name': 'value3', 'rank': 5, 'date': date.fromisoformat('2018-01-02')})

        tab.add_line({'name': 'value1', 'rank': 5, 'date': date.fromisoformat('2019-12-04')})
        tab.add_line({'name': 'value1', 'rank': 4, 'date': date.fromisoformat('2019-12-04')})
        tab.add_line({'name': 'value1', 'rank': 3, 'date': date.fromisoformat('2019-12-04')})
        tab.add_line({'name': 'value1', 'rank': 2, 'date': date.fromisoformat('2019-12-04')})
        tab.add_line({'name': 'value1', 'rank': 1, 'date': date.fromisoformat('2019-12-04')})

        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-15')})
        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-12')})
        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-01')})
        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-22')})
        tab.add_line({'name': 'value2', 'rank': 1, 'date': date.fromisoformat('2021-10-30')})

        tab.sort('name', 'rank', 'date')
        tab.render(file=output)

        print()
        print(output.getvalue())
        assert output.getvalue()=="""name   | rank | date       | 
value1 | 1    | 2019-12-04 | 
value1 | 2    | 2019-12-04 | 
value1 | 3    | 2019-12-04 | 
value1 | 4    | 2019-12-04 | 
value1 | 5    | 2019-12-04 | 
value2 | 1    | 2021-10-01 | 
value2 | 1    | 2021-10-12 | 
value2 | 1    | 2021-10-15 | 
value2 | 1    | 2021-10-22 | 
value2 | 1    | 2021-10-30 | 
value3 | 1    | 2018-01-04 | 
value3 | 1    | 2018-01-04 | 
value3 | 5    | 2018-01-01 | 
value3 | 5    | 2018-01-02 | 
value3 | 5    | 2018-01-04 | 
"""


