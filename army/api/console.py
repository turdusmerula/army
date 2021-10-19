import sys

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

    def sort(self, columns={}):
        pass
    
    def render(self, file=sys.stdout):
        sizes = {}
        for column in self._columns:
            sizes[column] = len(column)
            for line in self._lines:
                if len(line[column])>sizes[column]:
                    sizes[column] = len(line[column])

        for column in self._columns:
            print(f"{column.ljust(sizes[column])} | ", end='', file=file)
        print("", file=sys.stdout)
        
        for line in self._lines:
            for column in self._columns:
                print(f"{line[column].ljust(sizes[column])} | ", end='', file=file)
            print("", file=sys.stdout)
