import os
import sys

prefix = None

def set_prefix_path(path):
    global prefix
    prefix = path

# prefix a path with prefix dir
def prefix_path(path):
    return PrefixPath(path)

# @description A prefixale path, used to represent an absolute path with prefix
class PrefixPath(os.PathLike):
    def __init__(self, path):
        super(PrefixPath, self).__init__()
        if isinstance(path, PrefixPath):
            self._path = path.path
        else:
            self._path = path
        
    @property
    def path(self):
        return self._path
    
    @property
    def prefix_path(self):
        global prefix
        
        if prefix is None:
            return self.path 
        
        path = self.path
        # if path is absolute then remove the starting / to allow join to work properly 
        if path.startswith('/'):
            path = self.path[len('/'):]
        
        return os.path.join(prefix, path)

    def __fspath__(self):
        return self.prefix_path
