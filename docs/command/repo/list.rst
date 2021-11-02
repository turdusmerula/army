army repo list
==============

Name
----

repo list - list configured repositories

Synopsis
--------

`army repo list [-v] [-h]`


Description
-----------

List configured repositories.
Repositories are listed in the exact order used to search packages.

Options
-------

    `-h` or `--help`
        Show help and exits.
        
    `-v`, `-vv`, `-vvv`, `-vvvv`
        | Verbosity mode. By default console only reports fatal errors, you can increase the verbosity with this option.
        | `-v`: Error level, show all errors that may have occured. Unless fatal errors a simple error can alter the behavior of Army without stopping it. 
        | `-vv`: Warning level, show all warnings.
        | `-vvv`: Info level, the info level gives some details on what is going on when Army is executing.
        | `-vvvv`: Debug level, the debug level gives a lot of details that may help resolve Army bugs or understand why it is not working properly (very verbose).
