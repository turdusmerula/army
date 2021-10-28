from army.api.command import parser, group, command, option, argument
from army.api.log import log
from army.api.plugin import plugins
from army.version import version as army_version

@parser
@command(name='version', help='Show version')
@option(name='all', shortcut='a', default=False, help='List all loaded plugins versions', flag=True)
def version(ctx, all, **kwargs):
    log.info(f"version")
    
    print(f"army, version {army_version}")
    print("Copyright (C) 2016 Free Software Foundation, Inc.")
    print("License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>")
    print("")
    print("This is free software; you are free to change and redistribute it.")
    print("There is NO WARRANTY, to the extent permitted by law.")

    if all==True:
        if len(plugins)==0:
            print("No plugin loaded.")
        else:
            print("\nLoaded plugins:")
        for plugin in plugins:
            print("-", plugins[plugin])