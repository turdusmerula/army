#!/usr/bin/env python3
from army import main
from curses import wrapper

if __name__ == "__main__":
    if __debug__:
        main()
    else:
        # wrapper to handle nicely curses in case of unhandled exception
        wrapper(main)
