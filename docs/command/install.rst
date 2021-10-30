army install
============

Name
----

install - install packages inside project or user space

Synopsis
--------

`army install [-v] [-h] [-e] [-g] [-r] PACKAGE ...`


Description
-----------

Install packages inside project or user space.

| Packages are referenced in the form of `[REPOSITORY@]NAME[@VERSION]`. Only `NAME` is mandatory.
| If `REPOSITORY` is not specified and `NAME` matches from several repositories the first matching package will be taken.
| If `VERSION` is not specified then the greater version will be taken amongst all versions.

Arguments
---------

List of package to install.

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

	`-e` or `--edit`
		| This option is only relevant on local repositories and is available mostly as a developper feature. If used on a non candidate package it is ignored.
		| When in edit mode files from installed package are linked to source file instead of beeing copied on destination path. This allows developper to edit installed files directly. 
		| There is however some limitations:
		| - If a file is added or removed the installed package will not reflect the changes untill reinstall.
		| - The package file `army.toml` is not linked and will not reflect any change untill reinstall.
		| - This option only applies to the package beeing installed, not to its dependencies.

	`-g` or `--global`
		| By default packages are installed in the current path inside the `dist` folder.
		| Whis this option you can make packages available user wide by installing it inside the `~/.army/dist` folder.

	`-r` or `--reinstall`
		Force package to be reinstalled.
