from github import Repository


# utility tool to add member methods to a class
from functools import wraps
def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(self, *args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator

@add_method(Repository.Repository)
def delete_tag(self, name):
    """
    :calls: `DELETE /repos/:owner/:repo/git/refs/tags/:ref <https://developer.github.com/v3/git/refs/#delete-a-reference>`_
    :rtype: None
    """
    headers, data = self._requester.requestJsonAndCheck("DELETE", f"{self.url}/git/refs/tags/{name}")
