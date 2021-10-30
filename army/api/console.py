import sys

class ConsoleException(Exception):
    def __init__(self, message):
        self.message = message

class ItemList():
    def __init__(self, columns=[]):
        self._columns = columns
        self._lines = []
        self._current = None
        
    def add_line(self, values={}):
        self._lines.append({})
        self._current = self._lines[-1]
        for column in self._columns:
            self._current[column] = ""
        
        for value in values:
            self._current[value] = values[value]

    def sort(self, *args):
        for arg in args:
            if arg not in self._columns:
                raise ConsoleException(f"{arg}: undefined column")

        def sort_key(item):
            res = ()
            for arg in args:
                res += (item[arg],)
            return res
        
        res = sorted(self._lines, key=sort_key )
        self._lines = res
        
    def render(self, file=sys.stdout):
        sizes = {}
        for column in self._columns:
            sizes[column] = len(column)
            for line in self._lines:
                if len(str(line[column]))>sizes[column]:
                    sizes[column] = len(str(line[column]))

        for column in self._columns:
            print(f"{column.ljust(sizes[column])} | ", end='', file=file)
        print("", file=file)
        
        for line in self._lines:
            for column in self._columns:
                print(f"{str(line[column]).ljust(sizes[column])} | ", end='', file=file)
            print("", file=file)
