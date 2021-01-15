import os
import sys

prefix = None

def set_prefix_path(path):
    global prefix
    prefix = path

# prefix a path with prefix dir
def prefix_path(path):
    if prefix is None:
        return path 
    
    # if path is absolute then remove the starting / to allow join to work properly 
    if path.startswith('/'):
        path = path[len('/'):]
    
    return os.path.join(prefix, path)