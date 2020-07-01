from gitlab.v4.objects import ProjectRelease
from gitlab.base import *  # noqa
from gitlab import cli
from gitlab.exceptions import *  # noqa
from gitlab.mixins import *  # noqa
from gitlab import types
from gitlab import utils
import os

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

@add_method(ProjectRelease)
def add_link(self, name, url, type="other", **kwargs):
        id = self.get_id().replace("/", "%2F")
        path = "%s/%s/assets/links" % (self.manager.path, id)
        data = {
            "name": name,
            "url": url,
            "type": type
            }
        try:
            server_data = self.manager.gitlab.http_post(
                path, post_data=data, **kwargs
            )
        except exc.GitlabHttpError as e:
            raise exc.GitlabCreateError(e.response_code, e.error_message) from e
