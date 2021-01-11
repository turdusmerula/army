import os
import sys

prefix = None

# prefix a path with prefix dir
def prefix_path(path):
    if prefix is None:
        return path 
    
    # if path is absolute then remove the starting / to allow join to work properly 
    if path.startswith(os.path.pathsep):
        path = path[len(os.path.pathsep):]
    
    return os.path.join(prefix, path)