"""
Contains functions to handle directory- and filepath-related needs.
Currently only contains get_script_path(), but should be expanded
if related functions are needed.
"""

import sys
import os


def get_script_path():
    """Gets the absolute filepath of the script calling it"""

    return os.path.dirname(os.path.realpath(sys.argv[0]))
