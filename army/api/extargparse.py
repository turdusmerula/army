import sys
import argparse
from argparse import _, Action, _SubParsersAction
from army.api.log import log

# import sys
# import pprint
# # pretty print loaded modules
# pprint.pprint(sys.modules)

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


class _PseudoGroup(Action):
    def __init__(self, container, title, id):
        self.id = id
        sup = super(_PseudoGroup, self)
        sup.__init__(option_strings=[], dest=title)
        self.container = container
        self._choices_actions = []
        
    def add_parser(self, name, **kwargs):
        # add the parser to the main Action, but move the pseudo action
        # in the group's own list
        parser = self.container.add_parser(name, **kwargs)
        choice_action = self.container._choices_actions.pop()
        self._choices_actions.append(choice_action)
        return parser

    def _get_subactions(self):
        return self._choices_actions

    def add_parser_group(self, title, id):
        # the formatter can handle recursive subgroups
        grp = _PseudoGroup(self, title, id)
        self._choices_actions.append(grp)
        return grp

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            if name.isidentifier():
                arg_strings.append('%s=%r' % (name, value))
            else:
                star_args[name] = value
        if star_args:
            arg_strings.append('**%s' % repr(star_args))
        return 'aaaa%s(%s)' % (type_name, ', '.join(arg_strings))

# add method to class _SubParsersAction without inheriting it, pretty nasty but it works
@add_method(_SubParsersAction)
def add_parser_group(self, title, id=''):
    self.id = id
    grp = _PseudoGroup(self, title, id)
    self._choices_actions.append(Action(option_strings=[], dest=''))
    self._choices_actions.append(grp)
    return grp

@add_method(_SubParsersAction)
def __call__(self, parser, namespace, values, option_string=None):
    parser_name = values[0]
    arg_strings = values[1:]

    # set the parser name if requested
    if self.dest is not argparse.SUPPRESS:
        setattr(namespace, self.dest, parser_name)

    # select the parser
    try:
        parser = self._name_parser_map[parser_name]
    except KeyError:
        args = {'parser_name': parser_name,
                'choices': ', '.join(self._name_parser_map)}
        msg = _('unknown parser %(parser_name)r (choices: %(choices)s)') % args
        raise argparse.ArgumentError(self, msg)

    # CHANGES
    # parse all the remaining options into a new namespace
    # store any unrecognized options on the main namespace, so that the top
    # level parser can decide what to do with them
    newspace = argparse.Namespace()
    newspace, arg_strings = parser.parse_known_args(arg_strings, newspace)
    setattr(namespace, 'subspace', newspace) # is there a better 'dest'?

    if arg_strings:
        vars(namespace).setdefault(argparse._UNRECOGNIZED_ARGS_ATTR, [])
        getattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR).extend(arg_strings)

#argparse._SubParsersAction.__call__ = mycall

class ArgumentParser(argparse.ArgumentParser):    

    def error(self, message):
        self.print_help(sys.stderr)
        print('', file=sys.stderr)
        
#        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n\n') % args)
#        raise sys.exc_info()[1]

    def add_default_args(self):
        self.add_argument('-v', '--verbose', action='store_true', help='activate verbose mode', default=False)
        self.add_argument('-vv', action='store_true', help=argparse.SUPPRESS, default=False)
        self.add_argument('-vvv', action='store_true', help=argparse.SUPPRESS, default=False)
        
    def parse_default_args(self):
        namespace, args = self.parse_known_args()
        if hasattr(namespace, 'verbose') and namespace.verbose==True:
            print("Logging level warning")
            log.setLevel('WARNING')
        if hasattr(namespace, 'vv') and namespace.vv==True:
            print("Logging level info")
            log.setLevel('INFO')
        if hasattr(namespace, 'vvv') and namespace.vvv==True:
            print("Logging level debug")
            log.setLevel('DEBUG')
        return args
#     def get_subparser(self):